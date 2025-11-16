#!/usr/bin/env python3
"""
Comprehensive Clinical Guidelines & Reviews Collection
Focus on diagnostic criteria, clinical presentations, and differential diagnosis

Usage:
    python collect_clinical_guidelines.py --disease all --max 50
    python collect_clinical_guidelines.py --disease sepsis --max 100
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(__file__))
from collect_pubmed_pmc import PubMedCollector, save_article_data

load_dotenv()

NCBI_API_KEY = os.getenv('NCBI_API_KEY', '')
NCBI_EMAIL = os.getenv('NCBI_EMAIL', '')
OUTPUT_DIR = Path('../../data/raw/clinical_guidelines')


# Comprehensive list of infectious diseases
INFECTIOUS_DISEASES = {
    'bacterial': [
        'sepsis', 'bacterial meningitis', 'tuberculosis', 'pneumonia',
        'urinary tract infection', 'cellulitis', 'endocarditis',
        'osteomyelitis', 'necrotizing fasciitis', 'septic arthritis',
        'bacterial gastroenteritis', 'Clostridium difficile infection',
        'streptococcal pharyngitis', 'pertussis', 'Lyme disease'
    ],
    'viral': [
        'HIV infection', 'viral hepatitis', 'influenza', 'COVID-19',
        'herpes simplex', 'varicella zoster', 'infectious mononucleosis',
        'viral meningitis', 'dengue fever', 'measles', 'mumps',
        'viral pneumonia', 'cytomegalovirus infection', 'rabies'
    ],
    'fungal': [
        'candidiasis', 'aspergillosis', 'cryptococcal meningitis',
        'histoplasmosis', 'coccidioidomycosis', 'mucormycosis',
        'pneumocystis pneumonia', 'fungal endocarditis'
    ],
    'parasitic': [
        'malaria', 'toxoplasmosis', 'amebiasis', 'giardiasis',
        'trichinosis', 'leishmaniasis', 'schistosomiasis',
        'cryptosporidiosis', 'babesiosis'
    ],
    'systemic': [
        'fever of unknown origin', 'neutropenic fever',
        'hospital acquired infection', 'surgical site infection',
        'catheter related infection', 'ventilator associated pneumonia'
    ]
}


def build_disease_specific_query(disease: str, open_access: bool = True) -> str:
    """
    Build optimized query for a specific disease focusing on clinical diagnostic content

    Args:
        disease: Disease name
        open_access: Filter to open access only

    Returns:
        Query string
    """

    # Core diagnostic terms
    diagnostic_terms = [
        'diagnosis',
        'diagnostic criteria',
        'clinical presentation',
        'differential diagnosis',
        'signs and symptoms',
        'diagnostic approach'
    ]

    # Publication types with clinical value
    pub_types = [
        'Review[PT]',
        'Practice Guideline[PT]',
        'Guideline[PT]',
        'Meta-Analysis[PT]',
        'Systematic Review[PT]'
    ]

    # Build query: (disease) AND (diagnostic terms) AND (publication types)
    disease_q = f'"{disease}"[MeSH Terms] OR "{disease}"[Title]'
    diagnostic_q = ' OR '.join([f'"{term}"[Title/Abstract]' for term in diagnostic_terms])
    pubtype_q = ' OR '.join(pub_types)

    query = f'({disease_q}) AND ({diagnostic_q}) AND ({pubtype_q})'

    if open_access:
        query += ' AND ffrft[filter]'

    # Recent articles (last 10 years)
    query += ' AND ("2014"[PDAT] : "2025"[PDAT])'

    return query


def get_disease_queries(category: str = 'all', max_per_disease: int = 50) -> List[Tuple[str, str, str]]:
    """
    Generate queries for diseases

    Args:
        category: 'all', 'bacterial', 'viral', 'fungal', 'parasitic', 'systemic', or specific disease
        max_per_disease: Max articles per disease

    Returns:
        List of (category, disease, query) tuples
    """

    queries = []

    if category == 'all':
        # All categories
        for cat, diseases in INFECTIOUS_DISEASES.items():
            for disease in diseases:
                query = build_disease_specific_query(disease, open_access=True)
                queries.append((cat, disease, query))

    elif category in INFECTIOUS_DISEASES:
        # Specific category
        for disease in INFECTIOUS_DISEASES[category]:
            query = build_disease_specific_query(disease, open_access=True)
            queries.append((category, disease, query))

    else:
        # Specific disease
        query = build_disease_specific_query(category, open_access=True)
        queries.append(('custom', category, query))

    return queries


def extract_clinical_information(article_metadata: Dict) -> Dict:
    """
    Extract clinical information from article metadata

    Args:
        article_metadata: Article metadata from PubMed

    Returns:
        Dictionary with extracted clinical markers
    """

    clinical_info = {
        'has_abstract': False,
        'publication_types': [],
        'mesh_terms': [],
        'is_review': False,
        'is_guideline': False,
        'is_meta_analysis': False,
        'clinical_relevance_score': 0
    }

    # Check publication types
    pubtypes = article_metadata.get('pubtype', [])
    clinical_info['publication_types'] = pubtypes

    clinical_info['is_review'] = 'Review' in pubtypes
    clinical_info['is_guideline'] = any(
        'Guideline' in pt for pt in pubtypes
    )
    clinical_info['is_meta_analysis'] = 'Meta-Analysis' in pubtypes

    # Calculate clinical relevance score
    score = 0
    if clinical_info['is_guideline']:
        score += 10
    if clinical_info['is_meta_analysis']:
        score += 8
    if clinical_info['is_review']:
        score += 5

    # Check for attributes indicating quality
    attributes = article_metadata.get('attributes', [])
    if 'Has Abstract' in attributes:
        clinical_info['has_abstract'] = True
        score += 2

    clinical_info['clinical_relevance_score'] = score

    return clinical_info


def collect_clinical_guidelines(collector: PubMedCollector,
                               output_dir: Path,
                               category: str = 'all',
                               max_per_disease: int = 50):
    """
    Collect clinical guidelines and reviews for infectious diseases

    Args:
        collector: PubMedCollector instance
        output_dir: Output directory
        category: Disease category or specific disease
        max_per_disease: Maximum articles per disease
    """

    print(f"\n{'='*70}")
    print(f"CLINICAL GUIDELINES & REVIEWS COLLECTION")
    print(f"Category: {category}")
    print(f"{'='*70}\n")

    queries = get_disease_queries(category, max_per_disease)

    total_collected = 0
    total_fulltext = 0

    for cat, disease, query in queries:
        print(f"\n{'='*70}")
        print(f"Disease: {disease} ({cat})")
        print(f"{'='*70}")

        # Search
        print(f"Searching... ", end='')
        pmid_list = collector.search_pubmed(query, max_results=max_per_disease)

        if not pmid_list:
            print("No articles found")
            continue

        print(f"Found {len(pmid_list)} articles")

        # Fetch metadata
        print("Fetching metadata...", end=' ')
        metadata_list = collector.fetch_article_metadata(pmid_list)
        print(f"{len(metadata_list)} retrieved")

        # Extract PMC IDs
        pmid_to_pmcid = {}
        for pmid, metadata in zip(pmid_list, metadata_list):
            article_ids = metadata.get('articleids', [])
            for id_entry in article_ids:
                if id_entry.get('idtype') == 'pmc':
                    pmcid = id_entry.get('value', '')
                    if pmcid:
                        pmid_to_pmcid[pmid] = pmcid
                        break

        print(f"Full-text available: {len(pmid_to_pmcid)}")

        # Create output directories
        disease_safe = disease.replace(' ', '_').replace('/', '_')
        metadata_dir = output_dir / cat / disease_safe / "metadata"
        fulltext_dir = output_dir / cat / disease_safe / "fulltext"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        fulltext_dir.mkdir(parents=True, exist_ok=True)

        # Collect articles
        collected = 0
        fulltext = 0

        for pmid, metadata in tqdm(zip(pmid_list, metadata_list),
                                   total=len(pmid_list),
                                   desc=f"{disease[:30]:<30}",
                                   leave=False):

            # Extract clinical information
            clinical_info = extract_clinical_information(metadata)

            # Save metadata with clinical markers
            article_data = {
                'pmid': pmid,
                'pmcid': pmid_to_pmcid.get(pmid),
                'metadata': metadata,
                'clinical_info': clinical_info,
                'disease': disease,
                'category': cat,
                'query': query
            }

            save_article_data(article_data, metadata_dir)
            collected += 1

            # Fetch full text if available
            pmcid = pmid_to_pmcid.get(pmid)
            if pmcid:
                try:
                    full_text_xml = collector.fetch_full_text_xml(pmcid)
                    if full_text_xml:
                        xml_filepath = fulltext_dir / f"{pmcid}.xml"
                        with open(xml_filepath, 'w', encoding='utf-8') as f:
                            f.write(full_text_xml)
                        fulltext += 1
                except Exception as e:
                    # Skip if error (like 400 Bad Request for some PMC IDs)
                    pass

        # Save disease summary
        summary = {
            'disease': disease,
            'category': cat,
            'query': query,
            'metadata_collected': collected,
            'fulltext_collected': fulltext,
            'total_found': len(pmid_list)
        }

        summary_file = output_dir / cat / disease_safe / "summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        total_collected += collected
        total_fulltext += fulltext

        print(f"  Collected: {collected} metadata, {fulltext} full-text")

    print(f"\n{'='*70}")
    print(f"COLLECTION COMPLETE")
    print(f"{'='*70}")
    print(f"Total diseases processed: {len(queries)}")
    print(f"Total metadata: {total_collected}")
    print(f"Total full-text: {total_fulltext}")
    print(f"Output: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Collect clinical guidelines and reviews for infectious diseases"
    )
    parser.add_argument(
        '--disease',
        type=str,
        default='all',
        help='Disease category: all, bacterial, viral, fungal, parasitic, systemic, or specific disease name'
    )
    parser.add_argument(
        '--max',
        type=int,
        default=50,
        help='Maximum articles per disease (default: 50)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=str(OUTPUT_DIR),
        help='Output directory'
    )
    parser.add_argument(
        '--list-diseases',
        action='store_true',
        help='List all available diseases'
    )

    args = parser.parse_args()

    if args.list_diseases:
        print("\nAvailable disease categories and diseases:\n")
        for category, diseases in INFECTIOUS_DISEASES.items():
            print(f"{category.upper()}:")
            for disease in diseases:
                print(f"  - {disease}")
            print()
        return

    # Initialize collector
    collector = PubMedCollector(api_key=NCBI_API_KEY, email=NCBI_EMAIL)
    output_dir = Path(args.output)

    # Check API key
    if not NCBI_API_KEY:
        print("\n⚠️  WARNING: No NCBI API key - collection will be slow (3 req/sec)")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            return

    # Run collection
    collect_clinical_guidelines(
        collector,
        output_dir,
        category=args.disease,
        max_per_disease=args.max
    )


if __name__ == "__main__":
    main()

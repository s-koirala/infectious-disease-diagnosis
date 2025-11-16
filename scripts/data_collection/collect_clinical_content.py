#!/usr/bin/env python3
"""
Collect CLINICAL diagnostic content (not basic research)
Focus: Reviews, Guidelines, Meta-Analyses, Case Reports with diagnostic information
"""

import os
import sys
import time
import json
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm

# Import from existing collector
sys.path.insert(0, os.path.dirname(__file__))
from collect_pubmed_pmc import PubMedCollector, save_article_data

load_dotenv()

NCBI_API_KEY = os.getenv('NCBI_API_KEY', '')
NCBI_EMAIL = os.getenv('NCBI_EMAIL', '')
OUTPUT_DIR = os.getenv('OUTPUT_DIRECTORY', '../../data/raw/pubmed_pmc_clinical')


def build_clinical_diagnostic_query(disease_focus: str = "infectious disease",
                                    open_access_only: bool = True) -> str:
    """
    Build query focused on CLINICAL diagnostic content

    Args:
        disease_focus: Disease area to focus on
        open_access_only: Restrict to Open Access

    Returns:
        Query string optimized for clinical diagnostic information
    """

    # Publication types that contain clinical diagnostic info
    publication_types = [
        'Review[PT]',           # Review articles (overview of topic)
        'Practice Guideline[PT]',  # Clinical practice guidelines
        'Guideline[PT]',        # Guidelines
        'Meta-Analysis[PT]',    # Meta-analyses
        'Systematic Review[PT]',  # Systematic reviews
        'Case Reports[PT]',     # Case reports (clinical presentations)
    ]

    # Clinical diagnostic keywords
    diagnostic_terms = [
        'diagnosis',
        'clinical features',
        'differential diagnosis',
        'diagnostic criteria',
        'clinical presentation',
        'signs and symptoms',
        'diagnostic approach',
        'clinical manifestations'
    ]

    # Build query
    # (disease focus) AND (clinical terms) AND (publication types)

    disease_query = f'"{disease_focus}"[MeSH Terms] OR "{disease_focus}"[Title/Abstract]'

    clinical_query = ' OR '.join([f'"{term}"[Title/Abstract]' for term in diagnostic_terms])

    pubtype_query = ' OR '.join(publication_types)

    query = f'({disease_query}) AND ({clinical_query}) AND ({pubtype_query})'

    # Add open access filter
    if open_access_only:
        query += ' AND ffrft[filter]'

    # Recent content (last 10 years)
    query += ' AND ("2014"[PDAT] : "2025"[PDAT])'

    return query


def build_specific_condition_queries(open_access_only: bool = True) -> List[tuple]:
    """
    Build queries for specific infectious disease conditions

    Returns:
        List of (query_name, query_string) tuples
    """

    # Common infectious diseases that need good diagnostic content
    conditions = [
        "sepsis",
        "pneumonia",
        "meningitis",
        "tuberculosis",
        "HIV infection",
        "influenza",
        "malaria",
        "urinary tract infection",
        "cellulitis",
        "endocarditis",
        "osteomyelitis",
        "gastroenteritis"
    ]

    queries = []

    for condition in conditions:
        query_name = condition.replace(" ", "_")

        # Focus on diagnosis and clinical features
        query = f'"{condition}"[MeSH Terms] AND ("diagnosis"[Title/Abstract] OR "clinical features"[Title/Abstract] OR "differential diagnosis"[Title/Abstract]) AND (Review[PT] OR Practice Guideline[PT] OR Meta-Analysis[PT])'

        if open_access_only:
            query += ' AND ffrft[filter]'

        query += ' AND ("2014"[PDAT] : "2025"[PDAT])'

        queries.append((query_name, query))

    return queries


def collect_clinical_content(collector: PubMedCollector, output_dir: Path,
                             max_articles: int = 500,
                             query_type: str = "general"):
    """
    Collect clinical diagnostic content

    Args:
        collector: PubMedCollector instance
        output_dir: Output directory
        max_articles: Maximum articles to collect
        query_type: "general" or "specific" conditions
    """

    print(f"\n{'='*60}")
    print(f"CLINICAL DIAGNOSTIC CONTENT COLLECTION")
    print(f"{'='*60}\n")

    if query_type == "general":
        query = build_clinical_diagnostic_query(
            disease_focus="infectious disease",
            open_access_only=True
        )
        queries = [("infectious_disease_clinical", query)]
    else:
        queries = build_specific_condition_queries(open_access_only=True)

    all_collected = 0
    all_fulltext = 0

    for query_name, query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query_name}")
        print(f"{'='*60}")
        print(f"Search: {query[:100]}...\n")

        # Search
        print("Searching PubMed...")
        pmid_list = collector.search_pubmed(query, max_results=max_articles)

        if not pmid_list:
            print("No articles found for this query.")
            continue

        print(f"Found {len(pmid_list)} articles")

        # Fetch metadata
        print(f"Collecting metadata...")
        metadata_list = collector.fetch_article_metadata(pmid_list)

        # Extract PMC IDs
        print("Extracting PMC IDs...")
        pmid_to_pmcid = {}
        for pmid, metadata in zip(pmid_list, metadata_list):
            article_ids = metadata.get('articleids', [])
            for id_entry in article_ids:
                if id_entry.get('idtype') == 'pmc':
                    pmcid = id_entry.get('value', '')
                    if pmcid:
                        pmid_to_pmcid[pmid] = pmcid
                        break

        print(f"Found {len(pmid_to_pmcid)} with PMC full text\n")

        # Create output directories for this query
        metadata_dir = output_dir / query_name / "metadata"
        fulltext_dir = output_dir / query_name / "fulltext"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        fulltext_dir.mkdir(parents=True, exist_ok=True)

        # Collect articles
        collected = 0
        fulltext = 0

        for pmid, metadata in tqdm(zip(pmid_list, metadata_list),
                                   total=len(pmid_list),
                                   desc=f"Collecting {query_name}"):

            # Save metadata
            article_data = {
                'pmid': pmid,
                'pmcid': pmid_to_pmcid.get(pmid),
                'metadata': metadata,
                'query_type': query_name,
                'collected_date': datetime.now().isoformat()
            }

            save_article_data(article_data, metadata_dir)
            collected += 1

            # Fetch full text if available
            pmcid = pmid_to_pmcid.get(pmid)
            if pmcid:
                full_text_xml = collector.fetch_full_text_xml(pmcid)
                if full_text_xml:
                    xml_filepath = fulltext_dir / f"{pmcid}.xml"
                    with open(xml_filepath, 'w', encoding='utf-8') as f:
                        f.write(full_text_xml)
                    fulltext += 1

        # Save query summary
        summary = {
            'query_name': query_name,
            'query': query,
            'total_found': len(pmid_list),
            'metadata_collected': collected,
            'fulltext_collected': fulltext,
            'collection_date': datetime.now().isoformat()
        }

        summary_file = output_dir / query_name / "query_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        all_collected += collected
        all_fulltext += fulltext

        print(f"\n{query_name}: {collected} metadata, {fulltext} full-text")

    print(f"\n{'='*60}")
    print(f"TOTAL COLLECTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total metadata: {all_collected}")
    print(f"Total full-text: {all_fulltext}")
    print(f"Output: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Collect clinical diagnostic content (not basic research)"
    )
    parser.add_argument(
        '--type',
        choices=['general', 'specific'],
        default='general',
        help='Query type: general infectious disease or specific conditions'
    )
    parser.add_argument(
        '--max-per-query',
        type=int,
        default=100,
        help='Maximum articles per query (default: 100)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=OUTPUT_DIR,
        help='Output directory'
    )

    args = parser.parse_args()

    # Initialize collector
    collector = PubMedCollector(api_key=NCBI_API_KEY, email=NCBI_EMAIL)
    output_dir = Path(args.output)

    # Check API key
    if not NCBI_API_KEY:
        print("\n⚠️  WARNING: No NCBI API key found!")
        print("Collection will be slower (3 req/sec instead of 10 req/sec)")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)

    # Run collection
    collect_clinical_content(
        collector,
        output_dir,
        max_articles=args.max_per_query,
        query_type=args.type
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
MeSH-Optimized Clinical Guidelines Collection - Iteration 3

Purpose: Address low-yield keywords from Iteration 2 using standardized MeSH terms
         from NCBI's Medical Subject Headings controlled vocabulary.

Strategy:
- Replace free-text queries with MeSH-optimized queries
- Use standardized medical terminology for better retrieval
- Target specific disease categories that had low yields in Iteration 2

Low-yield keywords from Iteration 2:
- "systemic fungal infection": 3 articles → "Invasive Fungal Infections"[MeSH]
- "vector borne infection": 1 article → "Vector Borne Diseases"[MeSH] + specific diseases
- "zoonotic infection": 15 articles → "Zoonoses"[MeSH] + specific diseases
- "upper respiratory tract infection": 18 articles → "Respiratory Tract Infections"[MeSH]

Author: Claude Code
Date: 2025-11-15
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from Bio import Entrez
import requests
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Configuration
NCBI_API_KEY = os.getenv('NCBI_API_KEY')
NCBI_EMAIL = os.getenv('NCBI_EMAIL')
REQUESTS_PER_SECOND = int(os.getenv('REQUESTS_PER_SECOND', 10))
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIRECTORY', '../../data/raw/mesh_optimized_guidelines'))

# Configure Entrez
Entrez.email = NCBI_EMAIL
Entrez.api_key = NCBI_API_KEY

# MeSH-optimized keywords
MESH_KEYWORDS = {
    'vector_borne_diseases': {
        'mesh_term': 'Vector Borne Diseases',
        'description': 'Diseases transmitted by vectors (mosquitoes, ticks, fleas)',
        'specific_diseases': ['Malaria', 'Dengue', 'Lyme Disease', 'West Nile Fever',
                             'Yellow Fever', 'Chikungunya Fever', 'Zika Virus Infection',
                             'Rocky Mountain Spotted Fever', 'Ehrlichiosis', 'Babesiosis']
    },
    'zoonoses': {
        'mesh_term': 'Zoonoses',
        'description': 'Diseases transmitted from animals to humans',
        'specific_diseases': ['Rabies', 'Brucellosis', 'Q Fever', 'Tularemia',
                             'Anthrax', 'Leptospirosis', 'Plague', 'Hantavirus Infections']
    },
    'invasive_mycoses': {
        'mesh_term': 'Invasive Fungal Infections',
        'description': 'Systemic and invasive fungal infections',
        'specific_diseases': ['Candidemia', 'Invasive Aspergillosis', 'Mucormycosis',
                             'Cryptococcal Meningitis', 'Histoplasmosis', 'Coccidioidomycosis',
                             'Pneumocystis Pneumonia']
    },
    'respiratory_infections': {
        'mesh_term': 'Respiratory Tract Infections',
        'description': 'Upper and lower respiratory tract infections',
        'specific_diseases': ['Pharyngitis', 'Sinusitis', 'Otitis Media',
                             'Bronchitis', 'Community Acquired Pneumonia',
                             'Pertussis', 'Croup']
    },
    'opportunistic_infections': {
        'mesh_term': 'Opportunistic Infections',
        'description': 'Infections in immunocompromised patients',
        'specific_diseases': ['CMV Infection', 'PCP Pneumonia', 'Toxoplasmosis',
                             'Cryptosporidiosis', 'Microsporidiosis']
    },
    'sexually_transmitted_diseases': {
        'mesh_term': 'Sexually Transmitted Diseases',
        'description': 'STDs and STIs',
        'specific_diseases': ['Gonorrhea', 'Chlamydia Infections', 'Syphilis',
                             'Genital Herpes', 'Human Papillomavirus Infection',
                             'Chancroid', 'Lymphogranuloma Venereum']
    },
    'central_nervous_system_infections': {
        'mesh_term': 'Central Nervous System Infections',
        'description': 'CNS infections including meningitis and encephalitis',
        'specific_diseases': ['Bacterial Meningitis', 'Viral Meningitis',
                             'Viral Encephalitis', 'Brain Abscess', 'Neurocysticercosis']
    },
    'tropical_medicine': {
        'mesh_term': 'Tropical Medicine',
        'description': 'Diseases prevalent in tropical regions',
        'specific_diseases': ['Malaria', 'Leishmaniasis', 'Schistosomiasis',
                             'Trypanosomiasis', 'Filariasis', 'Onchocerciasis']
    }
}


class MeSHOptimizedCollector:
    """Collector using MeSH-optimized queries"""

    def __init__(self):
        self.last_request_time = 0
        self.request_interval = 1.0 / REQUESTS_PER_SECOND

    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_interval:
            time.sleep(self.request_interval - time_since_last)
        self.last_request_time = time.time()

    def build_mesh_query(self,
                        category_key: str,
                        category_info: Dict,
                        max_results: int = 100) -> str:
        """
        Build MeSH-optimized query

        Strategy:
        1. Use MeSH major topic for primary filtering
        2. Include differential diagnosis focus
        3. Restrict to reviews, guidelines, meta-analyses
        4. English, Humans, Last 20 years
        """

        mesh_term = category_info['mesh_term']

        # MeSH query (use Major Topic for focused results)
        mesh_query = f'"{mesh_term}"[MeSH Major Topic]'

        # Diagnostic focus
        diagnostic_terms = [
            'differential diagnosis',
            'diagnostic approach',
            'clinical features',
            'diagnosis',
        ]
        diagnostic_query = ' OR '.join([f'"{term}"[Title/Abstract]' for term in diagnostic_terms])

        # Publication types
        pub_types = [
            'Review[PT]',
            'Practice Guideline[PT]',
            'Guideline[PT]',
            'Meta-Analysis[PT]',
            'Systematic Review[PT]',
        ]
        pubtype_query = ' OR '.join(pub_types)

        # Build query
        query_parts = [
            f'({mesh_query})',
            f'({diagnostic_query})',
            f'({pubtype_query})',
        ]

        query = ' AND '.join(query_parts)

        # Filters
        query += ' AND ffrft[filter]'  # Free full-text
        query += ' AND English[Language]'
        query += ' AND Humans[MeSH Terms]'

        # Date range: Last 20 years
        current_year = datetime.now().year
        start_year = current_year - 20
        query += f' AND ("{start_year}"[PDAT] : "{current_year}"[PDAT])'

        return query

    def build_specific_disease_query(self,
                                    disease: str,
                                    max_results: int = 50) -> str:
        """Build query for specific disease using MeSH when possible"""

        # Try MeSH term first, fall back to Title/Abstract
        disease_query = f'"{disease}"[MeSH Terms] OR "{disease}"[Title]'

        # Diagnostic focus
        diagnostic_query = '("differential diagnosis"[Title/Abstract] OR "diagnostic approach"[Title/Abstract] OR "clinical features"[Title/Abstract])'

        # Publication types
        pubtype_query = '(Review[PT] OR Practice Guideline[PT] OR Meta-Analysis[PT] OR Systematic Review[PT])'

        # Build complete query
        query = f'({disease_query}) AND {diagnostic_query} AND {pubtype_query}'

        # Filters
        query += ' AND ffrft[filter]'
        query += ' AND English[Language]'
        query += ' AND Humans[MeSH Terms]'

        # Date range
        current_year = datetime.now().year
        start_year = current_year - 20
        query += f' AND ("{start_year}"[PDAT] : "{current_year}"[PDAT])'

        return query

    def search_pubmed(self, query: str, max_results: int = 100) -> List[str]:
        """Search PubMed and return PMIDs"""
        self._rate_limit()

        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort="relevance",
                usehistory="y"
            )
            record = Entrez.read(handle)
            handle.close()
            return record.get('IdList', [])
        except Exception as e:
            print(f"Error searching PubMed: {e}")
            return []

    def fetch_metadata_batch(self, pmid_list: List[str], batch_size: int = 200) -> List[Dict]:
        """Fetch metadata in batches"""
        all_metadata = []

        for i in range(0, len(pmid_list), batch_size):
            batch = pmid_list[i:i + batch_size]
            self._rate_limit()

            try:
                handle = Entrez.esummary(
                    db="pubmed",
                    id=",".join(batch),
                    retmode="json"
                )
                data = json.loads(handle.read())
                handle.close()

                result = data.get('result', {})
                for pmid in batch:
                    if pmid in result:
                        all_metadata.append(result[pmid])
            except Exception as e:
                print(f"Error fetching metadata: {e}")
                continue

        return all_metadata

    def extract_pmc_ids(self, metadata_list: List[Dict]) -> Dict[str, str]:
        """Extract PMC IDs from metadata"""
        pmid_to_pmcid = {}

        for metadata in metadata_list:
            pmid = metadata.get('uid', '')
            article_ids = metadata.get('articleids', [])

            for id_entry in article_ids:
                if id_entry.get('idtype') == 'pmc':
                    pmcid = id_entry.get('value', '')
                    if pmcid:
                        pmid_to_pmcid[pmid] = pmcid
                        break

        return pmid_to_pmcid

    def fetch_fulltext(self, pmc_id: str) -> Optional[str]:
        """Fetch full-text XML from PMC"""
        self._rate_limit()

        url = "https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi"
        params = {
            "verb": "GetRecord",
            "identifier": f"oai:pubmedcentral.nih.gov:{pmc_id.replace('PMC', '')}",
            "metadataPrefix": "pmc"
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.text
            return None
        except Exception:
            return None

    def save_article(self, pmid: str, metadata: Dict, fulltext: Optional[str],
                    output_dir: Path) -> None:
        """Save article metadata and full-text"""

        metadata_dir = output_dir / 'metadata'
        fulltext_dir = output_dir / 'fulltext'
        metadata_dir.mkdir(parents=True, exist_ok=True)
        fulltext_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        metadata_file = metadata_dir / f"{pmid}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({'pmid': pmid, 'metadata': metadata}, f, indent=2)

        # Save full-text
        if fulltext:
            pmc_id = None
            for id_entry in metadata.get('articleids', []):
                if id_entry.get('idtype') == 'pmc':
                    pmc_id = id_entry.get('value', '')
                    break

            if pmc_id:
                fulltext_file = fulltext_dir / f"{pmc_id}.xml"
                with open(fulltext_file, 'w', encoding='utf-8') as f:
                    f.write(fulltext)

    def collect_category(self, category_key: str, category_info: Dict,
                        max_articles: int = 100) -> Dict:
        """Collect articles for a MeSH category"""

        print(f"\n{'='*70}")
        print(f"Category: {category_key}")
        print(f"MeSH Term: {category_info['mesh_term']}")
        print(f"Description: {category_info['description']}")
        print(f"{'='*70}")

        # Build query
        query = self.build_mesh_query(category_key, category_info, max_articles)

        # Search
        print("Searching...", end=' ')
        pmid_list = self.search_pubmed(query, max_articles)
        print(f"Found {len(pmid_list)} articles")

        if not pmid_list:
            return {'category': category_key, 'metadata': 0, 'fulltext': 0}

        # Fetch metadata
        print("Fetching metadata...", end=' ')
        metadata_list = self.fetch_metadata_batch(pmid_list)
        print(f"{len(metadata_list)} retrieved")

        # Extract PMC IDs
        pmid_to_pmcid = self.extract_pmc_ids(metadata_list)
        print(f"Full-text available: {len(pmid_to_pmcid)}")

        # Create output directory
        output_dir = OUTPUT_DIR / category_key.replace(' ', '_')

        # Collect articles
        fulltext_count = 0
        desc = f"{category_key[:30]:<30}"

        for pmid, metadata in tqdm(zip(pmid_list, metadata_list),
                                   total=len(pmid_list),
                                   desc=desc):

            fulltext = None
            if pmid in pmid_to_pmcid:
                pmc_id = pmid_to_pmcid[pmid]
                fulltext = self.fetch_fulltext(pmc_id)
                if fulltext:
                    fulltext_count += 1

            self.save_article(pmid, metadata, fulltext, output_dir)

        # Save summary
        summary = {
            'category': category_key,
            'mesh_term': category_info['mesh_term'],
            'description': category_info['description'],
            'query': query,
            'metadata_collected': len(metadata_list),
            'fulltext_collected': fulltext_count,
            'total_found': len(pmid_list)
        }

        summary_file = output_dir / 'summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"  Collected: {len(metadata_list)} metadata, {fulltext_count} full-text\n")

        return summary


def main():
    """Main collection function"""

    print("="*70)
    print("MESH-OPTIMIZED CLINICAL GUIDELINES COLLECTION")
    print("Iteration 3 - MeSH Controlled Vocabulary")
    print("="*70)
    print()

    print("Strategy:")
    print("- Use NCBI MeSH Major Topic terms")
    print("- Target low-yield categories from Iteration 2")
    print("- Differential diagnosis focus")
    print("- Reviews, Guidelines, Meta-analyses only")
    print("- English, Humans, Last 20 years")
    print()

    collector = MeSHOptimizedCollector()

    print(f"Total MeSH categories: {len(MESH_KEYWORDS)}")
    print()

    # Collect for each MeSH category
    results = []
    for category_key, category_info in MESH_KEYWORDS.items():
        result = collector.collect_category(category_key, category_info, max_articles=100)
        results.append(result)

    # Final summary
    print("\n" + "="*70)
    print("COLLECTION COMPLETE")
    print("="*70)

    total_metadata = sum(r['metadata_collected'] for r in results)
    total_fulltext = sum(r['fulltext_collected'] for r in results)

    print(f"\nTotal MeSH categories: {len(results)}")
    print(f"Total metadata: {total_metadata}")
    print(f"Total full-text: {total_fulltext}")
    print(f"Full-text coverage: {total_fulltext/total_metadata*100:.1f}%")
    print(f"\nOutput: {OUTPUT_DIR}")

    # Save overall summary
    overall_summary = {
        'collection_date': datetime.now().isoformat(),
        'iteration': 3,
        'strategy': 'MeSH-optimized queries',
        'total_categories': len(results),
        'total_metadata': total_metadata,
        'total_fulltext': total_fulltext,
        'categories': results
    }

    summary_file = OUTPUT_DIR / 'collection_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(overall_summary, f, indent=2)

    print(f"Summary: {summary_file}")


if __name__ == "__main__":
    main()

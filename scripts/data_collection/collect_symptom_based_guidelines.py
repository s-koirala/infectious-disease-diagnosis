#!/usr/bin/env python3
"""
Symptom-based Clinical Guidelines Collection - Second Iteration

Purpose: Collect clinical guidelines focused on SYMPTOMS and CLINICAL PRESENTATIONS
         rather than specific diseases. This aligns with the actual clinical workflow
         where physicians start with symptoms and work toward diagnosis.

Updated Query Strategy:
- Symptom-based keywords (fever, rash, headache, etc.)
- Specific high-priority conditions
- Filters: English, Humans, Reviews/Guidelines/Meta-analyses, Last 20 years

Output Goals:
1. Most probable differential diagnosis (DD)
2. Less common but important (secondary) differential diagnosis
3. Less common/rare differential diagnosis
4. Lab tests for highest probability DD
5. Clarification questions to refine DD

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
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIRECTORY', '../../data/raw/symptom_based_guidelines'))

# Configure Entrez
Entrez.email = NCBI_EMAIL
Entrez.api_key = NCBI_API_KEY

# Symptom-based and clinical presentation keywords
CLINICAL_KEYWORDS = {
    'symptoms': [
        'fever',
        'rash',
        'headache',
        'nausea',
        'vomiting',
        'diarrhea',
    ],
    'conditions': [
        'sepsis',
        'septic shock',
        'pneumonia',
        'endocarditis',
        'encephalitis',
        'meningitis',
        'hepatitis',
        'HIV',
        'AIDS',
        'tuberculosis',
        'systemic fungal infection',
        'upper respiratory tract infection',
        'urinary tract infection',
        'vector borne infection',
        'zoonotic infection',
    ],
    'diagnostic_focus': [
        'differential diagnosis',
        'diagnostic approach',
        'clinical features',
        'diagnostic criteria',
        'laboratory diagnosis',
        'diagnostic workup',
    ]
}

class SymptomBasedCollector:
    """Collector for symptom-based clinical guidelines"""

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

    def build_symptom_query(self,
                           symptom: str,
                           max_results: int = 100) -> str:
        """
        Build optimized query for symptom-based clinical guidelines

        Focus on:
        - Specific symptom/condition
        - Differential diagnosis content
        - Diagnostic approach
        - Publication types: Reviews, Guidelines, Meta-analyses
        - Filters: English, Humans, Last 20 years
        """

        # Symptom or condition (main focus)
        symptom_query = f'"{symptom}"[Title/Abstract]'

        # Diagnostic focus terms
        diagnostic_terms = [
            'differential diagnosis',
            'diagnostic approach',
            'diagnostic criteria',
            'clinical features',
            'diagnosis',
        ]
        diagnostic_query = ' OR '.join([f'"{term}"[Title/Abstract]' for term in diagnostic_terms])

        # Publication types (high-quality clinical content)
        pub_types = [
            'Review[PT]',
            'Practice Guideline[PT]',
            'Guideline[PT]',
            'Meta-Analysis[PT]',
            'Systematic Review[PT]',
        ]
        pubtype_query = ' OR '.join(pub_types)

        # Build complete query
        query_parts = [
            f'({symptom_query})',
            f'({diagnostic_query})',
            f'({pubtype_query})',
        ]

        query = ' AND '.join(query_parts)

        # Add filters
        query += ' AND ffrft[filter]'  # Free full-text
        query += ' AND English[Language]'  # English only
        query += ' AND Humans[MeSH Terms]'  # Human studies only

        # Date filter: Last 20 years (2005-2025)
        current_year = datetime.now().year
        start_year = current_year - 20
        query += f' AND ("{start_year}"[PDAT] : "{current_year}"[PDAT])'

        return query

    def search_pubmed(self, query: str, max_results: int = 100) -> List[str]:
        """Search PubMed and return list of PMIDs"""
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
        """Fetch article metadata in batches"""
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

                # Extract article data
                result = data.get('result', {})
                for pmid in batch:
                    if pmid in result:
                        all_metadata.append(result[pmid])

            except Exception as e:
                print(f"Error fetching metadata batch: {e}")
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

        url = f"https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi"
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
        except Exception as e:
            return None

    def save_article(self, pmid: str, metadata: Dict, fulltext: Optional[str],
                    output_dir: Path) -> None:
        """Save article metadata and full-text"""

        # Create directories
        metadata_dir = output_dir / 'metadata'
        fulltext_dir = output_dir / 'fulltext'
        metadata_dir.mkdir(parents=True, exist_ok=True)
        fulltext_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        metadata_file = metadata_dir / f"{pmid}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({'pmid': pmid, 'metadata': metadata}, f, indent=2)

        # Save full-text if available
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

    def collect_for_keyword(self, keyword: str, max_articles: int = 100) -> Dict:
        """Collect articles for a specific symptom/keyword"""

        print(f"\n{'='*70}")
        print(f"Keyword: {keyword}")
        print(f"{'='*70}")

        # Build query
        query = self.build_symptom_query(keyword, max_articles)

        # Search
        print("Searching...", end=' ')
        pmid_list = self.search_pubmed(query, max_articles)
        print(f"Found {len(pmid_list)} articles matching query")

        if not pmid_list:
            return {'keyword': keyword, 'metadata': 0, 'fulltext': 0}

        # Fetch metadata
        print(f"Fetching metadata...", end=' ')
        metadata_list = self.fetch_metadata_batch(pmid_list)
        print(f"{len(metadata_list)} retrieved")

        # Extract PMC IDs
        pmid_to_pmcid = self.extract_pmc_ids(metadata_list)
        print(f"Full-text available: {len(pmid_to_pmcid)}")

        # Create output directory
        output_dir = OUTPUT_DIR / keyword.replace(' ', '_').replace('/', '_')

        # Collect articles with progress bar
        fulltext_count = 0

        desc = f"{keyword[:30]:<30}"
        for pmid, metadata in tqdm(zip(pmid_list, metadata_list),
                                   total=len(pmid_list),
                                   desc=desc):

            # Fetch full-text if available
            fulltext = None
            if pmid in pmid_to_pmcid:
                pmc_id = pmid_to_pmcid[pmid]
                fulltext = self.fetch_fulltext(pmc_id)
                if fulltext:
                    fulltext_count += 1

            # Save article
            self.save_article(pmid, metadata, fulltext, output_dir)

        # Save summary
        summary = {
            'keyword': keyword,
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
    print("SYMPTOM-BASED CLINICAL GUIDELINES COLLECTION")
    print("Second Iteration - Refined Query Strategy")
    print("="*70)
    print()

    print("Collection Strategy:")
    print("- Focus: Symptoms and clinical presentations")
    print("- Diagnostic content: Differential diagnosis, diagnostic approach")
    print("- Publication types: Reviews, Guidelines, Meta-analyses")
    print("- Filters: English, Humans, Last 20 years")
    print()

    # Initialize collector
    collector = SymptomBasedCollector()

    # Combine all keywords
    all_keywords = (
        CLINICAL_KEYWORDS['symptoms'] +
        CLINICAL_KEYWORDS['conditions']
    )

    print(f"Total keywords to process: {len(all_keywords)}")
    print()

    # Collect for each keyword
    results = []
    for keyword in all_keywords:
        result = collector.collect_for_keyword(keyword, max_articles=100)
        results.append(result)

    # Final summary
    print("\n" + "="*70)
    print("COLLECTION COMPLETE")
    print("="*70)

    total_metadata = sum(r['metadata_collected'] for r in results)
    total_fulltext = sum(r['fulltext_collected'] for r in results)

    print(f"\nTotal keywords processed: {len(results)}")
    print(f"Total metadata collected: {total_metadata}")
    print(f"Total full-text collected: {total_fulltext}")
    print(f"Full-text coverage: {total_fulltext/total_metadata*100:.1f}%")

    print(f"\nOutput directory: {OUTPUT_DIR}")

    # Save overall summary
    overall_summary = {
        'collection_date': datetime.now().isoformat(),
        'total_keywords': len(results),
        'total_metadata': total_metadata,
        'total_fulltext': total_fulltext,
        'keywords': results
    }

    summary_file = OUTPUT_DIR / 'collection_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(overall_summary, f, indent=2)

    print(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()

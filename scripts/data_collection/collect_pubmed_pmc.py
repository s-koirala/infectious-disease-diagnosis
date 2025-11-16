#!/usr/bin/env python3
"""
PubMed/PMC Data Collection Script
Collects infectious disease articles from PubMed Central Open Access Subset

Usage:
    python collect_pubmed_pmc.py --query "infectious disease" --max-results 1000
    python collect_pubmed_pmc.py --pilot  # Collects 100 articles for testing
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

# Load environment variables
load_dotenv()

# Configuration
NCBI_API_KEY = os.getenv('NCBI_API_KEY', '')
NCBI_EMAIL = os.getenv('NCBI_EMAIL', '')
REQUESTS_PER_SECOND = float(os.getenv('REQUESTS_PER_SECOND', '3'))
OUTPUT_DIR = os.getenv('OUTPUT_DIRECTORY', '../../data/raw/pubmed_pmc')

# NCBI E-utilities Base URLs
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
ESEARCH_URL = f"{EUTILS_BASE}esearch.fcgi"
EFETCH_URL = f"{EUTILS_BASE}efetch.fcgi"
ESUMMARY_URL = f"{EUTILS_BASE}esummary.fcgi"

# Rate limiting
RATE_LIMIT_DELAY = 1.0 / REQUESTS_PER_SECOND


class PubMedCollector:
    """Collects articles from PubMed/PMC Open Access Subset"""

    def __init__(self, api_key: str = '', email: str = ''):
        self.api_key = api_key
        self.email = email
        self.session = requests.Session()
        self.last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting between API calls"""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()

    def search_pubmed(self, query: str, max_results: int = 100,
                     database: str = "pubmed") -> List[str]:
        """
        Search PubMed for articles matching query

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            database: Database to search ('pubmed' or 'pmc')

        Returns:
            List of PubMed IDs (PMIDs) or PMC IDs
        """
        self._rate_limit()

        params = {
            "db": database,
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "usehistory": "y"
        }

        if self.api_key:
            params["api_key"] = self.api_key
        if self.email:
            params["email"] = self.email

        try:
            response = self.session.get(ESEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()

            result = data.get("esearchresult", {})
            id_list = result.get("idlist", [])
            count = int(result.get("count", 0))

            print(f"Found {count} articles matching query")
            print(f"Retrieved {len(id_list)} IDs")

            return id_list

        except Exception as e:
            print(f"Error searching PubMed: {e}")
            return []

    def fetch_article_metadata(self, pmid_list: List[str],
                               database: str = "pubmed") -> List[Dict]:
        """
        Fetch metadata for list of PMIDs

        Args:
            pmid_list: List of PubMed IDs
            database: Database ('pubmed' or 'pmc')

        Returns:
            List of article metadata dictionaries
        """
        if not pmid_list:
            return []

        self._rate_limit()

        params = {
            "db": database,
            "id": ",".join(pmid_list),
            "retmode": "json"
        }

        if self.api_key:
            params["api_key"] = self.api_key

        try:
            response = self.session.get(ESUMMARY_URL, params=params)
            response.raise_for_status()
            data = response.json()

            result = data.get("result", {})
            articles = []

            for pmid in pmid_list:
                if pmid in result:
                    articles.append(result[pmid])

            return articles

        except Exception as e:
            print(f"Error fetching metadata: {e}")
            return []

    def fetch_full_text_xml(self, pmc_id: str) -> Optional[str]:
        """
        Fetch full-text XML for a PMC article

        Args:
            pmc_id: PMC ID (with or without 'PMC' prefix)

        Returns:
            XML content as string, or None if error
        """
        self._rate_limit()

        # Ensure PMC prefix
        if not pmc_id.startswith('PMC'):
            pmc_id = f"PMC{pmc_id}"

        params = {
            "db": "pmc",
            "id": pmc_id,
            "retmode": "xml"
        }

        if self.api_key:
            params["api_key"] = self.api_key

        try:
            response = self.session.get(EFETCH_URL, params=params)
            response.raise_for_status()
            return response.text

        except Exception as e:
            print(f"Error fetching full text for {pmc_id}: {e}")
            return None

    def convert_pmid_to_pmcid(self, pmid_list: List[str]) -> Dict[str, str]:
        """
        Convert PMIDs to PMC IDs using ID Converter API

        Args:
            pmid_list: List of PubMed IDs

        Returns:
            Dictionary mapping PMID -> PMCID
        """
        if not pmid_list:
            return {}

        self._rate_limit()

        converter_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
        params = {
            "ids": ",".join(pmid_list),
            "format": "json"
        }

        try:
            response = self.session.get(converter_url, params=params)
            response.raise_for_status()
            data = response.json()

            mapping = {}
            for record in data.get("records", []):
                pmid = record.get("pmid")
                pmcid = record.get("pmcid")
                if pmid and pmcid:
                    mapping[pmid] = pmcid

            return mapping

        except Exception as e:
            print(f"Error converting IDs: {e}")
            return {}


def build_infectious_disease_query(open_access_only: bool = True) -> str:
    """
    Build optimized search query for infectious disease articles

    Args:
        open_access_only: If True, restrict to Open Access articles

    Returns:
        Formatted query string
    """
    # Core infectious disease terms
    id_terms = [
        "infectious disease",
        "bacterial infection",
        "viral infection",
        "fungal infection",
        "parasitic infection",
        "sepsis",
        "pneumonia",
        "meningitis",
        "tuberculosis",
        "HIV",
        "hepatitis",
        "influenza"
    ]

    # Combine with OR
    query = " OR ".join([f'"{term}"' for term in id_terms])

    # Add free full text filter (for PMC Open Access articles)
    if open_access_only:
        query += ' AND ffrft[filter]'

    # Restrict to recent articles (last 10 years for relevance)
    query += ' AND ("2014"[PDAT] : "2025"[PDAT])'

    return query


def save_article_data(article_data: Dict, output_dir: Path):
    """
    Save article data to JSON file

    Args:
        article_data: Article data dictionary
        output_dir: Output directory path
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    pmid = article_data.get('pmid', 'unknown')
    filename = f"article_{pmid}.json"
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(article_data, f, indent=2, ensure_ascii=False)


def collect_pilot_dataset(collector: PubMedCollector, output_dir: Path,
                          max_articles: int = 100):
    """
    Collect pilot dataset of infectious disease articles

    Args:
        collector: PubMedCollector instance
        output_dir: Output directory for saved articles
        max_articles: Number of articles to collect
    """
    print(f"\n{'='*60}")
    print(f"PILOT DATASET COLLECTION")
    print(f"{'='*60}\n")

    # Build query
    query = build_infectious_disease_query(open_access_only=True)
    print(f"Query: {query[:100]}...\n")

    # Search PubMed
    print("Searching PubMed...")
    pmid_list = collector.search_pubmed(query, max_results=max_articles)

    if not pmid_list:
        print("No articles found. Exiting.")
        return

    print(f"\nCollecting metadata for {len(pmid_list)} articles...")

    # Fetch metadata
    metadata_list = collector.fetch_article_metadata(pmid_list)

    # Extract PMC IDs from metadata
    print("\nExtracting PMC IDs from metadata...")
    pmid_to_pmcid = {}
    for pmid, metadata in zip(pmid_list, metadata_list):
        # Check articleids for PMC ID
        article_ids = metadata.get('articleids', [])
        for id_entry in article_ids:
            if id_entry.get('idtype') == 'pmc':
                pmcid = id_entry.get('value', '')
                if pmcid:
                    pmid_to_pmcid[pmid] = pmcid
                    break

    print(f"Found {len(pmid_to_pmcid)} articles with PMC full text available")

    # Create output directories
    metadata_dir = output_dir / "metadata"
    fulltext_dir = output_dir / "fulltext"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    fulltext_dir.mkdir(parents=True, exist_ok=True)

    # Save metadata and attempt to fetch full text
    collected_count = 0
    fulltext_count = 0

    for pmid, metadata in tqdm(zip(pmid_list, metadata_list),
                                total=len(pmid_list),
                                desc="Collecting articles"):

        # Save metadata
        article_data = {
            'pmid': pmid,
            'pmcid': pmid_to_pmcid.get(pmid),
            'metadata': metadata,
            'collected_date': datetime.now().isoformat()
        }

        save_article_data(article_data, metadata_dir)
        collected_count += 1

        # Fetch full text if PMC ID available
        pmcid = pmid_to_pmcid.get(pmid)
        if pmcid:
            full_text_xml = collector.fetch_full_text_xml(pmcid)
            if full_text_xml:
                xml_filepath = fulltext_dir / f"{pmcid}.xml"
                with open(xml_filepath, 'w', encoding='utf-8') as f:
                    f.write(full_text_xml)
                fulltext_count += 1

    # Save collection summary
    summary = {
        'query': query,
        'total_found': len(pmid_list),
        'metadata_collected': collected_count,
        'fulltext_collected': fulltext_count,
        'collection_date': datetime.now().isoformat(),
        'output_directory': str(output_dir)
    }

    summary_file = output_dir / "collection_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print(f"COLLECTION COMPLETE")
    print(f"{'='*60}")
    print(f"Metadata collected: {collected_count}")
    print(f"Full text collected: {fulltext_count}")
    print(f"Output directory: {output_dir}")
    print(f"Summary saved to: {summary_file}")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Collect infectious disease articles from PubMed/PMC"
    )
    parser.add_argument(
        '--pilot',
        action='store_true',
        help='Run pilot collection (100 articles)'
    )
    parser.add_argument(
        '--query',
        type=str,
        help='Custom search query (overrides default)'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=100,
        help='Maximum number of articles to collect (default: 100)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=OUTPUT_DIR,
        help='Output directory for collected articles'
    )

    args = parser.parse_args()

    # Initialize collector
    collector = PubMedCollector(api_key=NCBI_API_KEY, email=NCBI_EMAIL)

    # Setup output directory
    output_dir = Path(args.output)

    # Check API key
    if not NCBI_API_KEY:
        print("\n⚠️  WARNING: No NCBI API key found!")
        print("Without an API key, you are limited to 3 requests/second.")
        print("Get your free API key at: https://www.ncbi.nlm.nih.gov/account/settings/")
        print("Add it to your .env file as: NCBI_API_KEY=your_key_here\n")
        response = input("Continue without API key? (y/n): ")
        if response.lower() != 'y':
            print("Exiting. Please add your API key and try again.")
            sys.exit(0)

    # Run collection
    if args.pilot:
        collect_pilot_dataset(collector, output_dir, max_articles=100)
    else:
        max_results = args.max_results
        collect_pilot_dataset(collector, output_dir, max_articles=max_results)


if __name__ == "__main__":
    main()

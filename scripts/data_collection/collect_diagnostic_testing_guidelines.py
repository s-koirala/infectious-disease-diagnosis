#!/usr/bin/env python3
"""
Diagnostic Testing Guidelines Collection - Iteration 4

Purpose: Collect literature on laboratory and diagnostic testing for infectious diseases
         to support Output #4: "Lab tests for DD with highest probability"

Strategy:
- Use MeSH-optimized queries focusing on diagnostic methodologies
- Target test interpretation, diagnostic algorithms, and test performance
- Reviews, Guidelines, Meta-analyses only
- English, Humans, Last 20 years

Author: Claude Code
Date: 2025-11-16
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
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIRECTORY', '../../data/raw/diagnostic_testing_guidelines'))

# Configure Entrez
Entrez.email = NCBI_EMAIL
Entrez.api_key = NCBI_API_KEY

# MeSH-optimized diagnostic testing categories
DIAGNOSTIC_CATEGORIES = {
    'molecular_diagnostics': {
        'mesh_term': 'Molecular Diagnostic Techniques',
        'description': 'PCR, NGS, and nucleic acid amplification tests',
        'specific_tests': ['PCR', 'Multiplex PCR', 'Next-Generation Sequencing', 'NAAT',
                          'RT-PCR', 'Real-time PCR', 'GeneXpert'],
    },
    'serologic_testing': {
        'mesh_term': 'Serologic Tests',
        'description': 'Antibody and antigen detection tests',
        'specific_tests': ['ELISA', 'IFA', 'Western Blot', 'Rapid Antigen Test',
                          'Immunofluorescence', 'Agglutination Tests'],
    },
    'blood_culture': {
        'mesh_term': 'Blood Culture',
        'description': 'Blood culture for bacteremia and fungemia diagnosis',
        'specific_tests': ['Blood culture', 'BACTEC', 'BacT/ALERT',
                          'Time to positivity', 'Culture contamination'],
    },
    'antimicrobial_susceptibility': {
        'mesh_term': 'Microbial Sensitivity Tests',
        'description': 'Antibiotic resistance and susceptibility testing',
        'specific_tests': ['MIC determination', 'Disk diffusion', 'E-test',
                          'Automated susceptibility testing', 'Resistance mechanisms'],
    },
    'viral_load_monitoring': {
        'mesh_term': 'Viral Load',
        'description': 'Quantitative viral testing for treatment monitoring',
        'specific_tests': ['HIV viral load', 'HCV viral load', 'CMV viral load',
                          'EBV viral load', 'Quantitative PCR'],
    },
    'tuberculosis_diagnostics': {
        'mesh_term': 'Tuberculosis',
        'mesh_qualifier': 'diagnosis',
        'description': 'TB-specific diagnostic tests',
        'specific_tests': ['AFB smear', 'Mycobacterial culture', 'GeneXpert MTB/RIF',
                          'IGRA', 'QuantiFERON', 'T-SPOT', 'TB PCR'],
    },
    'fungal_diagnostics': {
        'mesh_term': 'Mycoses',
        'mesh_qualifier': 'diagnosis',
        'description': 'Fungal biomarkers and diagnostic tests',
        'specific_tests': ['Galactomannan', 'Beta-D-glucan', 'Cryptococcal antigen',
                          'Fungal culture', 'Fungal PCR', 'Aspergillus antigen'],
    },
    'point_of_care_testing': {
        'mesh_term': 'Point-of-Care Testing',
        'description': 'Rapid diagnostic tests at point of care',
        'specific_tests': ['Malaria RDT', 'Strep test', 'Influenza rapid test',
                          'COVID-19 rapid test', 'Rapid HIV test', 'Bedside testing'],
    },
    'csf_analysis': {
        'mesh_term': 'Cerebrospinal Fluid',
        'mesh_qualifier': 'analysis',
        'description': 'CSF testing for CNS infections',
        'specific_tests': ['CSF cell count', 'CSF protein', 'CSF glucose',
                          'CSF culture', 'CSF PCR', 'Meningitis/encephalitis panel'],
    },
    'gi_pathogen_testing': {
        'mesh_term': 'Gastrointestinal Diseases',
        'additional_mesh': 'Molecular Diagnostic Techniques',
        'description': 'GI multiplex PCR panels and stool testing',
        'specific_tests': ['Stool culture', 'Ova and parasites', 'FilmArray GI',
                          'BioFire GI panel', 'C. difficile testing', 'Fecal leukocytes'],
    },
    'sti_testing': {
        'mesh_term': 'Sexually Transmitted Diseases',
        'mesh_qualifier': 'diagnosis',
        'description': 'STI testing algorithms and interpretation',
        'specific_tests': ['NAAT for GC/CT', 'RPR/VDRL', 'Syphilis testing',
                          'HIV testing algorithm', 'HSV PCR', 'HPV testing'],
    },
    'biomarkers_infection': {
        'mesh_term': 'Biomarkers',
        'additional_mesh': 'Bacterial Infections',
        'description': 'Biomarkers for infection diagnosis and management',
        'specific_tests': ['Procalcitonin', 'C-reactive protein', 'Presepsin',
                          'Lactate', 'ESR', 'Sepsis biomarkers'],
    },
}


class DiagnosticTestingCollector:
    """Collector for diagnostic testing literature"""

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

    def build_diagnostic_query(self,
                              category_key: str,
                              category_info: Dict,
                              max_results: int = 200) -> str:
        """
        Build MeSH-optimized query for diagnostic testing

        Strategy:
        1. Use MeSH Major Topic or MeSH with qualifier
        2. Include diagnostic focus terms
        3. Restrict to reviews, guidelines, meta-analyses
        4. English, Humans, Last 20 years
        """

        mesh_term = category_info['mesh_term']
        mesh_qualifier = category_info.get('mesh_qualifier', '')
        additional_mesh = category_info.get('additional_mesh', '')

        # Build MeSH query
        if mesh_qualifier:
            # Use MeSH with qualifier (e.g., Tuberculosis/diagnosis)
            mesh_query = f'"{mesh_term}/{mesh_qualifier}"[MeSH Terms]'
        else:
            # Use MeSH Major Topic
            mesh_query = f'"{mesh_term}"[MeSH Major Topic]'

        # Add additional MeSH if specified
        if additional_mesh:
            mesh_query += f' AND "{additional_mesh}"[MeSH Terms]'

        # Diagnostic focus terms
        diagnostic_terms = [
            'laboratory diagnosis',
            'diagnostic test',
            'test interpretation',
            'diagnostic accuracy',
            'sensitivity and specificity',
            'test performance',
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

        # Build complete query
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

    def search_pubmed(self, query: str, max_results: int = 200) -> List[str]:
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
                        max_articles: int = 200) -> Dict:
        """Collect articles for a diagnostic testing category"""

        print(f"\n{'='*70}")
        print(f"Category: {category_key}")
        print(f"MeSH Term: {category_info['mesh_term']}")
        print(f"Description: {category_info['description']}")
        print(f"{'='*70}")

        # Build query
        query = self.build_diagnostic_query(category_key, category_info, max_articles)

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
    print("DIAGNOSTIC TESTING GUIDELINES COLLECTION")
    print("Iteration 4 - Laboratory and Diagnostic Testing")
    print("="*70)
    print()

    print("Strategy:")
    print("- Use NCBI MeSH terms for diagnostic methodologies")
    print("- Focus on test interpretation and diagnostic algorithms")
    print("- Reviews, Guidelines, Meta-analyses only")
    print("- English, Humans, Last 20 years")
    print()

    collector = DiagnosticTestingCollector()

    print(f"Total diagnostic categories: {len(DIAGNOSTIC_CATEGORIES)}")
    print()

    # Collect for each diagnostic category
    results = []
    for category_key, category_info in DIAGNOSTIC_CATEGORIES.items():
        result = collector.collect_category(category_key, category_info, max_articles=200)
        results.append(result)

    # Final summary
    print("\n" + "="*70)
    print("COLLECTION COMPLETE")
    print("="*70)

    total_metadata = sum(r['metadata_collected'] for r in results)
    total_fulltext = sum(r['fulltext_collected'] for r in results)

    print(f"\nTotal diagnostic categories: {len(results)}")
    print(f"Total metadata: {total_metadata}")
    print(f"Total full-text: {total_fulltext}")
    if total_metadata > 0:
        print(f"Full-text coverage: {total_fulltext/total_metadata*100:.1f}%")
    print(f"\nOutput: {OUTPUT_DIR}")

    # Save overall summary
    overall_summary = {
        'collection_date': datetime.now().isoformat(),
        'iteration': 4,
        'strategy': 'MeSH-optimized diagnostic testing queries',
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

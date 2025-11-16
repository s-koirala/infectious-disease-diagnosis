#!/usr/bin/env python3
"""
Deduplicate Articles Across All Collection Iterations

Purpose: Identify and remove duplicate articles across Iterations 1, 2, and 3
         based on PMID (unique identifier).

Strategy:
- Scan all metadata JSON files across all iterations
- Track unique PMIDs and which iterations they appeared in
- Create deduplicated dataset with source iteration tracking
- Generate deduplication report

Author: Claude Code
Date: 2025-11-16
"""

import os
import json
from pathlib import Path
from typing import Dict, Set, List
from collections import defaultdict
import shutil

# Configuration
DATA_DIR = Path(r"C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\data\raw")
OUTPUT_DIR = Path(r"C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\data\processed\deduplicated")
REPORT_DIR = Path(r"C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\reports")

# Collection directories
# Note: Iterations 2 and 3 both saved to pubmed_pmc with different subdirectories
COLLECTIONS = {
    'iteration_1_disease': DATA_DIR / 'clinical_guidelines',
    'iteration_2_and_3_combined': DATA_DIR / 'pubmed_pmc',
}


def find_all_metadata_files(base_dir: Path) -> List[Path]:
    """Recursively find all metadata JSON files"""
    metadata_files = []

    if not base_dir.exists():
        print(f"Warning: Directory not found: {base_dir}")
        return metadata_files

    # Find all metadata subdirectories
    for metadata_dir in base_dir.rglob('metadata'):
        if metadata_dir.is_dir():
            # Get all JSON files in this metadata directory
            json_files = list(metadata_dir.glob('*.json'))
            metadata_files.extend(json_files)

    return metadata_files


def extract_pmid_from_metadata(json_file: Path) -> str:
    """Extract PMID from metadata JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('pmid', '')
    except Exception as e:
        print(f"Error reading {json_file}: {e}")
        return ''


def find_fulltext_file(pmid: str, metadata_file: Path) -> Path:
    """Find corresponding full-text XML file for a PMID"""
    # Full-text directory is sibling to metadata directory
    metadata_dir = metadata_file.parent
    fulltext_dir = metadata_dir.parent / 'fulltext'

    if not fulltext_dir.exists():
        return None

    # Try to find XML file with PMC ID
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            metadata = data.get('metadata', {})
            article_ids = metadata.get('articleids', [])

            for id_entry in article_ids:
                if id_entry.get('idtype') == 'pmc':
                    pmc_id = id_entry.get('value', '')
                    xml_file = fulltext_dir / f"{pmc_id}.xml"
                    if xml_file.exists():
                        return xml_file
    except Exception:
        pass

    return None


def deduplicate_collections():
    """Main deduplication function"""

    print("="*70)
    print("ARTICLE DEDUPLICATION ACROSS ITERATIONS")
    print("="*70)
    print()

    # Track PMIDs and their sources
    pmid_to_sources = defaultdict(list)  # PMID -> list of (iteration, file_path)
    pmid_to_metadata = {}  # PMID -> first metadata file encountered
    pmid_to_fulltext = {}  # PMID -> full-text file if exists

    # Scan all iterations
    for iteration_name, collection_dir in COLLECTIONS.items():
        print(f"Scanning {iteration_name}...")

        metadata_files = find_all_metadata_files(collection_dir)
        print(f"  Found {len(metadata_files)} metadata files")

        for metadata_file in metadata_files:
            pmid = extract_pmid_from_metadata(metadata_file)
            if pmid:
                # Track which iteration this PMID appeared in
                pmid_to_sources[pmid].append((iteration_name, metadata_file))

                # Store first occurrence
                if pmid not in pmid_to_metadata:
                    pmid_to_metadata[pmid] = metadata_file

                    # Check for full-text
                    fulltext_file = find_fulltext_file(pmid, metadata_file)
                    if fulltext_file:
                        pmid_to_fulltext[pmid] = fulltext_file

    print()
    print("="*70)
    print("DEDUPLICATION ANALYSIS")
    print("="*70)
    print()

    # Statistics
    total_articles_found = sum(len(find_all_metadata_files(d)) for d in COLLECTIONS.values())
    unique_articles = len(pmid_to_metadata)
    duplicates = total_articles_found - unique_articles
    articles_with_fulltext = len(pmid_to_fulltext)

    print(f"Total articles found across all iterations: {total_articles_found}")
    print(f"Unique articles (by PMID): {unique_articles}")
    print(f"Duplicate instances: {duplicates}")
    print(f"Unique articles with full-text: {articles_with_fulltext}")
    print(f"Full-text coverage: {articles_with_fulltext/unique_articles*100:.1f}%")
    print()

    # Breakdown by iteration overlap
    iteration_counts = defaultdict(int)
    for pmid, sources in pmid_to_sources.items():
        num_iterations = len(sources)
        iteration_counts[num_iterations] += 1

    print("Articles by number of iterations they appear in:")
    for num_iters in sorted(iteration_counts.keys()):
        count = iteration_counts[num_iters]
        print(f"  {num_iters} iteration(s): {count} articles")
    print()

    # Identify most duplicated articles
    most_duplicated = sorted(pmid_to_sources.items(),
                             key=lambda x: len(x[1]),
                             reverse=True)[:10]

    if any(len(sources) > 1 for _, sources in most_duplicated):
        print("Top 10 most duplicated articles:")
        for pmid, sources in most_duplicated:
            if len(sources) > 1:
                # Get title
                try:
                    with open(sources[0][1], 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        title = data.get('metadata', {}).get('title', 'N/A')[:60]
                except Exception:
                    title = 'N/A'

                iteration_names = [s[0].replace('iteration_', 'Iter ').replace('_', ' ').title()
                                  for s in sources]
                print(f"  PMID {pmid}: {len(sources)} times - {iteration_names}")
                print(f"    {title}...")
        print()

    # Create deduplicated dataset
    print("="*70)
    print("CREATING DEDUPLICATED DATASET")
    print("="*70)
    print()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata_out = OUTPUT_DIR / 'metadata'
    fulltext_out = OUTPUT_DIR / 'fulltext'
    metadata_out.mkdir(exist_ok=True)
    fulltext_out.mkdir(exist_ok=True)

    # Copy unique articles
    for pmid, metadata_file in pmid_to_metadata.items():
        # Copy metadata with source tracking
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Add deduplication metadata
            sources = [s[0] for s in pmid_to_sources[pmid]]
            data['deduplication_info'] = {
                'appeared_in_iterations': sources,
                'num_iterations': len(sources),
                'is_duplicate': len(sources) > 1,
            }

            # Save
            output_file = metadata_out / f"{pmid}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error processing PMID {pmid}: {e}")
            continue

        # Copy full-text if exists
        if pmid in pmid_to_fulltext:
            fulltext_file = pmid_to_fulltext[pmid]
            pmc_id = fulltext_file.stem
            output_fulltext = fulltext_out / f"{pmc_id}.xml"
            try:
                shutil.copy2(fulltext_file, output_fulltext)
            except Exception as e:
                print(f"Error copying full-text for PMID {pmid}: {e}")

    print(f"Copied {len(pmid_to_metadata)} unique metadata files to {metadata_out}")
    print(f"Copied {len(pmid_to_fulltext)} unique full-text files to {fulltext_out}")
    print()

    # Generate deduplication report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORT_DIR / 'deduplication_report.json'

    report = {
        'total_articles_found': total_articles_found,
        'unique_articles': unique_articles,
        'duplicate_instances': duplicates,
        'articles_with_fulltext': articles_with_fulltext,
        'fulltext_coverage_percent': round(articles_with_fulltext/unique_articles*100, 1),
        'articles_by_iteration_count': {str(k): v for k, v in iteration_counts.items()},
        'iteration_breakdown': {},
    }

    # Count unique articles per iteration
    for iteration_name in COLLECTIONS.keys():
        articles_in_iteration = [pmid for pmid, sources in pmid_to_sources.items()
                                if any(s[0] == iteration_name for s in sources)]
        report['iteration_breakdown'][iteration_name] = len(articles_in_iteration)

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Deduplication report saved to: {report_file}")
    print()

    print("="*70)
    print("DEDUPLICATION COMPLETE")
    print("="*70)
    print()
    print(f"Deduplicated dataset: {OUTPUT_DIR}")
    print(f"  - {unique_articles} unique articles")
    print(f"  - {articles_with_fulltext} with full-text ({articles_with_fulltext/unique_articles*100:.1f}%)")
    print(f"  - Removed {duplicates} duplicate instances")
    print()

    return report


if __name__ == "__main__":
    deduplicate_collections()

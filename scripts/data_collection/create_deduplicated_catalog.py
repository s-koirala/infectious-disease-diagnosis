#!/usr/bin/env python3
"""
Create Comprehensive Catalog for Deduplicated Dataset

Purpose: Generate catalog of all deduplicated articles with:
- Title, DOI, publication date, journal
- PMID, PMC ID
- Authors
- Publication type
- Full-text availability
- Deduplication information (which iterations article appeared in)

Author: Claude Code
Date: 2025-11-16
"""

import os
import json
from pathlib import Path
from typing import Dict, List
import pandas as pd
from datetime import datetime

# Configuration
DEDUPLICATED_DIR = Path(r"C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\data\processed\deduplicated")
REPORT_DIR = Path(r"C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\reports")

def extract_article_metadata(json_file: Path) -> Dict:
    """Extract relevant metadata from deduplicated article JSON"""

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pmid = data.get('pmid', '')
    metadata = data.get('metadata', {})
    dedup_info = data.get('deduplication_info', {})

    # Extract PMC ID
    pmc_id = ''
    article_ids = metadata.get('articleids', [])
    for id_entry in article_ids:
        if id_entry.get('idtype') == 'pmc':
            pmc_id = id_entry.get('value', '')
            break

    # Extract DOI
    doi = ''
    for id_entry in article_ids:
        if id_entry.get('idtype') == 'doi':
            doi = id_entry.get('value', '')
            break

    # Extract authors
    authors = metadata.get('authors', [])
    if authors:
        first_author = authors[0].get('name', '') if isinstance(authors[0], dict) else str(authors[0])
        author_count = len(authors)
        authors_str = '; '.join([a.get('name', str(a)) if isinstance(a, dict) else str(a)
                                for a in authors[:5]])  # First 5 authors
        if len(authors) > 5:
            authors_str += f' ... ({len(authors)} total)'
    else:
        first_author = ''
        author_count = 0
        authors_str = ''

    # Publication types
    pub_types = metadata.get('pubtype', [])
    pub_types_str = ', '.join(pub_types) if pub_types else ''

    # Determine primary type
    if 'Meta-Analysis' in pub_types:
        primary_type = 'Meta-Analysis'
    elif 'Systematic Review' in pub_types:
        primary_type = 'Systematic Review'
    elif 'Practice Guideline' in pub_types or 'Guideline' in pub_types:
        primary_type = 'Practice Guideline'
    elif 'Review' in pub_types:
        primary_type = 'Review'
    else:
        primary_type = pub_types[0] if pub_types else 'Article'

    # Check if specific types are present
    is_review = 'Review' in pub_types
    is_meta_analysis = 'Meta-Analysis' in pub_types
    is_guideline = 'Practice Guideline' in pub_types or 'Guideline' in pub_types
    is_systematic_review = 'Systematic Review' in pub_types

    # Check for full-text
    fulltext_dir = DEDUPLICATED_DIR / 'fulltext'
    has_fulltext = False
    if pmc_id:
        fulltext_file = fulltext_dir / f"{pmc_id}.xml"
        has_fulltext = fulltext_file.exists()

    # Publication date
    pubdate = metadata.get('pubdate', '')

    # Deduplication info
    appeared_in = ', '.join(dedup_info.get('appeared_in_iterations', []))
    num_iterations = dedup_info.get('num_iterations', 1)
    is_duplicate = dedup_info.get('is_duplicate', False)

    return {
        'pmid': pmid,
        'pmc_id': pmc_id,
        'doi': doi,
        'title': metadata.get('title', '').strip(),
        'first_author': first_author,
        'authors': authors_str,
        'author_count': author_count,
        'journal': metadata.get('fulljournalname', ''),
        'publication_date': pubdate,
        'primary_type': primary_type,
        'all_publication_types': pub_types_str,
        'is_review': is_review,
        'is_meta_analysis': is_meta_analysis,
        'is_guideline': is_guideline,
        'is_systematic_review': is_systematic_review,
        'has_fulltext': has_fulltext,
        'volume': metadata.get('volume', ''),
        'issue': metadata.get('issue', ''),
        'pages': metadata.get('pages', ''),
        'appeared_in_iterations': appeared_in,
        'num_iterations': num_iterations,
        'is_duplicate': is_duplicate,
    }


def main():
    """Generate deduplicated catalog"""

    print("="*80)
    print("DEDUPLICATED ARTICLE CATALOG GENERATION")
    print("="*80)
    print()

    metadata_dir = DEDUPLICATED_DIR / 'metadata'

    if not metadata_dir.exists():
        print(f"Error: Metadata directory not found: {metadata_dir}")
        return

    # Get all metadata files
    metadata_files = list(metadata_dir.glob('*.json'))
    total_articles = len(metadata_files)

    print(f"Processing {total_articles} deduplicated articles...")
    print()

    # Extract metadata from all articles
    article_data = []

    for i, metadata_file in enumerate(metadata_files):
        try:
            data = extract_article_metadata(metadata_file)
            article_data.append(data)
        except Exception as e:
            print(f"Error processing {metadata_file}: {e}")
            continue

        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{total_articles} articles...")

    print(f"  Processed {total_articles}/{total_articles} articles...")
    print()

    # Create DataFrame
    df = pd.DataFrame(article_data)

    # Sort by publication date (most recent first)
    df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')
    df = df.sort_values('publication_date', ascending=False)

    # Statistics
    print("="*80)
    print("CATALOG STATISTICS")
    print("="*80)
    print()

    print(f"Total articles: {len(df)}")
    print(f"Articles with full-text: {df['has_fulltext'].sum()} ({df['has_fulltext'].sum()/len(df)*100:.1f}%)")
    print()

    print("Publication Type Distribution:")
    print(df['primary_type'].value_counts().head(10).to_string())
    print()

    print(f"Reviews: {df['is_review'].sum()} ({df['is_review'].sum()/len(df)*100:.1f}%)")
    print(f"Meta-Analyses: {df['is_meta_analysis'].sum()} ({df['is_meta_analysis'].sum()/len(df)*100:.1f}%)")
    print(f"Guidelines: {df['is_guideline'].sum()} ({df['is_guideline'].sum()/len(df)*100:.1f}%)")
    print(f"Systematic Reviews: {df['is_systematic_review'].sum()} ({df['is_systematic_review'].sum()/len(df)*100:.1f}%)")
    print()

    print("Deduplication Statistics:")
    print(f"Articles appearing in 1 iteration: {(df['num_iterations'] == 1).sum()}")
    print(f"Articles appearing in 2 iterations: {(df['num_iterations'] == 2).sum()}")
    print(f"Articles appearing in 3+ iterations: {(df['num_iterations'] >= 3).sum()}")
    print()

    print("Top 10 Journals by Article Count:")
    print(df['journal'].value_counts().head(10).to_string())
    print()

    # Save to CSV
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORT_DIR / 'deduplicated_catalog.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"[OK] CSV catalog saved to: {csv_path}")

    # Save to Excel with multiple sheets
    try:
        excel_path = REPORT_DIR / 'deduplicated_catalog.xlsx'

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Main catalog
            df.to_excel(writer, sheet_name='All Articles', index=False)

            # Summary sheet
            summary_df = pd.DataFrame({
                'Metric': [
                    'Total Articles',
                    'Articles with Full-Text',
                    'Full-Text Coverage %',
                    'Reviews',
                    'Meta-Analyses',
                    'Practice Guidelines',
                    'Systematic Reviews',
                    'Articles in 1 Iteration Only',
                    'Articles in 2+ Iterations',
                ],
                'Value': [
                    len(df),
                    df['has_fulltext'].sum(),
                    f"{df['has_fulltext'].sum()/len(df)*100:.1f}%",
                    df['is_review'].sum(),
                    df['is_meta_analysis'].sum(),
                    df['is_guideline'].sum(),
                    df['is_systematic_review'].sum(),
                    (df['num_iterations'] == 1).sum(),
                    (df['num_iterations'] >= 2).sum(),
                ]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # By publication type
            type_summary = df.groupby('primary_type').agg({
                'pmid': 'count',
                'has_fulltext': 'sum',
            }).rename(columns={
                'pmid': 'Total Articles',
                'has_fulltext': 'With Full-Text',
            }).sort_values('Total Articles', ascending=False)
            type_summary.to_excel(writer, sheet_name='By Publication Type')

            # By iteration appearance
            iteration_summary = df.groupby('appeared_in_iterations').agg({
                'pmid': 'count',
                'has_fulltext': 'sum',
            }).rename(columns={
                'pmid': 'Total Articles',
                'has_fulltext': 'With Full-Text',
            }).sort_values('Total Articles', ascending=False)
            iteration_summary.to_excel(writer, sheet_name='By Iteration')

        print(f"[OK] Excel catalog saved to: {excel_path}")

    except Exception as e:
        print(f"Note: Could not create Excel file: {e}")
        print("CSV file contains all the data.")

    # Create simplified version
    simplified_df = df[['pmid', 'pmc_id', 'title', 'primary_type', 'journal',
                        'publication_date', 'doi', 'has_fulltext',
                        'appeared_in_iterations', 'num_iterations']]
    simplified_csv = REPORT_DIR / 'deduplicated_catalog_simplified.csv'
    simplified_df.to_csv(simplified_csv, index=False, encoding='utf-8-sig')
    print(f"[OK] Simplified catalog saved to: {simplified_csv}")

    print()
    print("="*80)
    print("CATALOG GENERATION COMPLETE")
    print("="*80)
    print(f"\nFiles created:")
    print(f"1. {csv_path.name} - Complete catalog")
    print(f"2. {excel_path.name if 'excel_path' in locals() else 'N/A'} - Excel workbook")
    print(f"3. {simplified_csv.name} - Simplified quick reference")
    print()


if __name__ == "__main__":
    main()

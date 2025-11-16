#!/usr/bin/env python3
"""
Create comprehensive catalog of all collected clinical guideline articles.

Generates a detailed table with:
- Article metadata (title, DOI, date, journal)
- Classification (disease, category, publication type)
- Identifiers (PMID, PMC ID)
- Additional useful information
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Paths
GUIDELINES_DIR = Path("../../data/raw/clinical_guidelines")
OUTPUT_DIR = Path("../../reports")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_article_metadata(json_file: Path, disease: str, category: str) -> Dict:
    """Extract relevant metadata from article JSON file"""

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        metadata = data.get('metadata', {})

        # Extract publication date
        pubdate = metadata.get('pubdate', '')
        if not pubdate:
            # Try epubdate or other date fields
            pubdate = metadata.get('epubdate', metadata.get('printpubdate', ''))

        # Extract DOI
        doi = None
        article_ids = metadata.get('articleids', [])
        for id_entry in article_ids:
            if id_entry.get('idtype') == 'doi':
                doi = id_entry.get('value', '')
                break

        # Extract PMC ID
        pmc_id = None
        for id_entry in article_ids:
            if id_entry.get('idtype') == 'pmc':
                pmc_id = id_entry.get('value', '')
                break

        # Extract PMID
        pmid = None
        for id_entry in article_ids:
            if id_entry.get('idtype') == 'pubmed':
                pmid = id_entry.get('value', '')
                break

        # If PMID not in articleids, try uid
        if not pmid:
            pmid = metadata.get('uid', '')

        # Extract publication types
        pub_types = metadata.get('pubtype', [])
        pub_types_str = '; '.join(pub_types) if pub_types else ''

        # Categorize publication type
        is_review = 'Review' in pub_types
        is_meta_analysis = 'Meta-Analysis' in pub_types or 'Systematic Review' in pub_types
        is_guideline = 'Practice Guideline' in pub_types or 'Guideline' in pub_types
        is_case_report = 'Case Reports' in pub_types

        primary_type = 'Journal Article'
        if is_guideline:
            primary_type = 'Practice Guideline'
        elif is_meta_analysis:
            primary_type = 'Meta-Analysis/Systematic Review'
        elif is_review:
            primary_type = 'Review'
        elif is_case_report:
            primary_type = 'Case Report'

        # Extract authors
        authors = metadata.get('authors', [])
        first_author = ''
        if authors and len(authors) > 0:
            first_author_data = authors[0]
            first_author = first_author_data.get('name', '')
            if not first_author:
                # Try constructing from firstname/lastname
                lastname = first_author_data.get('lastname', '')
                firstname = first_author_data.get('firstname', '')
                if lastname or firstname:
                    first_author = f"{lastname}, {firstname}".strip(', ')

        author_count = len(authors)

        # Format authors list
        if author_count == 0:
            authors_str = ''
        elif author_count == 1:
            authors_str = first_author
        elif author_count == 2:
            second_author = authors[1].get('name', '')
            authors_str = f"{first_author}; {second_author}"
        else:
            authors_str = f"{first_author} et al. ({author_count} authors)"

        # Check if full-text available
        has_fulltext = (json_file.parent.parent / 'fulltext' / f"{pmc_id}.xml").exists() if pmc_id else False

        return {
            'pmid': pmid,
            'pmc_id': pmc_id,
            'doi': doi,
            'title': metadata.get('title', '').strip(),
            'first_author': first_author,
            'authors': authors_str,
            'author_count': author_count,
            'journal': metadata.get('fulljournalname', metadata.get('source', '')),
            'publication_date': pubdate,
            'disease': disease,
            'category': category,
            'primary_type': primary_type,
            'all_publication_types': pub_types_str,
            'is_review': is_review,
            'is_meta_analysis': is_meta_analysis,
            'is_guideline': is_guideline,
            'has_fulltext': has_fulltext,
            'volume': metadata.get('volume', ''),
            'issue': metadata.get('issue', ''),
            'pages': metadata.get('pages', ''),
        }

    except Exception as e:
        print(f"Error processing {json_file}: {e}")
        return None

def collect_all_articles() -> List[Dict]:
    """Collect metadata from all articles in the collection"""

    all_articles = []

    # Define categories and their directories
    categories = {
        'bacterial': GUIDELINES_DIR / 'bacterial',
        'viral': GUIDELINES_DIR / 'viral',
        'fungal': GUIDELINES_DIR / 'fungal',
        'parasitic': GUIDELINES_DIR / 'parasitic',
        'systemic': GUIDELINES_DIR / 'systemic',
        'custom': GUIDELINES_DIR / 'custom',
    }

    total_files = 0
    processed = 0

    # Count total files first
    for category_name, category_dir in categories.items():
        if category_dir.exists():
            for disease_dir in category_dir.iterdir():
                if disease_dir.is_dir():
                    metadata_dir = disease_dir / 'metadata'
                    if metadata_dir.exists():
                        total_files += len(list(metadata_dir.glob('*.json')))

    print(f"Processing {total_files} article metadata files...\n")

    # Process each category
    for category_name, category_dir in categories.items():
        if not category_dir.exists():
            continue

        # Process each disease in category
        for disease_dir in category_dir.iterdir():
            if not disease_dir.is_dir():
                continue

            disease = disease_dir.name
            metadata_dir = disease_dir / 'metadata'

            if not metadata_dir.exists():
                continue

            # Process each article
            for json_file in metadata_dir.glob('*.json'):
                article_data = extract_article_metadata(json_file, disease, category_name)
                if article_data:
                    all_articles.append(article_data)
                    processed += 1

                    if processed % 100 == 0:
                        print(f"Processed {processed}/{total_files} articles...")

    print(f"\nCompleted processing {processed} articles")
    return all_articles

def create_catalog():
    """Main function to create comprehensive article catalog"""

    print("="*80)
    print("CLINICAL GUIDELINES ARTICLE CATALOG GENERATOR")
    print("="*80)
    print()

    # Collect all articles
    articles = collect_all_articles()

    if not articles:
        print("No articles found!")
        return

    # Create DataFrame
    df = pd.DataFrame(articles)

    # Sort by category, disease, publication date
    df = df.sort_values(['category', 'disease', 'publication_date'],
                        ascending=[True, True, False])

    # Reorder columns for better readability
    column_order = [
        'category',
        'disease',
        'title',
        'primary_type',
        'journal',
        'publication_date',
        'first_author',
        'author_count',
        'doi',
        'pmid',
        'pmc_id',
        'has_fulltext',
        'is_review',
        'is_meta_analysis',
        'is_guideline',
        'all_publication_types',
        'authors',
        'volume',
        'issue',
        'pages',
    ]

    df = df[column_order]

    # Generate statistics
    print("\n" + "="*80)
    print("COLLECTION STATISTICS")
    print("="*80)
    print(f"\nTotal articles: {len(df)}")
    print(f"Articles with full-text: {df['has_fulltext'].sum()} ({df['has_fulltext'].sum()/len(df)*100:.1f}%)")

    print("\nBy Category:")
    print(df['category'].value_counts().to_string())

    print("\nBy Primary Type:")
    print(df['primary_type'].value_counts().to_string())

    print(f"\nReviews: {df['is_review'].sum()}")
    print(f"Meta-Analyses/Systematic Reviews: {df['is_meta_analysis'].sum()}")
    print(f"Practice Guidelines: {df['is_guideline'].sum()}")

    print("\nTop 10 Journals:")
    print(df['journal'].value_counts().head(10).to_string())

    print("\nTop 10 Diseases by Article Count:")
    print(df['disease'].value_counts().head(10).to_string())

    # Save to CSV
    csv_path = OUTPUT_DIR / 'clinical_guidelines_catalog.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"\n[OK] CSV catalog saved to: {csv_path}")

    # Save to Excel with formatting
    try:
        excel_path = OUTPUT_DIR / 'clinical_guidelines_catalog.xlsx'

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Main catalog
            df.to_excel(writer, sheet_name='All Articles', index=False)

            # Summary statistics
            summary_data = {
                'Metric': [
                    'Total Articles',
                    'Articles with Full-Text',
                    'Full-Text Coverage %',
                    'Reviews',
                    'Meta-Analyses/Systematic Reviews',
                    'Practice Guidelines',
                    'Unique Diseases',
                    'Unique Journals',
                ],
                'Value': [
                    len(df),
                    df['has_fulltext'].sum(),
                    f"{df['has_fulltext'].sum()/len(df)*100:.1f}%",
                    df['is_review'].sum(),
                    df['is_meta_analysis'].sum(),
                    df['is_guideline'].sum(),
                    df['disease'].nunique(),
                    df['journal'].nunique(),
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # By category
            category_summary = df.groupby('category').agg({
                'pmid': 'count',
                'has_fulltext': 'sum',
                'is_review': 'sum',
                'is_meta_analysis': 'sum',
                'is_guideline': 'sum',
            }).rename(columns={
                'pmid': 'Total Articles',
                'has_fulltext': 'With Full-Text',
                'is_review': 'Reviews',
                'is_meta_analysis': 'Meta-Analyses',
                'is_guideline': 'Guidelines',
            })
            category_summary.to_excel(writer, sheet_name='By Category')

            # By disease
            disease_summary = df.groupby('disease').agg({
                'pmid': 'count',
                'has_fulltext': 'sum',
                'is_review': 'sum',
                'is_meta_analysis': 'sum',
            }).rename(columns={
                'pmid': 'Total Articles',
                'has_fulltext': 'With Full-Text',
                'is_review': 'Reviews',
                'is_meta_analysis': 'Meta-Analyses',
            }).sort_values('Total Articles', ascending=False)
            disease_summary.to_excel(writer, sheet_name='By Disease')

        print(f"[OK] Excel catalog saved to: {excel_path}")

    except Exception as e:
        print(f"Note: Could not create Excel file: {e}")
        print("CSV file contains all the data.")

    # Create a simplified version for quick reference
    simplified_df = df[['category', 'disease', 'title', 'primary_type',
                        'journal', 'publication_date', 'doi', 'has_fulltext']]
    simplified_csv = OUTPUT_DIR / 'clinical_guidelines_catalog_simplified.csv'
    simplified_df.to_csv(simplified_csv, index=False, encoding='utf-8-sig')
    print(f"[OK] Simplified catalog saved to: {simplified_csv}")

    print("\n" + "="*80)
    print("CATALOG GENERATION COMPLETE")
    print("="*80)
    print(f"\nFiles created:")
    print(f"1. {csv_path.name} - Complete catalog")
    print(f"2. {excel_path.name if 'excel_path' in locals() else 'N/A'} - Excel workbook with multiple sheets")
    print(f"3. {simplified_csv.name} - Simplified quick reference")

    return df

if __name__ == "__main__":
    catalog_df = create_catalog()

#!/usr/bin/env python3
"""
Efficient StatPearls Data Extraction
Downloads full StatPearls archive and extracts infectious disease articles

Usage:
    python extract_statpearls.py --download  # Download archive (1.6GB)
    python extract_statpearls.py --extract   # Extract and process
"""

import os
import re
import json
import argparse
import tarfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm

# StatPearls FTP location
STATPEARLS_FTP = "ftp://ftp.ncbi.nlm.nih.gov/pub/litarch/statpearls_NBK430685.tar.gz"
DOWNLOAD_DIR = Path("../../data/raw/statpearls")
EXTRACT_DIR = DOWNLOAD_DIR / "extracted"
OUTPUT_DIR = DOWNLOAD_DIR / "infectious_disease"


def download_statpearls():
    """Download StatPearls archive from NCBI FTP"""
    import urllib.request

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = DOWNLOAD_DIR / "statpearls_NBK430685.tar.gz"

    if archive_path.exists():
        print(f"Archive already exists: {archive_path}")
        print(f"Size: {archive_path.stat().st_size / (1024**3):.2f} GB")
        return archive_path

    print(f"Downloading StatPearls archive from NCBI FTP...")
    print(f"Size: ~1.6 GB - this may take 5-15 minutes\n")

    def show_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded / total_size * 100, 100)
        mb_downloaded = downloaded / (1024**2)
        mb_total = total_size / (1024**2)
        print(f"\rDownloading: {percent:.1f}% ({mb_downloaded:.0f}/{mb_total:.0f} MB)", end='')

    try:
        urllib.request.urlretrieve(STATPEARLS_FTP, archive_path, show_progress)
        print(f"\n\nDownload complete: {archive_path}")
        return archive_path
    except Exception as e:
        print(f"\nError downloading: {e}")
        return None


def extract_archive(archive_path: Path):
    """Extract StatPearls archive"""
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nExtracting archive to {EXTRACT_DIR}...")

    with tarfile.open(archive_path, 'r:gz') as tar:
        members = tar.getmembers()
        for member in tqdm(members, desc="Extracting"):
            tar.extract(member, EXTRACT_DIR)

    print(f"Extraction complete!")
    return EXTRACT_DIR


def parse_statpearls_xml(xml_file: Path) -> Optional[Dict]:
    """
    Parse StatPearls XML file and extract structured clinical information

    Returns:
        Dictionary with extracted clinical data
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Extract basic metadata
        article_data = {
            'nbk_id': None,
            'title': None,
            'authors': [],
            'publication_date': None,
            'sections': {},
            'keywords': [],
            'mesh_terms': [],
            'source_file': str(xml_file)
        }

        # Get NBK ID from filename or metadata
        article_data['nbk_id'] = xml_file.stem

        # Extract title
        title_elem = root.find('.//book-title') or root.find('.//article-title')
        if title_elem is not None:
            article_data['title'] = ''.join(title_elem.itertext()).strip()

        # Extract authors
        for contrib in root.findall('.//contrib[@contrib-type="author"]'):
            name_elem = contrib.find('.//name')
            if name_elem is not None:
                surname = name_elem.find('surname')
                given_names = name_elem.find('given-names')
                if surname is not None:
                    author = surname.text or ''
                    if given_names is not None and given_names.text:
                        author = f"{given_names.text} {author}"
                    article_data['authors'].append(author.strip())

        # Extract publication date
        pub_date = root.find('.//pub-date[@pub-type="ppub"]') or root.find('.//pub-date')
        if pub_date is not None:
            year = pub_date.find('year')
            if year is not None:
                article_data['publication_date'] = year.text

        # Extract all sections with their content
        for sec in root.findall('.//sec'):
            title_elem = sec.find('title')
            if title_elem is not None:
                section_title = ''.join(title_elem.itertext()).strip()

                # Get section content (paragraphs)
                paragraphs = []
                for para in sec.findall('.//p'):
                    para_text = ''.join(para.itertext()).strip()
                    if para_text:
                        paragraphs.append(para_text)

                if paragraphs:
                    article_data['sections'][section_title] = paragraphs

        # Extract keywords
        for kwd in root.findall('.//kwd'):
            if kwd.text:
                article_data['keywords'].append(kwd.text.strip())

        # Extract MeSH terms
        for subject in root.findall('.//subj-group[@subj-group-type="heading"]//subject'):
            if subject.text:
                article_data['mesh_terms'].append(subject.text.strip())

        return article_data

    except Exception as e:
        print(f"Error parsing {xml_file}: {e}")
        return None


def is_infectious_disease_article(article_data: Dict) -> bool:
    """
    Determine if article is about infectious diseases

    Args:
        article_data: Parsed article data

    Returns:
        True if article is about infectious diseases
    """
    # Keywords to identify infectious disease content
    id_keywords = [
        'infection', 'infectious', 'bacterial', 'viral', 'fungal', 'parasitic',
        'sepsis', 'pneumonia', 'meningitis', 'tuberculosis', 'HIV', 'AIDS',
        'hepatitis', 'influenza', 'malaria', 'antibiotic', 'antimicrobial',
        'pathogen', 'microbe', 'bacteria', 'virus', 'fungus', 'parasite'
    ]

    # Check title
    title = article_data.get('title', '').lower()
    if any(keyword in title for keyword in id_keywords):
        return True

    # Check keywords and MeSH terms
    keywords = ' '.join(article_data.get('keywords', [])).lower()
    mesh_terms = ' '.join(article_data.get('mesh_terms', [])).lower()

    if any(keyword in keywords or keyword in mesh_terms for keyword in id_keywords):
        return True

    # Check section titles
    sections = article_data.get('sections', {})
    section_titles = ' '.join(sections.keys()).lower()
    if any(keyword in section_titles for keyword in id_keywords):
        return True

    return False


def extract_diagnostic_information(article_data: Dict) -> Dict:
    """
    Extract structured diagnostic information from article

    Returns:
        Dictionary with diagnostic criteria, symptoms, tests, etc.
    """
    diagnostic_info = {
        'condition': article_data.get('title', ''),
        'symptoms': [],
        'diagnostic_criteria': [],
        'differential_diagnosis': [],
        'laboratory_tests': [],
        'imaging': [],
        'treatment': []
    }

    sections = article_data.get('sections', {})

    # Map section titles to categories
    section_mappings = {
        'symptoms': ['clinical presentation', 'history and physical', 'signs and symptoms', 'clinical features'],
        'diagnostic_criteria': ['diagnosis', 'diagnostic criteria', 'evaluation'],
        'differential_diagnosis': ['differential diagnosis', 'differential diagnoses'],
        'laboratory_tests': ['laboratory', 'laboratory tests', 'lab tests', 'workup'],
        'imaging': ['imaging', 'radiology', 'radiographic'],
        'treatment': ['treatment', 'management', 'therapy', 'therapeutic']
    }

    for category, section_keywords in section_mappings.items():
        for section_title, paragraphs in sections.items():
            section_lower = section_title.lower()
            if any(keyword in section_lower for keyword in section_keywords):
                diagnostic_info[category].extend(paragraphs)

    return diagnostic_info


def process_statpearls_archive(extract_dir: Path, output_dir: Path):
    """
    Process all XML files in StatPearls archive and extract infectious disease articles
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all XML files
    xml_files = list(extract_dir.rglob("*.xml"))
    print(f"\nFound {len(xml_files)} XML files in archive")

    # Process each file
    id_articles = []

    print("\nProcessing articles...")
    for xml_file in tqdm(xml_files, desc="Parsing articles"):
        article_data = parse_statpearls_xml(xml_file)

        if article_data and is_infectious_disease_article(article_data):
            # Extract diagnostic information
            diagnostic_info = extract_diagnostic_information(article_data)
            article_data['diagnostic_info'] = diagnostic_info

            id_articles.append(article_data)

            # Save individual article
            output_file = output_dir / f"{article_data['nbk_id']}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total StatPearls articles: {len(xml_files)}")
    print(f"Infectious disease articles: {len(id_articles)}")
    print(f"Percentage: {len(id_articles)/len(xml_files)*100:.1f}%")
    print(f"Output directory: {output_dir}")

    # Save summary
    summary = {
        'total_articles': len(xml_files),
        'infectious_disease_articles': len(id_articles),
        'extraction_date': str(Path.ctime(Path.cwd())),
        'article_list': [
            {
                'nbk_id': a['nbk_id'],
                'title': a['title'],
                'authors': a['authors'][:3] if len(a['authors']) > 3 else a['authors']
            }
            for a in id_articles
        ]
    }

    summary_file = output_dir / "extraction_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Summary saved: {summary_file}")

    return id_articles


def main():
    parser = argparse.ArgumentParser(
        description="Extract infectious disease articles from StatPearls"
    )
    parser.add_argument(
        '--download',
        action='store_true',
        help='Download StatPearls archive from NCBI FTP'
    )
    parser.add_argument(
        '--extract',
        action='store_true',
        help='Extract and process downloaded archive'
    )
    parser.add_argument(
        '--archive',
        type=str,
        help='Path to existing StatPearls archive file'
    )

    args = parser.parse_args()

    if args.download:
        archive_path = download_statpearls()
        if not archive_path:
            print("Download failed!")
            return

    if args.extract:
        # Find archive
        if args.archive:
            archive_path = Path(args.archive)
        else:
            archive_path = DOWNLOAD_DIR / "statpearls_NBK430685.tar.gz"

        if not archive_path.exists():
            print(f"Archive not found: {archive_path}")
            print("Use --download to download it first")
            return

        # Extract
        extract_dir = extract_archive(archive_path)

        # Process
        process_statpearls_archive(extract_dir, OUTPUT_DIR)

    if not args.download and not args.extract:
        parser.print_help()


if __name__ == "__main__":
    main()

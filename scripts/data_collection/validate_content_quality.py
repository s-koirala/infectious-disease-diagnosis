#!/usr/bin/env python3
"""
Automated Content Quality Validation

Purpose: Perform automated validation of collected articles to ensure
         they contain relevant diagnostic content for the 5-part output structure.

Validation Checks:
1. Presence of differential diagnosis terminology
2. Presence of diagnostic testing terminology
3. Presence of clinical features/symptoms terminology
4. Section structure analysis (if full-text XML available)
5. Abstract content analysis

Output: Validation report with quality metrics and flagged articles

Author: Claude Code
Date: 2025-11-16
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import xml.etree.ElementTree as ET
import re

# Configuration
DEDUPLICATED_DIR = Path(r"C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\data\processed\deduplicated")
REPORT_DIR = Path(r"C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\reports")

# Keyword categories for content validation
VALIDATION_KEYWORDS = {
    'differential_diagnosis': [
        'differential diagnosis',
        'differential',
        'ddx',
        'differential diagnostic',
        'alternative diagnoses',
        'diagnostic considerations',
        'diagnostic possibilities',
    ],
    'diagnostic_testing': [
        'laboratory test',
        'diagnostic test',
        'laboratory diagnosis',
        'laboratory finding',
        'test result',
        'laboratory investigation',
        'diagnostic workup',
        'diagnostic evaluation',
        'sensitivity',
        'specificity',
    ],
    'clinical_features': [
        'clinical feature',
        'clinical presentation',
        'clinical manifestation',
        'signs and symptoms',
        'presenting symptom',
        'presenting sign',
        'clinical finding',
        'physical examination',
    ],
    'diagnostic_criteria': [
        'diagnostic criteria',
        'diagnostic criterion',
        'case definition',
        'clinical criteria',
        'laboratory criteria',
    ],
    'treatment_guidance': [
        'treatment',
        'management',
        'therapy',
        'antimicrobial',
        'antibiotic',
        'antiviral',
        'antifungal',
    ],
}


def validate_text_content(text: str, category: str) -> Dict:
    """Check for presence of keywords in text"""
    if not text:
        return {'found': False, 'count': 0, 'keywords_found': []}

    text_lower = text.lower()
    keywords = VALIDATION_KEYWORDS.get(category, [])

    found_keywords = []
    total_count = 0

    for keyword in keywords:
        count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text_lower))
        if count > 0:
            found_keywords.append(keyword)
            total_count += count

    return {
        'found': len(found_keywords) > 0,
        'count': total_count,
        'keywords_found': found_keywords,
    }


def extract_abstract_from_metadata(metadata_file: Path) -> str:
    """Extract abstract text from metadata JSON"""
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Try to get abstract from metadata
        metadata = data.get('metadata', {})

        # Some formats have 'abstract' field
        if 'abstract' in metadata:
            return metadata['abstract']

        # Some have it in articleids or other fields
        # Return empty if not found
        return ""

    except Exception as e:
        print(f"Error reading {metadata_file}: {e}")
        return ""


def extract_fulltext_sections(fulltext_file: Path) -> Dict[str, str]:
    """Extract section texts from full-text XML"""
    sections = {}

    try:
        tree = ET.parse(fulltext_file)
        root = tree.getroot()

        # Find all section elements
        # PMC XML structure varies, look for common patterns
        for section in root.iter():
            if section.tag.endswith('sec'):
                # Get section title
                title_elem = section.find('.//{*}title')
                title = title_elem.text if title_elem is not None else 'Untitled Section'

                # Get section text
                text_parts = []
                for elem in section.iter():
                    if elem.text and elem.tag.endswith('p'):
                        text_parts.append(elem.text)

                sections[title] = ' '.join(text_parts)

        # Also get abstract
        for abstract in root.iter():
            if abstract.tag.endswith('abstract'):
                abstract_parts = []
                for elem in abstract.iter():
                    if elem.text:
                        abstract_parts.append(elem.text)
                sections['Abstract'] = ' '.join(abstract_parts)

    except Exception as e:
        print(f"Error parsing XML {fulltext_file}: {e}")

    return sections


def validate_article(pmid: str, metadata_file: Path, fulltext_file: Path = None) -> Dict:
    """Validate a single article"""

    validation = {
        'pmid': pmid,
        'has_fulltext': fulltext_file is not None and fulltext_file.exists(),
        'abstract_validation': {},
        'fulltext_validation': {},
        'overall_score': 0,
    }

    # Validate abstract
    abstract = extract_abstract_from_metadata(metadata_file)
    if abstract:
        for category in VALIDATION_KEYWORDS.keys():
            validation['abstract_validation'][category] = validate_text_content(abstract, category)

    # Validate full-text if available
    if validation['has_fulltext']:
        sections = extract_fulltext_sections(fulltext_file)

        # Combine all section text
        fulltext = ' '.join(sections.values())

        for category in VALIDATION_KEYWORDS.keys():
            validation['fulltext_validation'][category] = validate_text_content(fulltext, category)

    # Calculate overall quality score (0-100)
    # Based on presence of key content categories
    score_components = []

    # Check abstract or fulltext (prefer fulltext if available)
    source = validation['fulltext_validation'] if validation['has_fulltext'] else validation['abstract_validation']

    if source:
        # Differential diagnosis: 30 points
        if source.get('differential_diagnosis', {}).get('found', False):
            score_components.append(30)

        # Diagnostic testing: 25 points
        if source.get('diagnostic_testing', {}).get('found', False):
            score_components.append(25)

        # Clinical features: 20 points
        if source.get('clinical_features', {}).get('found', False):
            score_components.append(20)

        # Diagnostic criteria: 15 points
        if source.get('diagnostic_criteria', {}).get('found', False):
            score_components.append(15)

        # Treatment guidance: 10 points
        if source.get('treatment_guidance', {}).get('found', False):
            score_components.append(10)

    validation['overall_score'] = sum(score_components)

    return validation


def generate_validation_report():
    """Main validation function"""

    print("="*70)
    print("AUTOMATED CONTENT QUALITY VALIDATION")
    print("="*70)
    print()

    metadata_dir = DEDUPLICATED_DIR / 'metadata'
    fulltext_dir = DEDUPLICATED_DIR / 'fulltext'

    if not metadata_dir.exists():
        print(f"Error: Metadata directory not found: {metadata_dir}")
        return

    print(f"Metadata directory: {metadata_dir}")
    print(f"Full-text directory: {fulltext_dir}")
    print()

    # Get all metadata files
    metadata_files = list(metadata_dir.glob('*.json'))
    total_articles = len(metadata_files)

    print(f"Total articles to validate: {total_articles}")
    print()

    # Sample validation (full validation would be time-consuming)
    # Validate first 100 articles as a representative sample
    sample_size = min(100, total_articles)
    print(f"Validating sample of {sample_size} articles...")
    print()

    validations = []

    for i, metadata_file in enumerate(metadata_files[:sample_size]):
        pmid = metadata_file.stem

        # Find corresponding fulltext if exists
        # Try to extract PMC ID from metadata
        fulltext_file = None
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                metadata = data.get('metadata', {})
                article_ids = metadata.get('articleids', [])

                for id_entry in article_ids:
                    if id_entry.get('idtype') == 'pmc':
                        pmc_id = id_entry.get('value', '')
                        potential_fulltext = fulltext_dir / f"{pmc_id}.xml"
                        if potential_fulltext.exists():
                            fulltext_file = potential_fulltext
                            break
        except Exception:
            pass

        validation = validate_article(pmid, metadata_file, fulltext_file)
        validations.append(validation)

        if (i + 1) % 10 == 0:
            print(f"  Validated {i + 1}/{sample_size} articles...")

    print()
    print("="*70)
    print("VALIDATION RESULTS")
    print("="*70)
    print()

    # Calculate statistics
    total_with_fulltext = sum(1 for v in validations if v['has_fulltext'])
    avg_score = sum(v['overall_score'] for v in validations) / len(validations)

    print(f"Sample size: {len(validations)} articles")
    print(f"Articles with full-text: {total_with_fulltext} ({total_with_fulltext/len(validations)*100:.1f}%)")
    print(f"Average quality score: {avg_score:.1f}/100")
    print()

    # Score distribution
    score_bins = {
        'Excellent (80-100)': 0,
        'Good (60-79)': 0,
        'Fair (40-59)': 0,
        'Poor (20-39)': 0,
        'Very Poor (0-19)': 0,
    }

    for v in validations:
        score = v['overall_score']
        if score >= 80:
            score_bins['Excellent (80-100)'] += 1
        elif score >= 60:
            score_bins['Good (60-79)'] += 1
        elif score >= 40:
            score_bins['Fair (40-59)'] += 1
        elif score >= 20:
            score_bins['Poor (20-39)'] += 1
        else:
            score_bins['Very Poor (0-19)'] += 1

    print("Quality Score Distribution:")
    for category, count in score_bins.items():
        pct = count / len(validations) * 100
        print(f"  {category}: {count} articles ({pct:.1f}%)")
    print()

    # Content category presence
    print("Content Category Presence (in sample):")

    for category in VALIDATION_KEYWORDS.keys():
        count_abstract = sum(1 for v in validations
                           if v.get('abstract_validation', {}).get(category, {}).get('found', False))
        count_fulltext = sum(1 for v in validations
                           if v.get('fulltext_validation', {}).get(category, {}).get('found', False))

        total_count = max(count_abstract, count_fulltext)  # Count if found in either
        pct = total_count / len(validations) * 100

        category_label = category.replace('_', ' ').title()
        print(f"  {category_label}: {total_count}/{len(validations)} articles ({pct:.1f}%)")
    print()

    # Identify low-quality articles
    low_quality = [v for v in validations if v['overall_score'] < 40]

    if low_quality:
        print(f"Low-quality articles (score < 40): {len(low_quality)}")
        print("Sample of low-quality PMIDs:", [v['pmid'] for v in low_quality[:5]])
        print()

    # Save validation report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORT_DIR / 'content_validation_report.json'

    report = {
        'sample_size': len(validations),
        'total_articles': total_articles,
        'articles_with_fulltext': total_with_fulltext,
        'average_quality_score': round(avg_score, 1),
        'score_distribution': score_bins,
        'category_presence': {},
        'validations': validations,
    }

    # Add category presence to report
    for category in VALIDATION_KEYWORDS.keys():
        count = sum(1 for v in validations
                   if (v.get('abstract_validation', {}).get(category, {}).get('found', False) or
                       v.get('fulltext_validation', {}).get(category, {}).get('found', False)))
        report['category_presence'][category] = {
            'count': count,
            'percentage': round(count / len(validations) * 100, 1),
        }

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Validation report saved to: {report_file}")
    print()

    print("="*70)
    print("VALIDATION COMPLETE")
    print("="*70)
    print()
    print("Summary:")
    print(f"  - {len(validations)} articles validated (sample from {total_articles} total)")
    print(f"  - Average quality score: {avg_score:.1f}/100")
    print(f"  - {score_bins['Excellent (80-100)']} articles rated Excellent")
    print(f"  - {score_bins['Good (60-79)']} articles rated Good")
    print(f"  - Content categories well-represented: {sum(1 for c in report['category_presence'].values() if c['percentage'] > 50)}/5")
    print()

    return report


if __name__ == "__main__":
    generate_validation_report()

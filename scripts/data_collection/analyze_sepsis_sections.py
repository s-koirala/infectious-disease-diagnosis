#!/usr/bin/env python3
"""Analyze section content in sepsis clinical guidelines"""

import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter

fulltext_dir = Path("../../data/raw/clinical_guidelines/custom/sepsis/fulltext")

print("SEPSIS CLINICAL GUIDELINES - Section Analysis\n")
print("="*80)

section_counter = Counter()
diagnostic_sections = []

for xml_file in fulltext_dir.glob("*.xml"):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Get article title
        title_elem = root.find('.//article-title')
        title = title_elem.text if title_elem is not None else "Unknown"

        # Get sections
        sections = [sec.text.lower() for sec in root.findall('.//sec/title') if sec.text]

        # Count sections
        for section in sections:
            section_counter[section] += 1

        # Check for diagnostic-relevant sections
        diagnostic_keywords = ['diagnosis', 'diagnostic', 'clinical presentation',
                              'clinical features', 'signs and symptoms',
                              'differential diagnosis', 'biomarkers', 'criteria']

        has_diagnostic = any(any(kw in sec for kw in diagnostic_keywords) for sec in sections)
        if has_diagnostic:
            diagnostic_sections.append((title[:70], sections))

    except Exception as e:
        continue

print(f"\nTotal articles analyzed: {len(list(fulltext_dir.glob('*.xml')))}")
print(f"Articles with diagnostic sections: {len(diagnostic_sections)}")

print("\n" + "="*80)
print("MOST COMMON SECTION TITLES (Top 20):")
print("="*80)
for section, count in section_counter.most_common(20):
    print(f"{section:<60} {count:>3}")

print("\n" + "="*80)
print("SAMPLE ARTICLES WITH DIAGNOSTIC CONTENT:")
print("="*80)
for title, sections in diagnostic_sections[:5]:
    print(f"\n{title}")
    diagnostic_secs = [s for s in sections if any(kw in s for kw in
                      ['diagnosis', 'diagnostic', 'clinical', 'biomarker', 'criteria', 'symptom', 'sign'])]
    for sec in diagnostic_secs[:5]:
        print(f"  - {sec}")

#!/usr/bin/env python3
"""Analyze collected articles to check content type"""

import json
import os
from pathlib import Path

metadata_dir = Path("../../data/raw/pubmed_pmc/metadata")

print("Sample of collected articles:\n")
print(f"{'Title':<80} {'Type':<30}")
print("=" * 110)

for i, file in enumerate(sorted(metadata_dir.glob("*.json"))[:20]):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        metadata = data.get('metadata', {})
        title = metadata.get('title', 'Unknown')[:75]
        pubtypes = metadata.get('pubtype', [])
        pubtype_str = ', '.join(pubtypes[:2]) if pubtypes else 'Unknown'

        print(f"{title:<80} {pubtype_str:<30}")

print("\n" + "=" * 110)
print("\nPublication type distribution:")

# Count publication types
type_counts = {}
for file in metadata_dir.glob("*.json"):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        metadata = data.get('metadata', {})
        pubtypes = metadata.get('pubtype', [])
        for ptype in pubtypes:
            type_counts[ptype] = type_counts.get(ptype, 0) + 1

# Sort and display
for ptype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
    print(f"{ptype:<40} {count:>5}")

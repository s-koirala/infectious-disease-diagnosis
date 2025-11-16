#!/usr/bin/env python3
"""Analyze clinical collection"""

import json
from pathlib import Path

metadata_dir = Path("../../data/raw/pubmed_pmc/infectious_disease_clinical/metadata")

print("CLINICAL COLLECTION ANALYSIS:\n")
print(f"{'Title':<75} {'Type':<35}")
print("=" * 110)

for i, file in enumerate(sorted(metadata_dir.glob("*.json"))[:15]):
    with open(file, 'r') as f:
        data = json.load(f)
        metadata = data.get('metadata', {})
        title = metadata.get('title', 'Unknown')[:70]
        pubtypes = metadata.get('pubtype', [])
        pubtype_str = ', '.join(pubtypes[:2]) if pubtypes else 'Unknown'
        print(f"{title:<75} {pubtype_str:<35}")

print("\n" + "=" * 110)
print("\nPublication type distribution:")

type_counts = {}
for file in metadata_dir.glob("*.json"):
    with open(file, 'r') as f:
        data = json.load(f)
        metadata = data.get('metadata', {})
        pubtypes = metadata.get('pubtype', [])
        for ptype in pubtypes:
            type_counts[ptype] = type_counts.get(ptype, 0) + 1

for ptype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"{ptype:<40} {count:>5}")

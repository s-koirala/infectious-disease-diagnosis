#!/usr/bin/env python3
"""Test full text download"""

import os
from dotenv import load_dotenv
from collect_pubmed_pmc import PubMedCollector

load_dotenv()

API_KEY = os.getenv('NCBI_API_KEY', '')
EMAIL = os.getenv('NCBI_EMAIL', '')

collector = PubMedCollector(api_key=API_KEY, email=EMAIL)

# Test with a known PMC ID from the collected metadata
test_pmcid = "PMC12602529"

print(f"Testing full text download for {test_pmcid}...")

full_text = collector.fetch_full_text_xml(test_pmcid)

if full_text:
    print(f"Success! Downloaded {len(full_text)} characters")
    print(f"\nFirst 500 characters:")
    print(full_text[:500])
else:
    print("Failed to download full text")

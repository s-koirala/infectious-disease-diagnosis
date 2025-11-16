#!/usr/bin/env python3
"""Test the actual query construction"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('NCBI_API_KEY', '')
EMAIL = os.getenv('NCBI_EMAIL', '')

# Test different query variations
queries = [
    # Original complex query
    ('"infectious disease" OR "bacterial infection" OR "viral infection" OR "fungal infection" OR "parasitic infection" OR "sepsis" OR "pneumonia" OR "meningitis" OR "tuberculosis" OR "HIV" OR "hepatitis" OR "influenza" AND "open access"[filter] AND ("2014"[Date - Publication] : "2025"[Date - Publication])', "Complex with filters"),

    # Simpler versions
    ('infectious disease AND "open access"[filter]', "Simple with OA filter"),
    ('infectious disease', "Just keywords"),
    ('tuberculosis AND "open access"[filter]', "TB with OA filter"),
]

url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

for query, desc in queries:
    print(f"\n{'='*60}")
    print(f"Testing: {desc}")
    print(f"Query: {query[:80]}...")

    params = {
        "db": "pubmed",
        "term": query,
        "retmax": 10,
        "retmode": "json",
        "api_key": API_KEY,
        "email": EMAIL
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        result = data.get("esearchresult", {})
        count = result.get("count", 0)
        ids = result.get("idlist", [])

        print(f"Status: OK")
        print(f"Total found: {count}")
        print(f"IDs retrieved: {len(ids)}")
    else:
        print(f"Status: ERROR {response.status_code}")

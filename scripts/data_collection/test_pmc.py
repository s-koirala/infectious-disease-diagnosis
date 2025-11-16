#!/usr/bin/env python3
"""Test PMC database and OA filters"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('NCBI_API_KEY', '')
EMAIL = os.getenv('NCBI_EMAIL', '')

# Test different databases and filters
tests = [
    # PMC database tests
    ("pmc", "tuberculosis", "PMC - simple"),
    ("pmc", "tuberculosis AND free fulltext[filter]", "PMC - free fulltext filter"),
    ("pmc", "infectious disease", "PMC - infectious disease"),

    # PubMed with different filters
    ("pubmed", "tuberculosis[Title/Abstract] AND free full text[sb]", "PubMed - free full text subset"),
    ("pubmed", "tuberculosis AND ffrft[filter]", "PubMed - ffrft filter"),
]

url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

for db, query, desc in tests:
    print(f"\n{'='*60}")
    print(f"Test: {desc}")
    print(f"Database: {db}")
    print(f"Query: {query}")

    params = {
        "db": db,
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

        print(f"Total found: {count}")
        print(f"IDs retrieved: {len(ids)}")
        if ids:
            print(f"First ID: {ids[0]}")
    else:
        print(f"ERROR {response.status_code}")

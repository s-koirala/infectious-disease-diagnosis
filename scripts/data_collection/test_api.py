#!/usr/bin/env python3
"""Quick API test"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('NCBI_API_KEY', '')
EMAIL = os.getenv('NCBI_EMAIL', '')

# Simple test query
url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
params = {
    "db": "pubmed",
    "term": "tuberculosis",
    "retmax": 10,
    "retmode": "json",
    "api_key": API_KEY,
    "email": EMAIL
}

print(f"Testing NCBI API connection...")
print(f"API Key: {API_KEY[:10]}..." if API_KEY else "No API key")
print(f"Email: {EMAIL}")
print(f"\nSearching for: tuberculosis")

response = requests.get(url, params=params)
print(f"\nResponse status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    result = data.get("esearchresult", {})
    count = result.get("count", 0)
    ids = result.get("idlist", [])

    print(f"[OK] API working!")
    print(f"Total articles found: {count}")
    print(f"Retrieved IDs: {len(ids)}")
    print(f"First few IDs: {ids[:5]}")
else:
    print(f"[ERROR] {response.text}")

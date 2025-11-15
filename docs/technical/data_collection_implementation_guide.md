# Data Collection Implementation Guide - Phase 2

**Date:** 2025-11-15
**Purpose:** Practical guide for collecting infectious disease data from open sources
**Status:** Ready for implementation

---

## Overview

This guide provides implementation details for collecting data from legally compliant open sources:
1. PubMed/PMC Open Access Subset
2. CDC infectious disease resources
3. WHO global health data

All sources listed here **allow commercial use** and provide programmatic access.

---

## 1. PubMed/PMC E-utilities API

### API Overview

**Base URL:** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

**Key Operations:**
- **ESearch:** Search for articles by topic
- **EFetch:** Retrieve full article content
- **ESummary:** Get article summaries
- **ELink:** Find related articles
- **EPost:** Upload UID lists for batch operations

### Rate Limits

**Without API Key:**
- 3 requests per second maximum
- Large jobs: weekends or 9 PM - 5 AM ET weekdays

**With API Key (Recommended):**
- 10 requests per second
- Higher rates available upon request
- Get API key: https://www.ncbi.nlm.nih.gov/account/settings/

### Implementation Example 1: Search for Infectious Disease Articles

```python
import requests
import time
import xml.etree.ElementTree as ET

# NCBI E-utilities configuration
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
API_KEY = "YOUR_API_KEY_HERE"  # Get from NCBI account
EMAIL = "your.email@example.com"  # Required for NCBI tracking

def search_pubmed(query, max_results=100):
    """
    Search PubMed for articles matching query

    Args:
        query: Search term (e.g., "infectious diseases")
        max_results: Maximum number of results to return

    Returns:
        List of PubMed IDs (PMIDs)
    """
    search_url = f"{BASE_URL}esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "api_key": API_KEY,
        "tool": "infectious_disease_cdss",
        "email": EMAIL
    }

    response = requests.get(search_url, params=params)
    response.raise_for_status()

    data = response.json()
    pmids = data["esearchresult"]["idlist"]

    print(f"Found {len(pmids)} articles for query: {query}")
    return pmids

# Example usage
infectious_disease_queries = [
    "infectious diseases[MeSH Terms] AND diagnosis[Title/Abstract]",
    "bacterial infections[MeSH Terms] AND clinical presentation",
    "viral infections[MeSH Terms] AND treatment guidelines",
    "fungal infections[MeSH Terms] AND diagnosis",
    "parasitic diseases[MeSH Terms] AND symptoms"
]

# Search for articles
for query in infectious_disease_queries:
    pmids = search_pubmed(query, max_results=1000)
    time.sleep(0.1)  # Respect rate limits
```

### Implementation Example 2: Retrieve Full-Text Articles from PMC

```python
def fetch_pmc_articles(pmc_ids):
    """
    Fetch full-text XML for PMC articles

    Args:
        pmc_ids: List of PMC IDs (e.g., ["PMC123456", "PMC789012"])

    Returns:
        Dictionary mapping PMC ID to article XML
    """
    fetch_url = f"{BASE_URL}efetch.fcgi"
    articles = {}

    # Process in batches of 100 (NCBI recommendation)
    batch_size = 100
    for i in range(0, len(pmc_ids), batch_size):
        batch = pmc_ids[i:i+batch_size]

        params = {
            "db": "pmc",
            "id": ",".join(batch),
            "rettype": "full",
            "retmode": "xml",
            "api_key": API_KEY,
            "tool": "infectious_disease_cdss",
            "email": EMAIL
        }

        response = requests.get(fetch_url, params=params)
        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.content)

        # Extract individual articles
        for article in root.findall('.//article'):
            pmc_id = article.find('.//article-id[@pub-id-type="pmc"]')
            if pmc_id is not None:
                articles[pmc_id.text] = ET.tostring(article, encoding='unicode')

        print(f"Fetched {len(batch)} articles (batch {i//batch_size + 1})")
        time.sleep(0.1)  # Respect rate limits (10/sec with API key)

    return articles

# Example usage
# pmc_ids = ["PMC123456", "PMC789012"]  # Example PMC IDs
# articles_xml = fetch_pmc_articles(pmc_ids)
```

### Implementation Example 3: Convert PubMed IDs to PMC IDs

```python
def pmid_to_pmcid(pmids):
    """
    Convert PubMed IDs to PMC IDs (for full-text access)

    Args:
        pmids: List of PubMed IDs

    Returns:
        Dictionary mapping PMID to PMC ID
    """
    converter_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"

    # Process in batches of 200
    batch_size = 200
    pmid_to_pmc = {}

    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i+batch_size]

        params = {
            "ids": ",".join(batch),
            "format": "json",
            "tool": "infectious_disease_cdss",
            "email": EMAIL
        }

        response = requests.get(converter_url, params=params)
        response.raise_for_status()

        data = response.json()

        for record in data.get("records", []):
            pmid = record.get("pmid")
            pmcid = record.get("pmcid")
            if pmid and pmcid:
                pmid_to_pmc[pmid] = pmcid

        print(f"Converted {len(batch)} PMIDs (batch {i//batch_size + 1})")
        time.sleep(0.1)

    return pmid_to_pmc

# Example usage
# pmid_to_pmc_mapping = pmid_to_pmcid(pmids)
# pmc_ids = list(pmid_to_pmc_mapping.values())
```

### Implementation Example 4: Filter for Open Access Articles

```python
def search_pmc_open_access(query, max_results=1000):
    """
    Search specifically for Open Access articles in PMC

    Args:
        query: Search term
        max_results: Maximum results

    Returns:
        List of PMC IDs with open access full text
    """
    search_url = f"{BASE_URL}esearch.fcgi"

    # Add open access filter to query
    oa_query = f"{query} AND open access[filter]"

    params = {
        "db": "pmc",
        "term": oa_query,
        "retmax": max_results,
        "retmode": "json",
        "api_key": API_KEY,
        "tool": "infectious_disease_cdss",
        "email": EMAIL
    }

    response = requests.get(search_url, params=params)
    response.raise_for_status()

    data = response.json()
    pmc_ids = data["esearchresult"]["idlist"]

    print(f"Found {len(pmc_ids)} Open Access articles for: {query}")
    return pmc_ids

# Example usage
oa_articles = search_pmc_open_access(
    "infectious diseases AND diagnosis",
    max_results=5000
)
```

### Complete Workflow Example

```python
import json
from pathlib import Path

def collect_infectious_disease_articles(output_dir="data/raw/pubmed"):
    """
    Complete workflow to collect infectious disease articles from PubMed/PMC
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Define targeted infectious disease queries
    queries = [
        "bacterial infections AND clinical presentation AND diagnosis",
        "viral infections AND symptoms AND treatment",
        "fungal infections AND diagnosis AND therapy",
        "parasitic diseases AND clinical features",
        "sepsis AND infectious diseases AND management",
        "antimicrobial resistance AND treatment guidelines",
        "tuberculosis AND diagnosis AND treatment",
        "HIV AIDS AND clinical management",
        "influenza AND diagnosis AND antiviral therapy",
        "COVID-19 AND clinical features AND treatment"
    ]

    all_pmc_ids = set()

    # Step 1: Search for Open Access articles
    print("Step 1: Searching PMC for Open Access articles...")
    for query in queries:
        pmc_ids = search_pmc_open_access(query, max_results=1000)
        all_pmc_ids.update(pmc_ids)
        time.sleep(0.1)

    print(f"\nTotal unique Open Access articles found: {len(all_pmc_ids)}")

    # Step 2: Fetch article metadata
    print("\nStep 2: Fetching article metadata...")
    pmc_ids_list = list(all_pmc_ids)

    # Step 3: Download full-text articles
    print("\nStep 3: Downloading full-text articles...")
    articles_xml = fetch_pmc_articles(pmc_ids_list)

    # Step 4: Save to files
    print("\nStep 4: Saving articles to disk...")
    for pmc_id, xml_content in articles_xml.items():
        file_path = output_path / f"{pmc_id}.xml"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)

    # Save metadata
    metadata = {
        "total_articles": len(articles_xml),
        "pmc_ids": pmc_ids_list,
        "queries_used": queries,
        "collection_date": "2025-11-15"
    }

    with open(output_path / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Collection complete: {len(articles_xml)} articles saved to {output_dir}")
    return articles_xml

# Run the complete workflow
# articles = collect_infectious_disease_articles()
```

---

## 2. CDC Data and Guidelines

### CDC APIs Overview

CDC provides multiple APIs for accessing infectious disease data:

1. **CDC WONDER API** - Query epidemiological databases
2. **CDC Open Data Portal** - data.cdc.gov (Socrata API)
3. **Content Syndication API** - tools.cdc.gov/api
4. **NNDSS** - National Notifiable Diseases Surveillance System data

### Implementation Example 1: CDC Open Data Portal (Socrata API)

```python
from sodapy import Socrata

def fetch_cdc_infectious_disease_data():
    """
    Fetch infectious disease data from CDC Open Data Portal
    """
    # Initialize Socrata client
    client = Socrata("data.cdc.gov", None)

    # Example: NNDSS - Table II - diseases by state and territory
    # Dataset ID: 7xxt-tws6 (example - verify current dataset ID)

    # Query for recent data
    results = client.get(
        "nndss-dataset-id",  # Replace with actual dataset ID
        limit=10000,
        where="disease='Tuberculosis' OR disease='HIV/AIDS'"
    )

    client.close()

    print(f"Retrieved {len(results)} records from CDC")
    return results

# Example usage
# cdc_data = fetch_cdc_infectious_disease_data()
```

### Implementation Example 2: CDC Content Syndication API

```python
def fetch_cdc_content(topic="infectious-diseases"):
    """
    Fetch CDC health content via Content Syndication API
    """
    api_base = "https://tools.cdc.gov/api/v2/"

    # Search for content
    search_url = f"{api_base}resources/media"

    params = {
        "topic": topic,
        "mediaType": "Html",
        "max": 100
    }

    response = requests.get(search_url, params=params)
    response.raise_for_status()

    data = response.json()
    articles = data.get("results", [])

    print(f"Found {len(articles)} CDC articles on {topic}")
    return articles

# Example usage
# cdc_articles = fetch_cdc_content("infectious-diseases")
```

### CDC Guidelines - Manual Collection

Many CDC clinical guidelines are published as web pages and PDFs:

**Key CDC Infectious Disease Resources:**
- Treatment guidelines: https://www.cdc.gov/treatment-guidelines/
- Disease-specific pages: https://www.cdc.gov/az/diseases.html
- Healthcare professionals resources: https://www.cdc.gov/health-professionals/

**Recommended Approach:**
1. Identify relevant guideline pages
2. Manual download of PDFs or HTML scraping (within terms of use)
3. Extract text using PDF parsing libraries or BeautifulSoup
4. Structure into knowledge base format

---

## 3. WHO Data and Guidelines

### WHO APIs Overview

1. **ICD API** - International Classification of Diseases
2. **GHO OData API** - Global Health Observatory statistics
3. **WHO Data Collections** - Various datasets

### Implementation Example 1: WHO ICD API

```python
def fetch_who_icd_data(disease_category="infectious"):
    """
    Fetch disease classification data from WHO ICD API

    Note: Requires API token from https://icd.who.int/icdapi
    """
    api_base = "https://id.who.int/icd/release/11/2024-01/mms"

    # Authentication required - get token from WHO
    token = "YOUR_WHO_ICD_TOKEN"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Language": "en",
        "API-Version": "v2"
    }

    # Search for infectious diseases category
    search_url = f"{api_base}/search"

    params = {
        "q": disease_category,
        "useFlexisearch": "true",
        "flatResults": "true"
    }

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    return data

# Note: Requires registration at https://icd.who.int/icdapi for access token
```

### Implementation Example 2: WHO GHO OData API

```python
def fetch_who_gho_data(indicator="INFECTIOUS_DISEASE"):
    """
    Fetch global health statistics from WHO GHO OData API
    """
    api_base = "https://ghoapi.azureedge.net/api/"

    # Example: Fetch data for specific indicator
    url = f"{api_base}{indicator}"

    params = {
        "$format": "json"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    return data.get("value", [])

# Example usage
# who_data = fetch_who_gho_data("INFECTIOUS_DISEASE")
```

### WHO Guidelines - Manual Collection

WHO publishes extensive infectious disease guidelines:

**Key WHO Resources:**
- Guidelines: https://www.who.int/publications/guidelines
- Disease outbreak news: https://www.who.int/emergencies/disease-outbreak-news
- Health topics: https://www.who.int/health-topics/

**Recommended Approach:**
1. Identify relevant guideline PDFs
2. Download and extract text
3. Structure into knowledge base

---

## 4. Data Processing Pipeline

### Processing Workflow

```
1. Collection → 2. Extraction → 3. Structuring → 4. Vector Embedding → 5. Knowledge Base
```

### Implementation Example: Article Processing

```python
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

def process_pmc_article(xml_content):
    """
    Extract relevant information from PMC article XML

    Returns:
        Dictionary with structured article data
    """
    root = ET.fromstring(xml_content)

    # Extract metadata
    title = root.find('.//article-title')
    abstract = root.find('.//abstract')
    body = root.find('.//body')

    # Extract sections
    sections = {}
    if body is not None:
        for sec in body.findall('.//sec'):
            sec_title = sec.find('title')
            if sec_title is not None:
                section_name = sec_title.text
                # Extract paragraphs
                paragraphs = [p.text for p in sec.findall('.//p') if p.text]
                sections[section_name] = " ".join(paragraphs)

    article_data = {
        "title": title.text if title is not None else "",
        "abstract": abstract.text if abstract is not None else "",
        "sections": sections,
        "source": "PMC",
        "full_text": ET.tostring(root, encoding='unicode', method='text')
    }

    return article_data

def extract_clinical_information(article_data):
    """
    Extract disease-specific clinical information

    Focuses on: symptoms, diagnosis, treatment, epidemiology
    """
    clinical_info = {
        "disease_name": None,
        "symptoms": [],
        "diagnosis_methods": [],
        "treatments": [],
        "epidemiology": None
    }

    # Extract from sections
    sections = article_data.get("sections", {})

    # Look for relevant sections
    for section_name, content in sections.items():
        lower_name = section_name.lower()

        if any(keyword in lower_name for keyword in ["symptom", "clinical presentation", "manifestation"]):
            clinical_info["symptoms"].append(content)

        if any(keyword in lower_name for keyword in ["diagnosis", "diagnostic"]):
            clinical_info["diagnosis_methods"].append(content)

        if any(keyword in lower_name for keyword in ["treatment", "therapy", "management"]):
            clinical_info["treatments"].append(content)

        if any(keyword in lower_name for keyword in ["epidemiology", "incidence", "prevalence"]):
            clinical_info["epidemiology"] = content

    return clinical_info
```

---

## 5. Knowledge Base Schema

### Document Structure for Vector Database

```python
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class InfectiousDiseaseDocument:
    """
    Schema for infectious disease knowledge base documents
    """
    # Unique identifier
    doc_id: str

    # Content
    disease_name: str
    content: str  # Main text content for embedding

    # Metadata
    source: str  # "PMC", "CDC", "WHO"
    source_id: str  # PMC ID, CDC dataset ID, etc.
    category: str  # "symptoms", "diagnosis", "treatment", "epidemiology"

    # Disease classification
    pathogen_type: str  # "bacteria", "virus", "fungus", "parasite"
    icd_codes: List[str]

    # Provenance
    authors: List[str]
    publication_date: datetime
    last_updated: datetime

    # Licensing
    license: str  # "CC-BY-4.0", "Public Domain", etc.
    commercial_use_allowed: bool

    # Additional metadata
    keywords: List[str]
    related_diseases: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "doc_id": self.doc_id,
            "disease_name": self.disease_name,
            "content": self.content,
            "source": self.source,
            "source_id": self.source_id,
            "category": self.category,
            "pathogen_type": self.pathogen_type,
            "icd_codes": self.icd_codes,
            "authors": self.authors,
            "publication_date": self.publication_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "license": self.license,
            "commercial_use_allowed": self.commercial_use_allowed,
            "keywords": self.keywords,
            "related_diseases": self.related_diseases
        }
```

---

## 6. Implementation Priorities

### Week 1-2: PubMed/PMC Collection

**Priority 1: Set up PubMed/PMC API access**
- Register for NCBI API key
- Implement search and fetch functions
- Test with small dataset (100 articles)

**Priority 2: Collect pilot dataset**
- 1,000 infectious disease articles
- Focus on high-impact diseases (TB, HIV, influenza, sepsis, COVID-19)
- Verify full-text availability

### Week 3-4: CDC and WHO Integration

**Priority 3: CDC data collection**
- Access CDC Open Data Portal
- Download relevant guidelines (PDF/HTML)
- Extract and structure content

**Priority 4: WHO data collection**
- Register for WHO ICD API
- Access relevant guidelines
- Extract disease classifications

### Week 5-8: Scale and Processing

**Priority 5: Scale to 10,000+ articles**
- Expand PubMed/PMC collection
- Implement parallel processing
- Monitor rate limits and errors

**Priority 6: Data processing pipeline**
- Extract clinical information
- Structure for knowledge base
- Quality control and validation

---

## 7. Development Environment Setup

### Required Python Packages

```bash
pip install requests
pip install sodapy  # For CDC Socrata API
pip install beautifulsoup4  # For HTML parsing
pip install lxml  # For XML parsing
pip install pandas  # For data manipulation
pip install tqdm  # For progress bars
```

### Environment Variables

Create `.env` file:

```
NCBI_API_KEY=your_api_key_here
NCBI_EMAIL=your.email@example.com
WHO_ICD_TOKEN=your_who_token_here
```

---

## 8. Quality Control and Validation

### Article Selection Criteria

**Include:**
- Open Access articles with commercial-use-allowed licenses
- Peer-reviewed publications
- Recent publications (prefer last 10 years)
- Clinical focus (not pure basic research)
- English language

**Exclude:**
- Restricted access articles
- Non-commercial licenses (CC-BY-NC)
- Retracted articles
- Pre-prints without peer review (unless from reputable source)

### Validation Steps

1. **License verification:** Confirm each article allows commercial use
2. **Content relevance:** Verify infectious disease focus
3. **Quality assessment:** Check journal impact factor, peer review status
4. **Deduplication:** Remove duplicate articles
5. **Medical expert review:** Sample validation by infectious disease specialists

---

## Next Steps

1. Set up development environment
2. Register for API keys (NCBI, WHO)
3. Implement PubMed/PMC collection scripts
4. Collect pilot dataset (1,000 articles)
5. Process and structure data
6. Begin knowledge base construction

---

**Document Status:** Ready for implementation
**Owner:** Data Engineering Team
**Next Review:** After pilot data collection (Week 2)

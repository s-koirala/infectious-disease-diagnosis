# StatPearls Integration Guide

**Date:** 2025-11-15
**Purpose:** Guide for integrating StatPearls content with appropriate access
**Status:** Ready for implementation

---

## Access Options for StatPearls

### Option 1: NCBI Bookshelf (Free, Non-Commercial)

**Best for:** Academic research, non-commercial development, testing

**Access Methods:**

**A. FTP Bulk Download**
```bash
# Download entire StatPearls book (~1.6GB compressed)
wget ftp://ftp.ncbi.nlm.nih.gov/pub/litarch/statpearls_NBK430685.tar.gz

# Extract
tar -xzf statpearls_NBK430685.tar.gz

# Location contains XML files for all articles
```

**B. E-utilities API** (Individual Articles)
```python
import requests
import time

# NCBI E-utilities configuration
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
API_KEY = "YOUR_NCBI_API_KEY"
EMAIL = "your.email@example.com"

def search_statpearls(query, max_results=100):
    """
    Search StatPearls via NCBI Books database
    """
    search_url = f"{BASE_URL}esearch.fcgi"

    # Search in books database, filter for StatPearls
    params = {
        "db": "books",
        "term": f"{query} AND statpearls[book]",
        "retmax": max_results,
        "retmode": "json",
        "api_key": API_KEY,
        "tool": "infectious_disease_cdss",
        "email": EMAIL
    }

    response = requests.get(search_url, params=params)
    response.raise_for_status()

    data = response.json()
    uids = data["esearchresult"]["idlist"]

    print(f"Found {len(uids)} StatPearls articles for: {query}")
    return uids

def fetch_statpearls_article(nbk_id):
    """
    Fetch full text of StatPearls article by NBK ID

    Args:
        nbk_id: NBK identifier (e.g., "NBK430685")
    """
    fetch_url = f"{BASE_URL}efetch.fcgi"

    params = {
        "db": "books",
        "id": nbk_id,
        "rettype": "full",
        "retmode": "xml",
        "api_key": API_KEY,
        "tool": "infectious_disease_cdss",
        "email": EMAIL
    }

    response = requests.get(fetch_url, params=params)
    response.raise_for_status()

    return response.content

# Example usage
infectious_disease_queries = [
    "bacterial infections AND diagnosis",
    "viral infections AND treatment",
    "tuberculosis",
    "HIV",
    "sepsis"
]

for query in infectious_disease_queries:
    nbk_ids = search_statpearls(query, max_results=50)
    time.sleep(0.1)  # Respect rate limits
```

**License:** CC BY-NC-ND 4.0
- ✅ Use for: Academic research, testing, non-commercial development
- ✗ Restriction: Commercial use without separate agreement
- ✓ Solution: Contact StatPearls for commercial license if needed for production

---

### Option 2: Institutional Access

**Best for:** If you have university/hospital affiliation with StatPearls subscription

**Check Your Access:**
1. Visit: https://www.statpearls.com/
2. Log in through your institution
3. Check terms of your institutional license

**If you have institutional access:**
```python
# You may be able to access via institutional proxy or VPN
# Check with your institution's library about:
# - API access for research purposes
# - Bulk download permissions
# - Commercial use restrictions

# Institutional licenses vary - VERIFY YOUR SPECIFIC TERMS
```

**Action Required:**
- Contact your institution's library/IT
- Ask about API access or bulk download for research
- Clarify commercial use permissions
- Get written confirmation of allowed uses

---

### Option 3: Commercial License from StatPearls

**Best for:** Commercial clinical decision support system (production use)

**Contact StatPearls:**
- Use the email template in: `docs/business/licensing_outreach_templates.md`
- Request commercial licensing
- Negotiate API access and pricing

**Expected:**
- Licensing fee: $10K-$100K+/year (estimated)
- API access or structured data export
- Regular content updates
- Commercial use rights

---

## Implementation: FTP Bulk Download Method

### Step 1: Download StatPearls Archive

```bash
#!/bin/bash
# download_statpearls.sh

# Create data directory
mkdir -p "C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\data\raw\statpearls"

cd "C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\data\raw\statpearls"

# Download StatPearls archive
echo "Downloading StatPearls archive (1.6GB)..."
wget ftp://ftp.ncbi.nlm.nih.gov/pub/litarch/statpearls_NBK430685.tar.gz

# Extract
echo "Extracting archive..."
tar -xzf statpearls_NBK430685.tar.gz

# Download file list for reference
wget ftp://ftp.ncbi.nlm.nih.gov/pub/litarch/file_list.csv

echo "Download complete. StatPearls XML files available."
```

### Step 2: Parse StatPearls XML Files

```python
import xml.etree.ElementTree as ET
import os
from pathlib import Path
import json

def parse_statpearls_xml(xml_file):
    """
    Parse a StatPearls XML file and extract structured information

    Args:
        xml_file: Path to StatPearls XML file

    Returns:
        Dictionary with structured article data
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Extract article metadata
    article_data = {
        "nbk_id": None,
        "title": None,
        "authors": [],
        "abstract": None,
        "sections": {},
        "keywords": [],
        "last_updated": None
    }

    # Extract NBK ID
    nbk_elem = root.find('.//book-part-id[@book-part-id-type="NBK"]')
    if nbk_elem is not None:
        article_data["nbk_id"] = nbk_elem.text

    # Extract title
    title_elem = root.find('.//title-group/title')
    if title_elem is not None:
        article_data["title"] = title_elem.text

    # Extract authors
    for contrib in root.findall('.//contrib[@contrib-type="author"]'):
        name_elem = contrib.find('.//name')
        if name_elem is not None:
            surname = name_elem.find('surname')
            given_names = name_elem.find('given-names')
            if surname is not None and given_names is not None:
                author = f"{given_names.text} {surname.text}"
                article_data["authors"].append(author)

    # Extract abstract
    abstract_elem = root.find('.//abstract')
    if abstract_elem is not None:
        abstract_text = []
        for p in abstract_elem.findall('.//p'):
            if p.text:
                abstract_text.append(p.text)
        article_data["abstract"] = " ".join(abstract_text)

    # Extract body sections
    body = root.find('.//body')
    if body is not None:
        for sec in body.findall('.//sec'):
            title_elem = sec.find('title')
            if title_elem is not None and title_elem.text:
                section_title = title_elem.text

                # Extract section content
                section_paragraphs = []
                for p in sec.findall('.//p'):
                    p_text = ET.tostring(p, encoding='unicode', method='text')
                    section_paragraphs.append(p_text.strip())

                article_data["sections"][section_title] = " ".join(section_paragraphs)

    # Extract keywords
    for kwd in root.findall('.//kwd'):
        if kwd.text:
            article_data["keywords"].append(kwd.text)

    # Extract last updated date
    pub_date = root.find('.//pub-date')
    if pub_date is not None:
        year = pub_date.find('year')
        month = pub_date.find('month')
        day = pub_date.find('day')
        if year is not None:
            date_str = year.text
            if month is not None:
                date_str = f"{year.text}-{month.text.zfill(2)}"
            if day is not None:
                date_str = f"{date_str}-{day.text.zfill(2)}"
            article_data["last_updated"] = date_str

    return article_data

def extract_clinical_information(article_data):
    """
    Extract infectious disease-specific clinical information
    """
    clinical_info = {
        "disease_name": article_data.get("title"),
        "nbk_id": article_data.get("nbk_id"),
        "etiology": None,
        "epidemiology": None,
        "pathophysiology": None,
        "history_and_physical": None,
        "evaluation": None,
        "treatment": None,
        "differential_diagnosis": None,
        "prognosis": None,
        "complications": None
    }

    sections = article_data.get("sections", {})

    # Map section titles to clinical categories
    section_mapping = {
        "Etiology": "etiology",
        "Epidemiology": "epidemiology",
        "Pathophysiology": "pathophysiology",
        "History and Physical": "history_and_physical",
        "Evaluation": "evaluation",
        "Treatment / Management": "treatment",
        "Differential Diagnosis": "differential_diagnosis",
        "Prognosis": "prognosis",
        "Complications": "complications"
    }

    for section_title, content in sections.items():
        for key, value in section_mapping.items():
            if key.lower() in section_title.lower():
                clinical_info[value] = content
                break

    return clinical_info

def process_statpearls_directory(statpearls_dir, output_dir):
    """
    Process all StatPearls XML files in a directory

    Args:
        statpearls_dir: Directory containing StatPearls XML files
        output_dir: Directory to save processed JSON files
    """
    statpearls_path = Path(statpearls_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    xml_files = list(statpearls_path.glob("**/*.xml"))

    print(f"Found {len(xml_files)} XML files to process")

    processed_count = 0
    infectious_disease_articles = []

    # Keywords to identify infectious disease articles
    id_keywords = [
        "infection", "infectious", "bacteria", "bacterial", "virus", "viral",
        "fungal", "fungus", "parasite", "parasitic", "sepsis", "tuberculosis",
        "hiv", "aids", "influenza", "pneumonia", "meningitis", "hepatitis",
        "antimicrobial", "antibiotic", "antiviral"
    ]

    for xml_file in xml_files:
        try:
            article_data = parse_statpearls_xml(xml_file)

            # Check if article is about infectious diseases
            title = article_data.get("title", "").lower()
            keywords = [k.lower() for k in article_data.get("keywords", [])]
            abstract = article_data.get("abstract", "").lower()

            is_infectious_disease = any(
                keyword in title or
                keyword in abstract or
                any(keyword in kw for kw in keywords)
                for keyword in id_keywords
            )

            if is_infectious_disease:
                clinical_info = extract_clinical_information(article_data)

                # Save as JSON
                nbk_id = article_data.get("nbk_id", f"unknown_{processed_count}")
                output_file = output_path / f"{nbk_id}.json"

                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "metadata": article_data,
                        "clinical_information": clinical_info,
                        "source": "StatPearls",
                        "license": "CC-BY-NC-ND-4.0"
                    }, f, indent=2)

                infectious_disease_articles.append(nbk_id)
                processed_count += 1

                if processed_count % 100 == 0:
                    print(f"Processed {processed_count} infectious disease articles...")

        except Exception as e:
            print(f"Error processing {xml_file}: {e}")
            continue

    # Save index of all infectious disease articles
    index_file = output_path / "article_index.json"
    with open(index_file, 'w') as f:
        json.dump({
            "total_articles": processed_count,
            "article_ids": infectious_disease_articles,
            "extraction_date": "2025-11-15",
            "source": "StatPearls via NCBI Bookshelf",
            "license": "CC-BY-NC-ND-4.0"
        }, f, indent=2)

    print(f"\n✓ Processing complete!")
    print(f"  Total infectious disease articles: {processed_count}")
    print(f"  Output directory: {output_dir}")
    print(f"  Index file: {index_file}")

    return infectious_disease_articles

# Example usage
if __name__ == "__main__":
    statpearls_dir = "C:/Users/skoir/Documents/SKIE Enterprises/Infectious_Disease_Diagnosis/data/raw/statpearls"
    output_dir = "C:/Users/skoir/Documents/SKIE Enterprises/Infectious_Disease_Diagnosis/data/processed/statpearls"

    articles = process_statpearls_directory(statpearls_dir, output_dir)
```

### Step 3: Integration with Knowledge Base

```python
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class StatPearlsDocument:
    """
    Knowledge base document from StatPearls
    """
    doc_id: str  # NBK ID
    disease_name: str
    content: str  # For embedding

    # Clinical sections
    etiology: str
    epidemiology: str
    pathophysiology: str
    clinical_presentation: str
    evaluation: str
    treatment: str
    differential_diagnosis: str

    # Metadata
    authors: List[str]
    keywords: List[str]
    last_updated: str

    # Source and licensing
    source: str = "StatPearls"
    license: str = "CC-BY-NC-ND-4.0"
    commercial_use_allowed: bool = False  # Set to True if you have commercial license

    def to_knowledge_base_format(self) -> Dict:
        """
        Convert to format for vector database
        """
        # Combine all clinical content for embedding
        content_parts = []

        if self.etiology:
            content_parts.append(f"Etiology: {self.etiology}")
        if self.epidemiology:
            content_parts.append(f"Epidemiology: {self.epidemiology}")
        if self.pathophysiology:
            content_parts.append(f"Pathophysiology: {self.pathophysiology}")
        if self.clinical_presentation:
            content_parts.append(f"Clinical Presentation: {self.clinical_presentation}")
        if self.evaluation:
            content_parts.append(f"Evaluation: {self.evaluation}")
        if self.treatment:
            content_parts.append(f"Treatment: {self.treatment}")
        if self.differential_diagnosis:
            content_parts.append(f"Differential Diagnosis: {self.differential_diagnosis}")

        full_content = "\n\n".join(content_parts)

        return {
            "doc_id": f"statpearls_{self.doc_id}",
            "disease_name": self.disease_name,
            "content": full_content,
            "source": self.source,
            "source_id": self.doc_id,
            "category": "clinical_summary",
            "license": self.license,
            "commercial_use_allowed": self.commercial_use_allowed,
            "authors": self.authors,
            "keywords": self.keywords,
            "last_updated": self.last_updated
        }
```

---

## Important Legal Considerations

### ⚠️ Before Using StatPearls in Production

**Check Your Access Type:**

1. **NCBI Bookshelf (Free Access):**
   - License: CC BY-NC-ND 4.0
   - ✅ Allowed: Research, testing, non-commercial development
   - ✗ Not Allowed: Commercial deployment without license
   - **Action:** Use for development/testing, but get commercial license before production

2. **Institutional Access:**
   - License: Varies by institution
   - **Action Required:** Check your institution's license terms
   - Confirm commercial use is allowed
   - Get written permission if needed

3. **Commercial License:**
   - **Action Required:** Contact StatPearls Publishing
   - Negotiate terms and pricing
   - Get formal agreement
   - **Then:** Set `commercial_use_allowed: True` in code

### License Compliance Checklist

- [ ] Determined access method (NCBI, institutional, or commercial)
- [ ] Reviewed license terms for your access method
- [ ] Confirmed commercial use permissions (if deploying commercially)
- [ ] Documented license terms in code comments
- [ ] Set `commercial_use_allowed` flag appropriately
- [ ] Included proper attribution in application
- [ ] Consulted legal counsel if uncertain

---

## Recommended Approach

### For Development/Testing (Now)
```python
# Use NCBI Bookshelf access
commercial_use_allowed = False  # CC BY-NC-ND 4.0

# Download and process StatPearls
# Use for development and testing
# Build and validate system functionality
```

### For Production (Later)
```python
# Option A: Get commercial license from StatPearls
commercial_use_allowed = True  # With commercial license

# Option B: Use only open sources (PubMed/PMC, CDC, WHO)
# Don't include StatPearls in production
```

---

## Integration Priority

### Phase 2 (Current): Development
1. Download StatPearls via NCBI FTP
2. Process and extract infectious disease articles
3. Use for development and system validation
4. **Mark clearly as non-commercial license**

### Phase 3-4: Model Development
1. Include StatPearls in training/testing
2. Evaluate value vs. open sources
3. Determine if commercial license ROI is justified

### Phase 5-6: Production
1. If keeping StatPearls: Secure commercial license
2. If too expensive: Remove from production, use open sources only
3. Update `commercial_use_allowed` flag accordingly

---

## Next Steps

**If you have legitimate access to StatPearls:**

1. **Clarify your access type:**
   - Institutional subscription?
   - Personal account?
   - Commercial license already?

2. **Download StatPearls:**
   - Use FTP method above (recommended)
   - Or use E-utilities API for specific articles

3. **Process the data:**
   - Run the Python scripts above
   - Extract infectious disease articles
   - Structure for knowledge base

4. **Verify license compliance:**
   - Check if commercial use is allowed
   - Get written confirmation if needed
   - Document in project

5. **Integrate with existing data collection:**
   - Combine with PubMed/PMC, CDC, WHO
   - Create unified knowledge base
   - Mark license status for each source

---

**Would you like me to help you implement the StatPearls integration based on your specific access method?**

Let me know:
1. What type of access you have (institutional, NCBI, or other)
2. Whether it allows commercial use
3. If you want to start downloading and processing the data now

# Data Collection Scripts

This directory contains scripts for collecting infectious disease data from open-access sources.

## Quick Start

### 1. Install Dependencies

```bash
cd "C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\scripts\data_collection"
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional but Recommended)

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your NCBI API key:
```
NCBI_API_KEY=your_key_here
NCBI_EMAIL=your_email@example.com
```

**Get your free NCBI API key:**
1. Create an account at: https://www.ncbi.nlm.nih.gov/account/
2. Go to Settings: https://www.ncbi.nlm.nih.gov/account/settings/
3. Click "Create an API Key"
4. Copy the key to your `.env` file

**Why use an API key?**
- Without key: 3 requests/second (slower)
- With key: 10 requests/second (faster)
- Higher limits available upon request

### 3. Run Pilot Collection

Collect 100 infectious disease articles for testing:

```bash
python collect_pubmed_pmc.py --pilot
```

This will:
- Search PubMed/PMC for infectious disease articles
- Collect metadata for 100 articles
- Download full-text XML for articles in PMC Open Access Subset
- Save results to `../../data/raw/pubmed_pmc/`

### 4. Run Full Collection

Collect larger dataset (e.g., 1000 articles):

```bash
python collect_pubmed_pmc.py --max-results 1000
```

## Collection Strategy Evolution

**See [DATA_COLLECTION_STRATEGY.md](../../DATA_COLLECTION_STRATEGY.md) for complete strategy documentation.**

### Iteration 1: Disease-Specific Collection (COMPLETED)
- Focus: Individual diseases (sepsis, TB, pneumonia, etc.)
- Results: 3,090 articles collected, 2,444 full-text
- Scripts: `collect_clinical_guidelines.py`

### Iteration 2: Symptom-Based Collection (COMPLETED)
- Focus: Clinical presentations and symptoms (fever, rash, headache, etc.)
- Rationale: Aligns with clinical workflow (symptoms → diagnosis)
- Results: 1,757 metadata, 1,039 full-text (59.1% coverage)
- Scripts: `collect_symptom_based_guidelines.py`

### Iteration 3: MeSH-Optimized Collection (CURRENT)
- Focus: Use NCBI MeSH controlled vocabulary for better retrieval
- Rationale: Address low-yield keywords from Iteration 2
- Target: Vector-borne, zoonotic, fungal, respiratory, opportunistic, STD, CNS, tropical
- Scripts: `collect_mesh_optimized_guidelines.py` **← Recommended**

---

## Scripts Overview

### `collect_mesh_optimized_guidelines.py` ⭐ **RECOMMENDED - Third Iteration**

**MeSH-optimized clinical guidelines collection** - Uses standardized medical terminology.

**Purpose:** Address low-yield keywords from Iteration 2 using NCBI's MeSH controlled vocabulary.

**MeSH Categories (8 terms):**
- Vector Borne Diseases
- Zoonoses
- Invasive Fungal Infections
- Respiratory Tract Infections
- Opportunistic Infections
- Sexually Transmitted Diseases
- Central Nervous System Infections
- Tropical Medicine

**Filters:** English, Humans, Reviews/Guidelines/Meta-analyses, Last 20 years

**Usage:**
```bash
# Run MeSH-optimized collection (~800 articles)
python collect_mesh_optimized_guidelines.py
```

**Output:** `data/raw/mesh_optimized_guidelines/`

---

### `collect_symptom_based_guidelines.py` - Second Iteration (COMPLETED)

**Symptom-based clinical guidelines collection** - Aligns with actual clinical workflow.

**Purpose:** Collect articles focused on differential diagnosis from symptom presentations.

**Keywords:**
- Symptoms: fever, rash, headache, nausea, vomiting, diarrhea
- Conditions: sepsis, pneumonia, meningitis, encephalitis, HIV/AIDS, TB, UTI, etc.

**Filters:**
- English language only
- Human studies only
- Reviews, Guidelines, Meta-analyses, Systematic Reviews
- Last 20 years (2005-2025)

**Usage:**
```bash
# Run complete symptom-based collection (~2,200 articles)
python collect_symptom_based_guidelines.py
```

**Output:** `data/raw/symptom_based_guidelines/`

---

### `collect_clinical_guidelines.py`

Disease-specific clinical guidelines collection (Iteration 1 - already completed).

**Usage:**
```bash
# List all 52 diseases
python collect_clinical_guidelines.py --list-diseases

# Collect all diseases (52 × 50 articles)
python collect_clinical_guidelines.py --disease all --max 50

# Collect specific category
python collect_clinical_guidelines.py --disease bacterial --max 100

# Collect specific disease
python collect_clinical_guidelines.py --disease sepsis --max 200
```

**Output:** `data/raw/clinical_guidelines/`

---

### `collect_pubmed_pmc.py`

General PubMed/PMC collection script (baseline/initial implementation).

**Features:**
- Searches for infectious disease articles
- Filters for Open Access articles with commercial-use-allowed licenses
- Retrieves metadata (authors, title, abstract, publication info)
- Downloads full-text XML for PMC articles
- Implements proper rate limiting (respects NCBI guidelines)
- Saves structured data for processing

**Usage:**

```bash
# Pilot collection (100 articles)
python collect_pubmed_pmc.py --pilot

# Custom number of articles
python collect_pubmed_pmc.py --max-results 500

# Custom output directory
python collect_pubmed_pmc.py --max-results 1000 --output /path/to/output

# Custom search query
python collect_pubmed_pmc.py --query "tuberculosis diagnosis" --max-results 200
```

**Output Structure:**
```
data/raw/pubmed_pmc/
├── metadata/              # Article metadata (JSON)
│   ├── article_12345678.json
│   ├── article_12345679.json
│   └── ...
├── fulltext/              # Full-text XML files
│   ├── PMC1234567.xml
│   ├── PMC1234568.xml
│   └── ...
└── collection_summary.json  # Collection statistics
```

**Article Metadata Format:**
```json
{
  "pmid": "12345678",
  "pmcid": "PMC1234567",
  "metadata": {
    "title": "Article Title",
    "authors": [...],
    "pubdate": "2024",
    ...
  },
  "collected_date": "2025-11-15T..."
}
```

## Data Sources

### PubMed/PMC Open Access Subset

**What it is:**
- Millions of biomedical research articles
- Open Access subset: full-text available with reuse-friendly licenses
- Many articles allow commercial use (CC-BY, CC0, etc.)

**API Documentation:**
- E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- PMC OAI: https://www.ncbi.nlm.nih.gov/pmc/tools/oai/

**Search Strategy:**
The script searches for articles matching infectious disease terms:
- Infectious disease, bacterial/viral/fungal/parasitic infections
- Specific conditions: sepsis, pneumonia, meningitis, TB, HIV, etc.
- Filtered to Open Access articles (2014-2025)

**License Compliance:**
- All collected articles from PMC OA Subset
- Individual article licenses should be checked
- Most use CC-BY (allows commercial use with attribution)
- Script collects license information in metadata

## Rate Limiting and Best Practices

### NCBI Guidelines

**Rate Limits:**
- Without API key: Maximum 3 requests/second
- With API key: Maximum 10 requests/second
- Large jobs: Run on weekends or 9 PM - 5 AM ET weekdays

**This script:**
- Implements automatic rate limiting
- Respects NCBI terms of service
- Uses proper API parameters

### Avoiding Blocks

1. **Always use an API key** for larger collections
2. **Provide your email** in the `.env` file (NCBI requirement)
3. **Don't run multiple instances** simultaneously
4. **Be patient** - large collections take time

## Troubleshooting

### "No API key found" Warning

**Solution:** Add your NCBI API key to `.env` file
- Get key: https://www.ncbi.nlm.nih.gov/account/settings/
- Add to `.env`: `NCBI_API_KEY=your_key_here`

### "No articles found"

**Possible causes:**
- Query too restrictive
- Network connection issue
- NCBI API temporarily unavailable

**Solution:** Try simpler query or check NCBI status

### Slow Collection Speed

**Causes:**
- No API key (limited to 3 req/sec)
- Network latency
- NCBI server load

**Solution:**
- Add API key for faster rate (10 req/sec)
- Run during off-peak hours
- Be patient - this is normal for large datasets

### Full Text Not Available

**This is normal:**
- Not all PubMed articles have PMC full text
- Only PMC Open Access Subset has full text
- Script collects metadata for all, full text when available

**What the script does:**
- Saves metadata for all articles found
- Downloads full text XML only when PMC ID available
- Reports counts in collection summary

## Additional Scripts

### `extract_statpearls.py`

StatPearls FTP extraction (awaiting commercial license).

**Usage:**
```bash
# Download StatPearls archive (~1.6GB)
python extract_statpearls.py --download

# Extract infectious disease articles
python extract_statpearls.py --extract
```

**Status:** Deferred pending license acquisition

---

### `create_article_catalog.py`

Generate comprehensive catalog of all collected articles.

**Usage:**
```bash
python create_article_catalog.py
```

**Output:** `reports/clinical_guidelines_catalog.csv`

Creates detailed spreadsheet with:
- Title, DOI, journal, publication date
- Disease, category, publication type
- PMIDs, PMC IDs, authors
- Full-text availability

---

## Output Structure Alignment

The **symptom-based collection** directly supports the 5-part clinical output:

1. **Most probable differential diagnosis** - Articles with ranked differentials
2. **Less common but important DD** - "Can't miss" diagnoses from reviews
3. **Less common/rare DD** - Comprehensive differential lists
4. **Lab tests for highest probability DD** - Diagnostic workup recommendations
5. **Clarifying questions** - Clinical features that narrow differential

---

## Next Steps

After collecting symptom-based data (Iteration 2):

1. **Validate Content:** Sample articles to verify differential diagnosis focus
2. **Process Articles:** Extract structured diagnostic information from XML
3. **Integrate Collections:** Combine Iteration 1 + 2, remove duplicates
4. **Structure Knowledge Base:** Dual indexing (by symptom + by disease)
5. **Extract Training Data:** Symptom → Disease mappings for ML model
6. **Build Vector Database:** Create embeddings for RAG system

See [DATA_COLLECTION_STRATEGY.md](../../DATA_COLLECTION_STRATEGY.md) for complete strategy.

## Data Collection Checklist

- [ ] Install Python dependencies (`requirements.txt`)
- [ ] Register for NCBI API key
- [ ] Configure `.env` file with API key and email
- [ ] Run pilot collection (100 articles)
- [ ] Verify data quality and relevance
- [ ] Run full collection (1,000+ articles)
- [ ] Process collected data
- [ ] Begin CDC data collection (future)
- [ ] Begin WHO data collection (future)

## Legal Compliance

**License Status:**
- ✅ PubMed/PMC Open Access: Commercial use allowed for most articles
- ✅ CDC data: Public domain (U.S. Government)
- ✅ WHO data: Many publications allow reuse
- ❌ StatPearls: Requires commercial license (deferred)
- ❌ Medscape: Requires commercial license (deferred)

**Attribution Requirements:**
- Respect individual article licenses (CC-BY, etc.)
- Provide proper attribution for all sources
- Check license metadata for each article

**See:** [data_source_legal_assessment.md](../../docs/research/data_source_legal_assessment.md) for full legal analysis.

---

**Last Updated:** 2025-11-15
**Current Status:** Iteration 3 - MeSH-Optimized Collection Ready

**Completed:**
- Iteration 1: 3,090 metadata, 2,444 full-text (disease-specific)
- Iteration 2: 1,757 metadata, 1,039 full-text (symptom-based)
- **Total: 4,847 metadata, 3,483 full-text articles**

**Next Steps:**
1. Run MeSH-optimized collection: `python collect_mesh_optimized_guidelines.py`
2. Validate content quality across all iterations
3. Integrate collections and remove duplicates
4. Begin data processing and knowledge extraction

**Future Iterations:**
- Iteration 4: Diagnostic testing focus (deferred)
- Iteration 5: Additional symptoms and syndrome patterns

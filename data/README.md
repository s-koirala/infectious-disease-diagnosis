# Data Directory

This directory stores all collected and processed data for the infectious disease diagnosis project.

## Directory Structure

```
data/
├── raw/                      # Raw data collected from sources
│   ├── pubmed_pmc/          # PubMed/PMC articles
│   │   ├── metadata/        # Article metadata (JSON)
│   │   ├── fulltext/        # Full-text XML files
│   │   └── collection_summary.json
│   ├── cdc/                 # CDC guidelines and data (future)
│   └── who/                 # WHO international data (future)
│
├── processed/               # Processed and structured data
│   ├── clinical_summaries/ # Extracted clinical information
│   ├── embeddings/         # Vector embeddings for RAG
│   └── training_data/      # ML model training datasets
│
└── knowledge_base/          # Structured knowledge base for RAG
    ├── articles/           # Processed articles in KB format
    ├── guidelines/         # Clinical guidelines
    └── index/              # Vector database indices

```

## Data Collection Status

### Completed
- ✅ Scripts created for PubMed/PMC collection
- ✅ Python environment set up

### In Progress
- 🔄 Register for NCBI API key
- 🔄 Run pilot data collection (100 articles)

### Pending
- ⏳ Full PubMed/PMC collection (1,000+ articles)
- ⏳ CDC data collection
- ⏳ WHO data collection
- ⏳ Data processing and structuring

## Git Ignore

The `data/` directory is excluded from Git (see `.gitignore`) because:
- Large file sizes (XML, embeddings)
- Frequently updated during collection
- Regenerable from source APIs

**What IS tracked:**
- Data collection scripts
- Processing pipeline code
- Collection summaries and metadata schemas

**What is NOT tracked:**
- Raw article files (XML, JSON)
- Processed embeddings
- Vector database files
- Large CSV/parquet training datasets

## Data Sources and Licenses

### PubMed/PMC Open Access Subset
- **License:** Various (mostly CC-BY, CC0)
- **Commercial use:** ✅ Allowed for OA subset
- **Attribution:** Required per individual article license
- **Source:** https://www.ncbi.nlm.nih.gov/pmc/

### CDC (Future)
- **License:** Public domain (U.S. Government work)
- **Commercial use:** ✅ Allowed
- **Attribution:** Not required but recommended
- **Source:** https://www.cdc.gov/

### WHO (Future)
- **License:** Varies by publication
- **Commercial use:** ✅ Often allowed
- **Attribution:** Required
- **Source:** https://www.who.int/

### StatPearls (Deferred)
- **License:** CC BY-NC-ND 4.0 (via NCBI)
- **Commercial use:** ❌ Prohibited without license
- **Status:** Deferred pending license clarification
- **Source:** https://www.ncbi.nlm.nih.gov/books/NBK430685/

## Usage

### Collecting Data

See [scripts/data_collection/README.md](../scripts/data_collection/README.md) for data collection instructions.

Quick start:
```bash
cd scripts/data_collection
python collect_pubmed_pmc.py --pilot
```

### Processing Data

Processing scripts will be added in Phase 2-3:
- Extract clinical information from XML
- Structure for knowledge base
- Generate embeddings for RAG
- Prepare ML training datasets

## Data Retention

- **Raw data:** Keep indefinitely (source of truth)
- **Processed data:** Regenerable, can be deleted if storage limited
- **Backup:** Recommended for raw data (especially if collection took significant time)

## Privacy and Compliance

- **No patient data:** All data is published medical literature and public health information
- **HIPAA:** Not applicable (no PHI collected)
- **IRB:** Not required (publicly available data)
- **Attribution:** Maintain proper attribution for all sources per license terms

---

**Last Updated:** 2025-11-15
**Status:** Directory structure created, ready for data collection

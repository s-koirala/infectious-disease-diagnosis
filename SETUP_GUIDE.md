# Setup Guide - Phase 2 Data Collection

Quick start guide for setting up the data collection environment.

## Prerequisites

- ✅ Python 3.9+ installed
- ✅ Git installed
- ✅ GitHub CLI installed (for repo management)
- ✅ Internet connection

## Step 1: Register for NCBI API Key (5 minutes)

An NCBI API key is **strongly recommended** for faster data collection.

1. **Create NCBI Account:**
   - Go to: https://www.ncbi.nlm.nih.gov/account/
   - Click "Register for an NCBI Account"
   - Fill in registration form
   - Verify your email

2. **Generate API Key:**
   - Log in to your NCBI account
   - Go to: https://www.ncbi.nlm.nih.gov/account/settings/
   - Scroll to "API Key Management"
   - Click "Create an API Key"
   - Copy the generated key (you'll need it in Step 3)

3. **Save API Key:**
   - Keep your API key secure
   - You'll add it to your `.env` file in the next step

**Benefits:**
- Without API key: 3 requests/second
- With API key: 10 requests/second (3x faster!)

## Step 2: Configure Environment (2 minutes)

1. **Navigate to scripts directory:**
   ```bash
   cd "C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\scripts\data_collection"
   ```

2. **Copy environment template:**
   ```bash
   copy .env.example .env
   ```

3. **Edit `.env` file:**
   - Open `.env` in your text editor
   - Replace `your_api_key_here` with your actual NCBI API key
   - Replace `your_email@example.com` with your email
   - Save the file

   Example:
   ```
   NCBI_API_KEY=a1b2c3d4e5f6g7h8i9j0
   NCBI_EMAIL=your.email@example.com
   REQUESTS_PER_SECOND=10
   ```

## Step 3: Verify Installation (1 minute)

Dependencies should already be installed. Verify:

```bash
cd "C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\scripts\data_collection"
python -c "import requests, pandas, tqdm; print('✓ All dependencies installed')"
```

If you see an error, reinstall:
```bash
pip install -r requirements.txt
```

## Step 4: Run Pilot Collection (5-10 minutes)

Test the collection system with 100 articles:

```bash
python collect_pubmed_pmc.py --pilot
```

**What this does:**
- Searches PubMed/PMC for infectious disease articles
- Collects metadata for 100 articles
- Downloads full-text XML when available
- Saves to `../../data/raw/pubmed_pmc/`
- Creates collection summary

**Expected output:**
```
============================================================
PILOT DATASET COLLECTION
============================================================

Query: "infectious disease" OR "bacterial infection"...

Searching PubMed...
Found 125847 articles matching query
Retrieved 100 IDs

Collecting metadata for 100 articles...
Converting PMIDs to PMC IDs...
Found 67 articles with PMC full text available

Collecting articles: 100%|████████████| 100/100 [02:45<00:00]

============================================================
COLLECTION COMPLETE
============================================================
Metadata collected: 100
Full text collected: 67
```

**Troubleshooting:**
- If you see "No API key found" warning, check your `.env` file
- If collection is very slow, verify API key is correct
- If no articles found, check your internet connection

## Step 5: Verify Collected Data (1 minute)

Check the output directory:

```bash
cd "C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\data\raw\pubmed_pmc"
dir /b
```

You should see:
```
metadata/
fulltext/
collection_summary.json
```

**Inspect summary:**
```bash
type collection_summary.json
```

Should show collection statistics:
```json
{
  "query": "...",
  "total_found": 100,
  "metadata_collected": 100,
  "fulltext_collected": 67,
  "collection_date": "2025-11-15T...",
  "output_directory": "..."
}
```

## Step 6: Full Collection (Optional, 30-60 minutes)

Once pilot collection succeeds, run full collection for 1,000 articles:

```bash
cd "C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\scripts\data_collection"
python collect_pubmed_pmc.py --max-results 1000
```

**Estimated time:**
- With API key (10 req/sec): ~30-45 minutes
- Without API key (3 req/sec): ~60-90 minutes

**Storage requirements:**
- Metadata: ~50 KB per article (50 MB for 1,000)
- Full text XML: ~100 KB per article (100 MB for 1,000)
- Total: ~150 MB for 1,000 articles

## Next Steps After Collection

1. **Validate Data Quality:**
   - Review sample articles
   - Check license information
   - Verify relevance to infectious diseases

2. **Process Data:**
   - Extract clinical information from XML
   - Structure for knowledge base format
   - Generate embeddings for RAG

3. **CDC and WHO Collection:**
   - Create collection scripts for CDC data
   - Create collection scripts for WHO data
   - Integrate with knowledge base

4. **Knowledge Base Construction:**
   - Combine all sources
   - Create vector database
   - Prepare for RAG system

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'requests'"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "No API key found" warning
**Solution:** Add API key to `.env` file (see Step 2)

### Issue: Collection is very slow
**Solutions:**
- Add API key for 3x speed increase
- Run during off-peak hours (weekends, 9 PM - 5 AM ET)
- Reduce `--max-results` for testing

### Issue: "No articles found"
**Solutions:**
- Check internet connection
- Verify NCBI API is accessible: https://www.ncbi.nlm.nih.gov/
- Try simpler query: `python collect_pubmed_pmc.py --query "infection" --max-results 10`

### Issue: Not all articles have full text
**This is expected:**
- Only PMC Open Access Subset has full text
- Typically 60-70% of PubMed articles have PMC full text
- Metadata is collected for all articles

### Issue: Rate limiting errors
**Solutions:**
- Ensure you're using API key correctly
- Check REQUESTS_PER_SECOND in `.env` (should be 10 with key, 3 without)
- Don't run multiple collection scripts simultaneously

## Getting Help

1. **Check documentation:**
   - [scripts/data_collection/README.md](scripts/data_collection/README.md)
   - [docs/technical/data_collection_implementation_guide.md](docs/technical/data_collection_implementation_guide.md)

2. **NCBI Documentation:**
   - E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/
   - PMC API: https://www.ncbi.nlm.nih.gov/pmc/tools/developers/

3. **Project Documentation:**
   - Phase 2 Summary: [PHASE_2_SESSION_SUMMARY.md](PHASE_2_SESSION_SUMMARY.md)
   - Legal Assessment: [docs/research/data_source_legal_assessment.md](docs/research/data_source_legal_assessment.md)

## Quick Reference

**Pilot collection (100 articles):**
```bash
cd "C:\Users\skoir\Documents\SKIE Enterprises\Infectious_Disease_Diagnosis\scripts\data_collection"
python collect_pubmed_pmc.py --pilot
```

**Full collection (1,000 articles):**
```bash
python collect_pubmed_pmc.py --max-results 1000
```

**Custom query:**
```bash
python collect_pubmed_pmc.py --query "tuberculosis diagnosis" --max-results 200
```

**Check collected data:**
```bash
cd "../../data/raw/pubmed_pmc"
type collection_summary.json
```

---

**Estimated Total Setup Time:** 15-20 minutes
**Ready to collect:** After completing Steps 1-5
**Support:** See project documentation or NCBI API documentation

**Status:** ✅ Environment ready for data collection

# Data Collection Strategy - Evolution and Refinement

**Date:** 2025-11-15
**Status:** Second Iteration - Symptom-Based Collection

---

## Executive Summary

This document tracks the evolution of our data collection strategy from disease-specific to **symptom-based** queries, aligning with the actual clinical diagnostic workflow.

**Key Insight:** Clinicians start with **symptoms**, not diagnoses. Our collection strategy must reflect this reality.

---

## Iteration 1: Disease-Specific Collection

### Approach
- Query by specific diseases (sepsis, tuberculosis, pneumonia, etc.)
- 52 infectious diseases across 5 categories
- Focus on clinical guidelines and reviews

### Results
- **Total articles:** 3,090 metadata, 2,444 full-text (79.1% coverage)
- **Quality:** 81.5% reviews, 8.2% meta-analyses, 2.6% practice guidelines
- **Coverage:** All major infectious diseases represented

### What Worked
✅ High-quality clinical content (reviews, guidelines)
✅ Good full-text coverage (79-81%)
✅ Comprehensive disease coverage (52 diseases)
✅ Reliable data source (PubMed/PMC)

### Limitations Identified
❌ **Mismatch with clinical workflow** - Doctors don't start with a known disease
❌ **Difficult to map symptoms → diseases** - Collection organized by diagnosis, not presentation
❌ **Limited differential diagnosis content** - Focused on single diseases, not differential thinking
❌ **Missing clinical presentation emphasis** - Not optimized for symptom-driven queries

---

## Iteration 2: Symptom-Based Collection (COMPLETED)

### Strategic Pivot

**From:** Disease-specific queries (e.g., "sepsis diagnosis")
**To:** Symptom and presentation queries (e.g., "fever differential diagnosis")

**Rationale:**
1. **Aligns with clinical workflow** - Physicians present with symptoms first
2. **Supports differential diagnosis** - Articles explicitly discuss multiple possibilities
3. **Better for ML training** - Symptoms → diagnoses mapping is the actual prediction task
4. **Enhances LLM responses** - Chatbot can reason from symptoms to differential

### New Query Strategy

#### Keywords - Symptoms (6 core presentations)
- Fever
- Rash
- Headache
- Nausea or vomiting
- Diarrhea
- (Additional symptoms can be added iteratively)

#### Keywords - High-Priority Conditions (16 conditions)
- Sepsis or septic shock
- Pneumonia
- Endocarditis
- Encephalitis
- Meningitis
- Hepatitis
- HIV or AIDS
- Tuberculosis
- Systemic fungal infection
- Upper respiratory tract infection
- Urinary tract infection
- Vector borne infection
- Zoonotic infection

#### Diagnostic Focus Terms (Always Included)
- Differential diagnosis
- Diagnostic approach
- Clinical features
- Diagnostic criteria
- Laboratory diagnosis
- Diagnostic workup

### Enhanced Filters

```
Base Query Structure:
("[symptom/condition]"[Title/Abstract])
AND
("differential diagnosis" OR "diagnostic approach" OR "diagnostic criteria" OR "clinical features" OR "diagnosis")
AND
(Review[PT] OR Practice Guideline[PT] OR Guideline[PT] OR Meta-Analysis[PT] OR Systematic Review[PT])
AND
ffrft[filter]
AND
English[Language]
AND
Humans[MeSH Terms]
AND
("2005"[PDAT] : "2025"[PDAT])
```

**New Filters:**
- ✅ **English[Language]** - English-only articles (ensures usability)
- ✅ **Humans[MeSH Terms]** - Human studies only (excludes animal/in-vitro research)
- ✅ **Last 20 years** - 2005-2025 (ensures current evidence, expanded from 10 years)

---

## Output Structure Alignment

The symptom-based collection directly supports the 5-part output structure:

### 1. Most Probable Differential Diagnosis
**Data needed:** Articles ranking likelihood of diseases given symptoms
**Query support:** "differential diagnosis" + symptom keywords captures this content

### 2. Less Common but Important DD
**Data needed:** Articles discussing "can't miss" diagnoses
**Query support:** Reviews often include serious/emergent differential considerations

### 3. Less Common/Rare DD
**Data needed:** Comprehensive differential diagnosis lists
**Query support:** Systematic reviews provide exhaustive differentials

### 4. Lab Tests for Highest Probability DD
**Data needed:** Diagnostic workup recommendations
**Query support:** "diagnostic approach" + "laboratory diagnosis" captures test recommendations

### 5. Clarifying Questions
**Data needed:** Clinical features that narrow differential
**Query support:** "clinical features" + "diagnostic criteria" provides discriminating characteristics

---

## Collection Comparison

| Aspect | Iteration 1 (Disease) | Iteration 2 (Symptom) |
|--------|----------------------|----------------------|
| **Query Focus** | Specific diseases | Symptoms + presentations |
| **Keywords** | 52 diseases | 6 symptoms + 16 conditions = 22 total |
| **Date Range** | 2014-2025 (10 years) | 2005-2025 (20 years) |
| **Language Filter** | None | English only |
| **Species Filter** | None | Humans only |
| **Workflow Alignment** | Diagnosis → details | **Symptoms → diagnosis** ✓ |
| **Differential Focus** | Limited | **Explicit** ✓ |
| **ML Training** | Harder to map | **Direct mapping** ✓ |
| **Expected Articles** | ~3,000 | ~2,200 (22 keywords × 100) |

---

## Expected Outcomes - Iteration 2

### Quantity
- **22 keywords** × **100 articles each** = **~2,200 articles**
- Expected full-text coverage: **75-80%** = **~1,650-1,750 full-text**

### Quality Improvements
- ✅ **Higher differential diagnosis content** - Explicit focus in queries
- ✅ **More clinically actionable** - Symptom-driven approach matches workflow
- ✅ **Better for ML training** - Direct symptoms → diseases mapping
- ✅ **English-only, human studies** - Higher quality, more relevant
- ✅ **Longer timeframe** - More comprehensive evidence base (20 years vs 10)

### Knowledge Base Structure

**Iteration 1:** Disease → [Articles about that disease]
**Iteration 2:** Symptom → [Differential diagnosis articles] → Multiple diseases

**Advantage:** Iteration 2 naturally captures the diagnostic reasoning process

---

## Implementation Plan

### Phase 1: Symptom-Based Collection (Next)
1. Execute `collect_symptom_based_guidelines.py`
2. Collect ~2,200 symptom-based articles
3. Create catalog and validate content quality

### Phase 2: Integration
1. Combine Iteration 1 (disease-specific) + Iteration 2 (symptom-based)
2. Remove duplicates (same articles may appear in both)
3. Create unified knowledge base with dual indexing:
   - Index by symptom (for differential diagnosis)
   - Index by disease (for disease-specific details)

### Phase 3: Knowledge Extraction
1. Extract structured data from articles:
   - Symptom → Disease associations
   - Diagnostic criteria
   - Laboratory test recommendations
   - Clinical features for differentiation
2. Build training dataset for ML model
3. Populate vector database for RAG system

---

## Iterative Refinement Process

**Iteration 2 Results:**
- 21 keywords processed
- 1,757 metadata, 1,039 full-text (59.1% coverage)
- High-yield keywords: septic shock (76), TB (69), HIV (68), sepsis (65)
- Low-yield keywords: vector borne (1), systemic fungal (3), zoonotic (15), upper respiratory (18)

---

## Iteration 3: MeSH-Optimized Collection (COMPLETED)

### Strategic Response to Low Yields

**Problem identified:** Free-text queries like "vector borne infection" don't match standard medical terminology used in PubMed indexing.

**Solution:** Use NCBI's MeSH (Medical Subject Headings) controlled vocabulary.

### MeSH Strategy

**What is MeSH:**
- Standardized medical terminology maintained by NCBI
- All PubMed articles indexed with MeSH terms
- Hierarchical structure (tree) of medical concepts
- Queries using MeSH terms = higher precision retrieval

**Query Optimization:**
```
Before (Iteration 2): "vector borne infection"[Title/Abstract] → 1 article
After (Iteration 3):  "Vector Borne Diseases"[MeSH Major Topic] → Expected 50-100 articles
```

### MeSH Categories (8 terms)

Replacing and expanding low-yield categories:

**1. Vector Borne Diseases** (MeSH: D018562)
- Replaces: "vector borne infection" (1 article)
- Includes: Malaria, Dengue, Lyme Disease, West Nile Fever, Zika

**2. Zoonoses** (MeSH: D015047)
- Replaces: "zoonotic infection" (15 articles)
- Includes: Rabies, Brucellosis, Q Fever, Tularemia, Anthrax

**3. Invasive Fungal Infections** (MeSH: D000072742)
- Replaces: "systemic fungal infection" (3 articles)
- Includes: Candidemia, Invasive Aspergillosis, Mucormycosis

**4. Respiratory Tract Infections** (MeSH: D012141)
- Replaces: "upper respiratory tract infection" (18 articles)
- Includes: Pharyngitis, Sinusitis, Bronchitis, CAP

**5. Opportunistic Infections** (MeSH: D009894)
- New category
- Includes: CMV, PCP, Toxoplasmosis in immunocompromised

**6. Sexually Transmitted Diseases** (MeSH: D012749)
- New category
- Includes: Gonorrhea, Chlamydia, Syphilis, Genital Herpes

**7. Central Nervous System Infections** (MeSH: D020969)
- New category
- Includes: Meningitis, Encephalitis, Brain Abscess

**8. Tropical Medicine** (MeSH: D014326)
- New category
- Includes: Malaria, Leishmaniasis, Schistosomiasis, Trypanosomiasis

### Actual Results

**Quantity:**
- 8 MeSH categories, 200 articles max per category
- 1,214 metadata articles collected
- 730 full-text articles (60.1% coverage)

**Category Breakdown:**
- Vector Borne Diseases: 200 metadata, 136 full-text
- Respiratory Tract Infections: 200 metadata, 137 full-text
- Sexually Transmitted Diseases: 200 metadata, 145 full-text
- Central Nervous System Infections: 200 metadata, 106 full-text
- Opportunistic Infections: 154 metadata, 70 full-text
- Invasive Fungal Infections: 143 metadata, 75 full-text
- Zoonoses: 93 metadata, 45 full-text
- Tropical Medicine: 24 metadata, 16 full-text

**MeSH Strategy Success:**
- Vector borne: 1 article (Iteration 2) → 136 full-text (136x improvement)
- Systemic fungal: 3 articles → 75 full-text (25x improvement)
- Zoonoses: 15 articles → 45 full-text (3x improvement)
- Upper respiratory: 18 articles → 137 full-text (7.6x improvement)

### Implementation

**Script:** `collect_mesh_optimized_guidelines.py`

**Query structure:**
```
("[MeSH Term]"[MeSH Major Topic])
AND
("differential diagnosis" OR "diagnostic approach" OR "clinical features" OR "diagnosis")
AND
(Review[PT] OR Practice Guideline[PT] OR Meta-Analysis[PT] OR Systematic Review[PT])
AND
ffrft[filter]
AND
English[Language]
AND
Humans[MeSH Terms]
AND
("2005"[PDAT] : "2025"[PDAT])
```

---

## Future Iterations

This is the **third iteration**, but likely not the last. Future iterations may:

### Potential Iteration 4 - Diagnostic Testing Focus
- Laboratory diagnosis strategies
- Diagnostic testing recommendations
- Serologic diagnosis
- Microbiologic diagnosis
- Culture and sensitivity
- Rapid diagnostic tests
- Test interpretation

### Potential Iteration 5
- Add more symptom keywords based on ID frequency
- Include specific syndrome patterns (e.g., "fever and rash")
- Geographic/travel-related queries (e.g., "returning traveler fever")
- Age-specific queries (pediatric vs geriatric ID)
- Specialty-specific (ICU, emergency department)
- Procedure-related (post-surgical infections)

### Quality Feedback Loop
1. Collect articles
2. **Validate content** - Does it support the 5-part output?
3. Identify gaps
4. Refine queries
5. Repeat

**Key principle:** The knowledge base is **iterative and evolving**, not a one-time collection.

---

## Success Metrics

### Iteration 2 Success Criteria

**Quantitative:**
- ✅ Collect ≥2,000 articles
- ✅ Achieve ≥75% full-text coverage
- ✅ Maintain ≥80% reviews/meta-analyses/guidelines

**Qualitative:**
- ✅ Articles explicitly discuss differential diagnosis
- ✅ Content maps symptoms → multiple diseases
- ✅ Laboratory/diagnostic workup recommendations present
- ✅ Clinical features for differentiation included

**Functional:**
- ✅ Supports 3-tier differential diagnosis output
- ✅ Enables lab test recommendation extraction
- ✅ Provides basis for clarifying questions
- ✅ Supplies literature references for all recommendations

---

## Conclusion

**Iteration 1 (Disease-Specific):**
- Established baseline collection (3,090 articles)
- Validated data source and quality
- Provided disease-specific depth

**Iteration 2 (Symptom-Based):**
- Aligns with clinical workflow (symptoms → diagnosis)
- Explicitly captures differential diagnosis reasoning
- Better supports the 5-part output structure
- Enhances ML training data (direct symptom → disease mapping)

**Combined Strategy:**
- Use **Iteration 2** as primary knowledge base for differential diagnosis
- Use **Iteration 1** as supplementary disease-specific reference
- Integrate both for comprehensive coverage

**The knowledge base is a living resource** that will evolve based on:
- Clinical validation feedback
- Model performance
- Identified gaps
- User needs

This iterative approach ensures the system continuously improves and remains aligned with clinical reality.

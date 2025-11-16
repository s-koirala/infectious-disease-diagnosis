# Iteration 4: Diagnostic Testing Collection Strategy

**Date:** 2025-11-16
**Purpose:** Collect literature on laboratory and diagnostic testing for infectious diseases
**Approach:** MeSH-optimized queries focusing on diagnostic methodologies and test interpretation

---

## ARUP Lab Analysis

ARUP Laboratories (https://www.aruplab.com/infectious-disease) is a leading reference laboratory for infectious disease testing. Their test catalog reveals key diagnostic categories:

**Testing Modalities:**
- Molecular diagnostics (PCR, NGS, NAAT)
- Serologic testing
- Culture and susceptibility testing
- Microscopy and staining
- Antigen detection
- Viral load monitoring
- Genotyping and resistance testing

**Disease Categories Covered:**
- Viral infections (COVID-19, influenza, HIV, hepatitis, measles, monkeypox, Zika)
- Bacterial infections (TB, fastidious organisms, Chlamydia)
- Fungal infections (Candida auris, general mycology)
- Parasitic infections (GI parasites, microsporidia)
- Sexually transmitted infections (HPV, genital ulcer disease, vaginitis)
- Vector-borne diseases (tickborne infections)
- Gastrointestinal pathogens

---

## MeSH Term Research for Diagnostic Testing

### Core Diagnostic MeSH Terms

**1. Microbiological Techniques** (MeSH: D008829)
- Broad category covering all microbiological diagnostic methods
- Sub-terms: Bacterial typing, culture techniques, virology techniques

**2. Molecular Diagnostic Techniques** (MeSH: D025202)
- PCR, sequencing, nucleic acid amplification
- Sub-terms: Real-time PCR, multiplex PCR, next-generation sequencing

**3. Serologic Tests** (MeSH: D012698)
- Antibody detection, antigen detection
- Sub-terms: ELISA, immunofluorescence, agglutination tests

**4. Bacterial Diagnostic Tests** (MeSH: D001431)
- Culture methods, gram staining, identification
- Sub-terms: Blood culture, urine culture, wound culture

**5. Virological Techniques** (MeSH: D014773)
- Viral culture, viral load, viral typing
- Sub-terms: Viral isolation, viral antigen detection

**6. Mycological Typing Techniques** (MeSH: D025301)
- Fungal culture, susceptibility testing, identification

**7. Parasitology Techniques** (MeSH: D010271)
- Microscopy, molecular detection, antigen tests

**8. Antimicrobial Susceptibility Testing** (MeSH: D008826)
- Antibiotic resistance testing, MIC determination
- Critical for treatment guidance

**9. Point-of-Care Testing** (MeSH: D019095)
- Rapid diagnostic tests, bedside testing
- Increasingly important in ID diagnosis

**10. Clinical Laboratory Techniques** (MeSH: D019411)
- General laboratory diagnostic methods
- Broad coverage of clinical testing

---

## Proposed MeSH Categories for Iteration 4

### Category 1: Molecular Diagnostics
**MeSH Term:** "Molecular Diagnostic Techniques"[MeSH Major Topic]
**Rationale:** PCR, NGS, and NAAT are foundational for modern ID diagnosis
**Expected Content:** Guidelines on molecular test selection, interpretation, validation
**Specific Tests:** PCR panels, multiplex assays, sequencing for resistance

### Category 2: Serologic Testing
**MeSH Term:** "Serologic Tests"[MeSH Major Topic]
**Rationale:** Antibody/antigen detection critical for many IDs
**Expected Content:** Test interpretation, timing, limitations, false positives/negatives
**Specific Tests:** ELISA, IFA, rapid antigen tests, Western blot

### Category 3: Blood Culture and Bacteremia
**MeSH Term:** "Blood Culture"[MeSH Terms]
**Rationale:** Essential for sepsis, endocarditis, bacteremia diagnosis
**Expected Content:** Collection techniques, interpretation, contamination vs true infection
**Clinical Relevance:** High-priority for sepsis patients

### Category 4: Antimicrobial Resistance Testing
**MeSH Term:** "Microbial Sensitivity Tests"[MeSH Major Topic]
**Rationale:** Critical for antibiotic stewardship and treatment selection
**Expected Content:** Susceptibility patterns, resistance mechanisms, MIC interpretation
**Clinical Impact:** Directly guides antibiotic selection

### Category 5: Viral Load Monitoring
**MeSH Term:** "Viral Load"[MeSH Terms]
**Rationale:** Essential for HIV, hepatitis C, CMV management
**Expected Content:** When to test, interpretation, treatment response monitoring
**Diseases:** HIV, HCV, HBV, CMV, EBV

### Category 6: Tuberculosis Diagnostic Tests
**MeSH Term:** "Tuberculosis"[MeSH] AND "Diagnostic Techniques and Procedures"[MeSH]
**Rationale:** TB diagnosis is complex (smear, culture, NAAT, IGRA)
**Expected Content:** Test selection algorithm, latent vs active, resistance testing
**Special Focus:** Interferon-gamma release assays (IGRA), GeneXpert

### Category 7: Fungal Diagnostic Tests
**MeSH Term:** "Mycoses"[MeSH] AND "Diagnostic Techniques and Procedures"[MeSH]
**Rationale:** Fungal diagnosis requires specialized tests (galactomannan, beta-D-glucan)
**Expected Content:** Biomarker testing, culture, antifungal susceptibility
**Diseases:** Aspergillosis, candidemia, cryptococcosis, mucormycosis

### Category 8: Rapid Diagnostic Tests
**MeSH Term:** "Point-of-Care Testing"[MeSH Major Topic]
**Rationale:** Rapid tests increasingly used in clinical decision-making
**Expected Content:** Performance characteristics, appropriate use, limitations
**Examples:** Malaria RDTs, strep throat, influenza, COVID-19

### Category 9: Cerebrospinal Fluid Analysis
**MeSH Term:** "Cerebrospinal Fluid"[MeSH] AND "Diagnostic Techniques"[MeSH]
**Rationale:** Critical for CNS infection diagnosis (meningitis, encephalitis)
**Expected Content:** Cell count interpretation, protein/glucose, PCR panels
**Clinical Scenarios:** Bacterial vs viral meningitis differentiation

### Category 10: Gastrointestinal Pathogen Testing
**MeSH Term:** "Gastrointestinal Diseases"[MeSH] AND "Molecular Diagnostic Techniques"[MeSH]
**Rationale:** GI PCR panels have transformed diarrhea workup
**Expected Content:** When to order, interpretation, pathogen significance
**Tests:** Stool culture, ova and parasites, multiplex PCR panels

### Category 11: Sexually Transmitted Infection Testing
**MeSH Term:** "Sexually Transmitted Diseases"[MeSH] AND "Diagnostic Techniques"[MeSH]
**Rationale:** STI testing algorithms are evidence-based
**Expected Content:** Screening vs diagnostic testing, NAAT vs culture, partner testing
**Diseases:** Gonorrhea, chlamydia, syphilis, HIV, HSV, HPV

### Category 12: Biomarkers for Infection
**MeSH Term:** "Biomarkers"[MeSH] AND "Bacterial Infections"[MeSH]
**Rationale:** Procalcitonin, CRP, presepsin used to guide diagnosis
**Expected Content:** When to use, interpretation, limitations, antibiotic stewardship
**Clinical Use:** Sepsis diagnosis, viral vs bacterial differentiation

---

## Query Structure for Iteration 4

```
Base Query Template:
("[Diagnostic MeSH Term]"[MeSH Major Topic] OR "[Disease MeSH]"[MeSH] AND "Diagnostic Techniques"[MeSH])
AND
("laboratory diagnosis" OR "diagnostic test" OR "test interpretation" OR "diagnostic accuracy" OR "sensitivity and specificity")
AND
(Review[PT] OR Practice Guideline[PT] OR Meta-Analysis[PT] OR Systematic Review[PT] OR Guideline[PT])
AND
ffrft[filter]
AND
English[Language]
AND
Humans[MeSH Terms]
AND
("2005"[PDAT] : "2025"[PDAT])
```

**Diagnostic-Specific Terms:**
- Laboratory diagnosis
- Diagnostic test
- Test interpretation
- Diagnostic accuracy
- Sensitivity and specificity
- Positive predictive value
- Negative predictive value
- Test performance
- Diagnostic algorithm
- Testing strategy

---

## Expected Outcomes

**Quantity:**
- 12 diagnostic testing categories
- 100-200 articles per category
- Expected total: 1,200-2,400 articles
- Expected full-text: 800-1,600 (60-70% coverage)

**Quality:**
- Focus on test interpretation and diagnostic algorithms
- Evidence-based testing strategies
- Performance characteristics (sensitivity, specificity, PPV, NPV)
- Guidelines on when to order tests
- Cost-effectiveness and appropriate use

**Clinical Utility:**
- Directly supports Output #4: "Lab tests for DD with highest probability"
- Provides interpretation guidance for test results
- Helps differentiate between diagnoses based on test results
- Supports antibiotic stewardship with appropriate testing

---

## Integration with Previous Iterations

**Complementary Coverage:**
- Iteration 1: Disease-specific information
- Iteration 2: Symptom-based differential diagnosis
- Iteration 3: Specialized disease categories (vector-borne, CNS, STDs, etc.)
- **Iteration 4:** Diagnostic testing to confirm/exclude diagnoses

**Clinical Workflow Alignment:**
1. Patient presents with symptoms (Iteration 2)
2. Differential diagnosis generated (Iterations 1, 2, 3)
3. **Appropriate tests ordered (Iteration 4)** ← New addition
4. Results interpreted to refine diagnosis (Iteration 4)
5. Treatment initiated based on confirmed diagnosis

---

## Alternative Keywords (Non-MeSH)

If MeSH yields are insufficient, consider these free-text alternatives:

**Test Methodologies:**
- "polymerase chain reaction" OR "PCR"
- "nucleic acid amplification test" OR "NAAT"
- "enzyme-linked immunosorbent assay" OR "ELISA"
- "blood culture"
- "rapid diagnostic test"
- "interferon-gamma release assay" OR "IGRA"
- "next-generation sequencing" OR "NGS"
- "multiplex PCR panel"

**Biomarkers:**
- "procalcitonin"
- "C-reactive protein" OR "CRP"
- "beta-D-glucan"
- "galactomannan"
- "cryptococcal antigen"

**Specific Tests:**
- "GeneXpert MTB/RIF"
- "FilmArray"
- "BioFire"
- "QuantiFERON"
- "T-SPOT"

---

## Validation Questions

Before proceeding with Iteration 4, consider:

1. **Scope:** Should we include imaging (CT, MRI) or focus purely on laboratory tests?
2. **Specificity:** Should we target specific test platforms (e.g., FilmArray, BioFire) or keep it general?
3. **Clinical Context:** Should we include pre-test probability and Bayesian interpretation?
4. **Turnaround Time:** Should we differentiate rapid vs send-out tests?
5. **Cost-Effectiveness:** Should we include health economics of testing?

**Recommendation:** Start with laboratory tests (blood, CSF, respiratory, GI, urine). Defer imaging to potential Iteration 5.

---

## Next Steps

1. Validate MeSH terms using NCBI MeSH Browser
2. Create test queries to estimate article yields
3. Refine categories based on yield estimates
4. Create `collect_diagnostic_testing_guidelines.py` script
5. Execute Iteration 4 collection

---

**Author:** Claude Code
**Date:** 2025-11-16
**Status:** Proposed - Awaiting user approval

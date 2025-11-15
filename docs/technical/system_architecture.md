# System Architecture: Infectious Disease Diagnosis Clinical Decision Support

**Date:** 2025-11-15
**Project:** Infectious Disease Diagnosis Clinical Decision Support System
**Version:** 1.0 (Initial Design)

---

## Architecture Overview

The system comprises two integrated components:
1. **Predictive Diagnosis Model:** ML-based infectious disease prediction engine
2. **LLM Clinical Chatbot:** Conversational AI for clinical guidance using RAG architecture

These components work together to provide comprehensive clinical decision support for infectious disease diagnosis.

---

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  Web UI      │  │  Mobile UI   │  │  API Integration    │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                      Integration Layer                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │        Conversation Manager & Orchestration             │   │
│  │  • Session management  • Context tracking               │   │
│  │  • Component routing   • Response synthesis             │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────┬────────────────────────┬────────────────────┘
                    │                        │
       ┌────────────▼────────────┐  ┌────────▼────────────────┐
       │  Predictive Model       │  │  LLM Chatbot Component  │
       │  Component              │  │  (RAG Architecture)     │
       └─────────────────────────┘  └─────────────────────────┘
                    │                        │
       ┌────────────▼────────────┐  ┌────────▼────────────────┐
       │  ML Model Pipeline      │  │  RAG Pipeline           │
       │  • Feature engineering  │  │  • Query processing     │
       │  • Ensemble models      │  │  • Vector retrieval     │
       │  • Prediction output    │  │  • LLM generation       │
       │  • Explainability       │  │  • Source attribution   │
       └─────────────────────────┘  └───────────┬─────────────┘
                    │                            │
       ┌────────────▼────────────┐  ┌───────────▼─────────────┐
       │  Training Data          │  │  Knowledge Base         │
       │  • StatPearls           │  │  • Vector Database      │
       │  • Medscape             │  │  • Embeddings           │
       │  • Clinical datasets    │  │  • Medical literature   │
       └─────────────────────────┘  └─────────────────────────┘
```

---

## Component 1: Predictive Diagnosis Model

### Purpose
Machine learning model that analyzes patient presentation to predict infectious disease diagnoses with probability scores.

### Architecture

#### Input Layer
**Data Types:**
- Patient demographics (age, sex, location)
- Clinical symptoms and duration
- Vital signs (temperature, HR, BP, RR)
- Medical history and comorbidities
- Exposure history and travel
- Laboratory results (if available)
- Temporal patterns

**Input Format:**
```json
{
  "demographics": {
    "age": 45,
    "sex": "M",
    "location": "geographic_region"
  },
  "symptoms": [
    {"symptom": "fever", "duration_days": 3, "severity": "high"},
    {"symptom": "cough", "duration_days": 5, "severity": "moderate"}
  ],
  "vitals": {
    "temperature_f": 102.3,
    "heart_rate": 95,
    "bp_systolic": 125,
    "bp_diastolic": 80,
    "respiratory_rate": 18
  },
  "labs": {
    "wbc": 15000,
    "neutrophils_percent": 80,
    "crp": 50
  },
  "history": {
    "comorbidities": ["diabetes"],
    "recent_travel": "Southeast Asia",
    "exposures": ["sick_contacts"]
  }
}
```

#### Feature Engineering Pipeline

**1. Feature Extraction:**
- Numeric features: Vital signs, lab values, age, duration
- Categorical features: Symptoms, location, exposures, comorbidities
- Derived features: Symptom combinations, severity scores, temporal patterns

**2. Feature Transformation:**
- Standardization for numeric features
- One-hot encoding for categorical features
- Feature interaction terms (e.g., fever + cough + travel)
- Temporal features (symptom progression patterns)

**3. Feature Selection:**
- Clinical relevance (domain expert input)
- Statistical significance (correlation analysis)
- Model-based selection (feature importance)

#### Model Architecture

**Ensemble Approach (Recommended):**

**Base Models:**
1. **XGBoost Classifier**
   - Handles tabular data effectively
   - Feature importance built-in
   - Robust to missing values
   - High accuracy for structured clinical data

2. **CatBoost Classifier**
   - Superior categorical feature handling
   - Built-in regularization
   - Symmetric tree structure
   - Handles missing data natively

3. **Random Forest Classifier**
   - Robust ensemble baseline
   - Feature importance
   - Reduced overfitting
   - Interpretable

**Meta-Model:**
- Logistic Regression or Neural Network
- Combines base model predictions
- Calibrated probability outputs

**Alternative (if sufficient data): Deep Learning**
- LSTM for temporal symptom patterns
- Attention mechanisms for feature importance
- Requires larger training dataset (10,000+ cases)

#### Output Layer

**Prediction Output:**
```json
{
  "predictions": [
    {
      "disease": "Influenza A",
      "probability": 0.65,
      "confidence": "high",
      "evidence": ["fever", "cough", "seasonal_pattern"]
    },
    {
      "disease": "COVID-19",
      "probability": 0.25,
      "confidence": "moderate",
      "evidence": ["fever", "cough", "travel_history"]
    },
    {
      "disease": "Bacterial pneumonia",
      "probability": 0.10,
      "confidence": "low",
      "evidence": ["fever", "elevated_wbc"]
    }
  ],
  "recommended_tests": [
    "Rapid influenza test",
    "COVID-19 PCR",
    "Chest X-ray",
    "Blood cultures"
  ],
  "suggested_labs": [
    "Complete blood count",
    "Comprehensive metabolic panel",
    "Procalcitonin",
    "C-reactive protein"
  ]
}
```

#### Explainability Component

**SHAP (SHapley Additive exPlanations):**
- Per-prediction feature contributions
- Visualizations for clinicians
- Transparency in decision-making

**Output Example:**
```json
{
  "explanation": {
    "top_contributing_features": [
      {"feature": "fever_over_101", "contribution": 0.23},
      {"feature": "travel_to_endemic_region", "contribution": 0.18},
      {"feature": "duration_over_7_days", "contribution": 0.12}
    ],
    "visualization_data": {...}
  }
}
```

### Training Pipeline

**Data Collection:**
1. Synthetic data generation (initial development)
2. StatPearls disease profiles (feature patterns)
3. Medscape clinical presentations
4. Public infectious disease datasets (if available)
5. Real clinical data (partnership with institutions)

**Training Process:**
1. Data preprocessing and cleaning
2. Train-test split (80/20) with stratification
3. Cross-validation (5-fold or 10-fold)
4. Hyperparameter tuning (grid search or Bayesian optimization)
5. Ensemble model training
6. Calibration of probability outputs
7. Validation on holdout set

**Evaluation Metrics:**
- Accuracy, Precision, Recall, F1-score
- AUC-ROC for each disease class
- Top-3 and Top-5 accuracy (differential diagnosis)
- Calibration plots
- Clinical utility metrics

### Deployment Architecture

**Model Serving:**
- FastAPI or Flask REST API
- Containerized (Docker)
- Scalable (Kubernetes for production)
- Model versioning (MLflow or DVC)

**Model Updates:**
- Regular retraining schedule (quarterly)
- A/B testing for new model versions
- Monitoring for drift and performance degradation

---

## Component 2: LLM Clinical Chatbot (RAG Architecture)

### Purpose
Conversational AI that provides evidence-based clinical guidance, explains diagnostic predictions, and assists with test/treatment decisions.

### RAG (Retrieval-Augmented Generation) Architecture

#### Architecture Diagram

```
User Query
    │
    ▼
┌─────────────────────────┐
│  Query Processing       │
│  • Intent detection     │
│  • Entity extraction    │
│  • Query reformulation  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Embedding Generation   │
│  • BioBERT/PubMedBERT   │
│  • Vector representation│
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Vector Database Search │
│  • Semantic similarity  │
│  • Top-N retrieval      │
│  • Metadata filtering   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Re-ranking (Optional)  │
│  • Relevance scoring    │
│  • Top-K refinement     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Context Assembly       │
│  • Retrieved documents  │
│  • Predictive model out │
│  • Conversation history │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  LLM Generation         │
│  • GPT-4 / Claude       │
│  • Prompt engineering   │
│  • Safety constraints   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Response Processing    │
│  • Source attribution   │
│  • Formatting           │
│  • Confidence scoring   │
└───────────┬─────────────┘
            │
            ▼
       User Response
```

#### Knowledge Base Architecture

**Vector Database: ChromaDB (Development) / Pinecone (Production)**

**Document Structure:**
```json
{
  "id": "disease_001_symptoms",
  "content": "Influenza A presents with sudden onset fever, cough...",
  "metadata": {
    "disease": "Influenza A",
    "category": "clinical_presentation",
    "source": "StatPearls",
    "icd10": "J10.1",
    "pathogen_type": "virus",
    "last_updated": "2025-01-15"
  },
  "embedding": [0.123, 0.456, ...]
}
```

**Document Categories:**
- Disease overviews
- Clinical presentations (symptoms)
- Diagnostic approaches (tests and labs)
- Differential diagnoses
- Treatment guidelines (categories, not specific prescriptions)
- Epidemiology and risk factors

**Chunking Strategy:**
- Chunk size: 300-500 tokens
- Overlap: 50 tokens
- Semantic coherence maintained
- Section-based chunking (symptoms, diagnosis, treatment)

#### Embedding Model

**Primary: PubMedBERT or BioBERT**
- Medical domain-specific embeddings
- Superior performance on clinical text
- Pre-trained on biomedical literature

**Dimension:** 768 (standard BERT)

**Alternative: Clinical-BERT**
- Trained on clinical notes
- Good for clinical language understanding

#### LLM Selection

**Production Options:**

**Option 1: GPT-4 (OpenAI)**
- Pros: Highest quality, medical knowledge, excellent reasoning
- Cons: Cost, API dependency, privacy considerations

**Option 2: Claude 3 (Anthropic)**
- Pros: High quality, safety-focused, good medical understanding
- Cons: Cost, API dependency

**Option 3: Llama 3 or Meditron (Open-source)**
- Pros: On-premise deployment, HIPAA compliance, no API costs
- Cons: Lower quality than GPT-4/Claude, requires infrastructure

**Recommendation:** GPT-4 or Claude for initial development, evaluate Llama 3/Meditron for production if privacy/cost critical.

#### Prompt Engineering

**System Prompt Template:**
```
You are a clinical decision support assistant specializing in infectious
diseases. Your role is to provide evidence-based guidance to clinicians.

CRITICAL CONSTRAINTS:
- Provide diagnostic guidance, not autonomous diagnoses
- Suggest test categories and lab work, not treatment prescriptions
- Recommend treatment categories, not specific medications
- Always cite sources for clinical recommendations
- Acknowledge uncertainty when appropriate
- Emphasize need for clinical judgment

RESPONSE FORMAT:
- Clear, concise medical terminology with plain language explanations
- Source citations for all clinical claims
- Differential diagnosis considerations
- Recommended diagnostic workup

Context: {retrieved_documents}
Predictive Model Output: {model_predictions}
Conversation History: {history}

User Query: {user_query}
```

**Safety Constraints:**
- No specific medication dosing
- No autonomous treatment decisions
- Clear disclaimers about decision support role
- Emphasis on clinician judgment

#### Response Generation

**Response Structure:**
```json
{
  "response": "Based on the patient's presentation...",
  "sources": [
    {
      "content": "Influenza A typically presents with...",
      "source": "StatPearls - Influenza",
      "url": "https://..."
    }
  ],
  "confidence": "high",
  "differential_diagnosis": [
    "Influenza A (65% probability)",
    "COVID-19 (25% probability)",
    "Bacterial pneumonia (10% probability)"
  ],
  "recommended_tests": [
    "Rapid influenza test",
    "COVID-19 PCR"
  ],
  "suggested_labs": [
    "CBC with differential",
    "CRP"
  ],
  "treatment_categories": [
    "Antiviral therapy (for confirmed influenza)",
    "Supportive care"
  ],
  "disclaimer": "This is clinical decision support. Final diagnosis and treatment decisions require physician judgment."
}
```

### Integration with Predictive Model

**Conversation Flow:**

1. **User initiates query** (e.g., "45-year-old male with fever and cough for 3 days")

2. **Chatbot gathers information:**
   - Conversational elicitation of symptoms
   - Clarifying questions for missing data
   - Structured data extraction

3. **Invoke Predictive Model:**
   - Structured input sent to ML model
   - Receive probability predictions

4. **RAG retrieval:**
   - Retrieve relevant disease information for top predictions
   - Gather diagnostic and treatment guidance

5. **LLM generates response:**
   - Synthesizes model predictions with retrieved knowledge
   - Explains reasoning and evidence
   - Provides recommendations

6. **User interaction:**
   - Clinician reviews and asks follow-up questions
   - Chatbot provides additional details
   - Iterative refinement

**Integration API:**
```python
# Pseudo-code
def process_clinical_query(user_input, session_context):
    # Extract structured data from conversation
    structured_data = extract_clinical_data(user_input, session_context)

    # Call predictive model
    predictions = predictive_model.predict(structured_data)

    # Retrieve relevant knowledge
    retrieved_docs = rag_retriever.retrieve(
        query=user_input,
        filter={"disease": predictions.top_diseases}
    )

    # Generate response with LLM
    response = llm.generate(
        prompt=build_prompt(
            user_input,
            predictions,
            retrieved_docs,
            session_context
        )
    )

    return response
```

---

## Integration Layer: Conversation Manager

### Responsibilities
- Manage user sessions and context
- Route between components
- Orchestrate conversation flow
- Synthesize outputs

### Session Management
- Track conversation history
- Maintain patient context within session
- Clear session data after completion (privacy)

### Context Tracking
```json
{
  "session_id": "abc123",
  "user_role": "clinician",
  "conversation_history": [
    {"role": "user", "message": "..."},
    {"role": "assistant", "message": "..."}
  ],
  "current_case": {
    "patient_data": {...},
    "working_diagnosis": [...],
    "tests_ordered": [...]
  },
  "timestamp": "2025-11-15T10:30:00Z"
}
```

---

## Data Layer

### Training Data (Predictive Model)
- **Storage:** PostgreSQL or cloud data warehouse
- **Format:** Structured tables (patients, symptoms, diagnoses, labs)
- **Versioning:** Data version control (DVC)
- **Access:** Secure, HIPAA-compliant

### Knowledge Base (RAG)
- **Vector Database:** ChromaDB (dev) / Pinecone (prod)
- **Content:** Extracted from StatPearls, Medscape, PubMed, clinical guidelines
- **Updates:** Quarterly synchronization, version tracking
- **Backup:** Regular backups, disaster recovery

---

## Infrastructure and Deployment

### Development Environment
- Local development with Docker Compose
- Jupyter notebooks for experimentation
- Version control: Git/GitHub
- ML experiment tracking: MLflow

### Production Architecture

**Cloud Platform:** AWS, Google Cloud, or Azure (HIPAA-compliant regions)

**Components:**
1. **API Gateway:** AWS API Gateway or nginx
2. **Application Server:** FastAPI (Python) in Docker containers
3. **Model Serving:** TensorFlow Serving or custom FastAPI endpoints
4. **Vector Database:** Managed Pinecone or self-hosted Milvus
5. **Relational Database:** PostgreSQL (RDS or managed)
6. **Caching:** Redis for session management
7. **Monitoring:** Prometheus + Grafana
8. **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)

**Containerization:**
```
docker-compose.yml:
- api-gateway
- predictive-model-service
- llm-chatbot-service
- vector-database
- postgres
- redis
- monitoring
```

**Scaling:**
- Horizontal scaling with Kubernetes
- Load balancing
- Auto-scaling based on traffic

### Security and Compliance

**HIPAA Compliance:**
- No storage of patient-identifiable information
- End-to-end encryption (TLS)
- Access controls and authentication
- Audit logging
- Business Associate Agreements (BAAs) with cloud providers

**API Security:**
- Authentication (OAuth 2.0 or API keys)
- Rate limiting
- Input validation and sanitization
- CORS policies

**Data Privacy:**
- Minimal data retention
- Anonymization of logs
- Secure communication channels
- Regular security audits

---

## Monitoring and Observability

### Model Performance Monitoring
- Prediction accuracy tracking
- Confidence calibration checks
- Drift detection (data and concept drift)
- A/B testing for model versions

### System Metrics
- API latency and throughput
- Error rates
- Cache hit rates
- Database query performance

### User Analytics
- Query patterns
- Session duration
- User satisfaction (feedback collection)
- Most common disease queries

### Alerting
- Model performance degradation
- System downtime
- High error rates
- Security incidents

---

## Technology Stack Summary

### Predictive Model
- **Languages:** Python 3.10+
- **ML Libraries:** scikit-learn, XGBoost, CatBoost, LightGBM
- **Deep Learning (optional):** TensorFlow or PyTorch
- **Explainability:** SHAP
- **Experiment Tracking:** MLflow

### LLM Chatbot
- **LLM:** GPT-4, Claude 3, or Llama 3
- **Embeddings:** PubMedBERT, BioBERT
- **Vector Database:** ChromaDB (dev), Pinecone (prod)
- **Orchestration:** LangChain or custom
- **Frameworks:** Python, FastAPI

### Infrastructure
- **API Framework:** FastAPI
- **Web Framework (UI):** React or Vue.js
- **Database:** PostgreSQL
- **Caching:** Redis
- **Containerization:** Docker, Docker Compose
- **Orchestration:** Kubernetes (production)
- **Cloud:** AWS, GCP, or Azure (HIPAA-compliant)

### Monitoring and DevOps
- **Monitoring:** Prometheus, Grafana
- **Logging:** ELK Stack
- **CI/CD:** GitHub Actions, GitLab CI, or Jenkins
- **Version Control:** Git, GitHub/GitLab

---

## Development Roadmap Integration

This architecture supports the phased development approach:

**Phase 1 (Research & Planning):** Architecture defined ✓

**Phase 2 (Data Collection):** Knowledge base and training data preparation

**Phase 3 (Predictive Model):** ML model development and training

**Phase 4 (LLM Chatbot):** RAG implementation and chatbot development

**Phase 5 (Integration):** Conversation manager and unified system

**Phase 6 (Deployment):** Production deployment and validation

---

## Conclusion

This architecture provides a scalable, maintainable, and clinically effective system for infectious disease diagnosis support. The separation of concerns between predictive modeling and conversational AI allows independent development and optimization of each component, while the integration layer ensures seamless user experience.

Key architectural strengths:
- Modular design for independent component development
- Scalable infrastructure for growth
- Evidence-based RAG approach for accuracy
- Explainable AI for clinical trust
- HIPAA-compliant security design
- Monitoring for continuous improvement

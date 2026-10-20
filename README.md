# Venture: Explainable Multi-Modal AI for Risk-Aware Personalized Hiking in Sri Lanka
## Component 4: Context-Aware Emergency Detection and Response Recommendation System
**Student**: Mihiranga U.G.P.G. (IT23309142)  
**Supervisor**: Mrs. Lokesha Weerasinghe | **Co-Supervisor**: Ms. Lashika Chamini  
**Project Group**: J26-IT-342  
**Affiliation**: Sri Lanka Institute of Information Technology (SLIIT), Department of Information Technology  

---

## 1. Project Overview & Scope
Hiking in Sri Lanka's mountainous terrains (Knuckles, Horton Plains, Adam's Peak, Ella Rock, Sinharaja, Riverston, Pidurangala) involves dynamic environmental risks such as sudden tropical cloudbursts, landslides, trail blockages, steep drop-offs, and communication dropouts. 

**Component 4** provides intelligent, context-aware emergency decision support during the emergency stage of a hike by combining:
1. **Unstructured Incident Text NLP**: Extracts emergency categories, severity indicators, and assistance needs.
2. **Machine Learning Pipeline**: Multi-class emergency classification and severity estimation comparing **Random Forest (Baseline 1)** and **XGBoost (Baseline 2)** with 5-Fold Stratified Cross-Validation.
3. **Domain Knowledge Graph Reasoning**: NetworkX-based ontology connecting environmental context, hazards, resources, and response actions with explainable traversal paths.
4. **Explainable AI (XAI)**: SHAP (SHapley Additive exPlanations) TreeExplainer factor attribution providing transparent rationale for emergency predictions.
5. **Geospatial Emergency Resource Locator**: Haversine distance and mountain response time calculation to verified Sri Lankan hospitals, DWC wildlife ranger posts, and police stations.
6. **Mobile Application**: Flutter frontend (`venture_mobileapp`) providing responsive screens for reporting, analysis, assessment, context telemetry, recommendations, resources, XAI insights, and SOS dispatch.

---

## 2. System Architecture

```text
               +-------------------------------------------------------------+
               |                         INPUT LAYER                         |
               | Incident Text | GPS Coordinates | Telemetry | Terrain Data  |
               +------------------------------+------------------------------+
                                              |
                                              v
               +-------------------------------------------------------------+
               |            DATA PROCESSING & CONTEXT CONSTRUCTION           |
               |      Cleaning | Feature Pipeline | NLP Indicator Extraction |
               +------------------------------+------------------------------+
                                              |
                                              v
               +-------------------------------------------------------------+
               |                  AI / ML EMERGENCY DETECTION                |
               |  Random Forest & XGBoost Classifiers | Severity Regressor   |
               +------------------------------+------------------------------+
                                              |
                                              v
               +-------------------------------------------------------------+
               |                    DECISION SUPPORT LAYER                   |
               | NetworkX Knowledge Graph Traversal | SHAP Explainability    |
               +------------------------------+------------------------------+
                                              |
                                              v
               +-------------------------------------------------------------+
               |                         OUTPUT LAYER                        |
               | Assessment | Prioritized Guidance | Nearest Sri Lanka Units |
               +-------------------------------------------------------------+
```

---

## 3. Directory Structure

```text
├── ML_models/
│   └── component04/
│       ├── data/                   # Synthetic emergency incidents & KG triples
│       ├── models/                 # Serialized model pipelines (.joblib)
│       ├── reports/                # Classification & ablation JSON reports
│       ├── train_models.py         # Advanced ML training & ablation pipeline
│       ├── kg_reasoning.py         # NetworkX ontology reasoning engine
│       ├── nlp_extract.py          # Incident text extraction module
│       └── api.py                  # Component 4 API bridge
├── backend/
│   ├── api/
│   │   └── emergency.py            # Component 4 REST API router
│   ├── services/
│   │   ├── emergency_service.py    # Main multimodal orchestrator
│   │   ├── geo_service.py          # Haversine nearest resources locator
│   │   └── explainability_service.py # SHAP interpretability service
│   ├── schemas/
│   │   └── emergency.py            # Pydantic request & response models
│   └── main.py                     # Unified FastAPI application entrypoint
├── frontend/
│   └── venture_mobileapp/          # Flutter mobile application
│       └── lib/
│           ├── models/             # Typed Dart emergency models
│           ├── services/           # Dio HTTP API client with offline fallback
│           └── screens/component04/ # 8 complete UI screens
└── tests/
    └── test_emergency_pipeline.py  # Automated unit and integration test suite
```

---

## 4. Setup & Installation

### Python Backend & ML Environment
```bash
# Activate existing virtual environment (Windows)
.venv\Scripts\activate

# Install required dependencies
pip install -r backend/requirements.txt
pip install xgboost shap networkx pytest httpx
```

### Running Model Training, Evaluation & Ablation Study
```bash
python ML_models/component04/train_models.py
```
This script:
- Compares **Random Forest** vs. **XGBoost** for emergency classification and severity estimation.
- Executes **5-Fold Stratified Cross-Validation**.
- Executes the **Ablation Study** (Variants A, B, C, D) defined in Section 3.7.3.
- Computes global **SHAP TreeExplainer feature importance** values.
- Exports evaluation reports to `ML_models/component04/reports/`.

---

## 5. Running the API

Start the FastAPI application:
```bash
uvicorn backend.main:app --reload --port 8000
```
Interactive Swagger API documentation will be available at:
`http://127.0.0.1:8000/docs`

### Key Endpoints:
- `POST /api/v1/emergency/analyze`: Full multimodal emergency decision analysis (NLP + ML + KG + SHAP + Geo).
- `POST /api/v1/emergency/extract-text`: Unstructured text entity extraction.
- `GET /api/v1/emergency/resources`: Nearest Sri Lankan emergency facilities via GPS coordinates.
- `GET /api/v1/emergency/benchmarks`: Model comparisons and ablation study metrics.
- `GET /api/v1/emergency/shap-importance`: Global SHAP feature importance attribution.

---

## 6. Running Automated Tests

Run the complete test suite:
```bash
pytest tests/test_emergency_pipeline.py -v
```
All 16 test cases cover NLP extraction, Knowledge Graph reasoning, Haversine geospatial calculations, SHAP factor attribution, and FastAPI endpoints.

---

## 7. Running the Mobile Application (Flutter)

Navigate to the mobile app directory:
```bash
cd frontend/venture_mobileapp
flutter run
```
The app communicates with the FastAPI backend at `http://10.0.2.2:8000` (Android emulator) or `http://127.0.0.1:8000` (web/desktop), with automatic offline fallback so demo presentations run seamlessly.

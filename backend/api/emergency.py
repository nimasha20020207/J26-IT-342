"""
API Router for Component 4: Emergency Detection & Response Recommendation System
"""
from pathlib import Path
import json
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from backend.schemas.emergency import (
    IncidentInput,
    FullEmergencyAnalysisResponse,
    NLPInformationExtraction,
    NearestResourceItem
)
from backend.services.emergency_service import EmergencyDecisionService
from backend.services.geo_service import GeoEmergencyService

router = APIRouter(prefix="/api/v1/emergency", tags=["Component 4: Emergency Detection & Response"])

service = EmergencyDecisionService()
geo_service = GeoEmergencyService()

ROOT_DIR = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT_DIR / "ML_models" / "component04" / "reports"

@router.post("/analyze", response_model=FullEmergencyAnalysisResponse, summary="Analyze Full Emergency Scenario")
def analyze_emergency(incident: IncidentInput):
    """
    Executes the multimodal pipeline:
    1. Incident Report NLP extraction
    2. ML Emergency Classification & Severity Regression
    3. Knowledge Graph Reasoning for context-aware actions
    4. SHAP Feature Attribution & Interpretability
    5. Geospatial nearest emergency facilities identification
    """
    try:
        response = service.analyze(incident)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency analysis pipeline error: {str(e)}")

@router.post("/extract-text", response_model=NLPInformationExtraction, summary="Extract Emergency Entities from Text")
def extract_text_indicators(text: str = Query(..., description="Incident narrative text")):
    """Extracts emergency keywords, severity cues, environmental factors, and assistance requests."""
    res = service.nlp_extractor.extract(text)
    return NLPInformationExtraction(
        detected_emergency_types=res.get("detected_emergency_types", []),
        primary_candidate=res.get("primary_candidate", "unspecified"),
        severity_urgency=res.get("severity_urgency", "LOW"),
        environmental_hazards=res.get("environmental_hazards", []),
        required_assistance=res.get("required_assistance", []),
        confidence_score=res.get("confidence_score", 0.0)
    )

@router.get("/resources", summary="Get Nearest Sri Lankan Emergency Facilities")
def get_nearest_resources(
    latitude: float = Query(6.8096, description="GPS Latitude"),
    longitude: float = Query(80.8028, description="GPS Longitude"),
    limit: int = Query(5, ge=1, le=15, description="Max number of facilities"),
    resource_type: Optional[str] = Query(None, description="Filter: Hospital, Ranger Post, Police")
):
    """Calculates Haversine distances to emergency hospitals, DWC ranger posts, and police stations."""
    return geo_service.find_nearest_resources(latitude, longitude, limit=limit, resource_type=resource_type)

@router.get("/benchmarks", summary="Retrieve Research Model Baselines & Ablation Study Metrics")
def get_research_benchmarks():
    """
    Returns empirical evaluation results:
    - Baseline 1 (Random Forest) vs Baseline 2 (XGBoost)
    - 5-Fold Stratified Cross-Validation metrics
    - Severity estimation MAE, RMSE, R2
    - Ablation Study (Variants A, B, C, D)
    """
    comp_path = REPORTS_DIR / "model_comparison_report.json"
    abl_path = REPORTS_DIR / "ablation_study_report.json"
    
    if not comp_path.exists() or not abl_path.exists():
        raise HTTPException(status_code=404, detail="Benchmark reports not found. Please run training pipeline.")
        
    return {
        "model_comparison": json.loads(comp_path.read_text()),
        "ablation_study": json.loads(abl_path.read_text())
    }

@router.get("/shap-importance", summary="Retrieve Global SHAP Feature Importance Rankings")
def get_shap_feature_importance():
    """Returns ranked feature importance based on TreeExplainer SHAP values."""
    shap_path = REPORTS_DIR / "shap_feature_importance.json"
    if not shap_path.exists():
        raise HTTPException(status_code=404, detail="SHAP feature importance report not found.")
    return json.loads(shap_path.read_text())

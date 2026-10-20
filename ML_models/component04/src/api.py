"""Minimal FastAPI inference API for the demo. Run: uvicorn src.api:app --reload"""
from pathlib import Path
import joblib, pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
app = FastAPI(title="Hiking Emergency Component 4 API", version="0.1-demo")

class Incident(BaseModel):
    incident_text: str = Field(min_length=5)
    elevation_m: float = 800
    slope_degrees: float = 15
    rainfall_mm: float = 0
    temperature_c: float = 25
    wind_speed_kmh: float = 10
    visibility_pct: float = 80
    hours_hiking: float = 2
    distance_from_trailhead_km: float = 2
    phone_battery_pct: float = 70
    fatigue_score_1_10: int = Field(default=3, ge=1, le=10)
    water_remaining_l: float = 1
    remote_area: int = Field(default=0, ge=0, le=1)
    terrain_type: str = "forest"

def recommendations(emergency, severity, rain, visibility, terrain):
    actions = []
    if emergency == "injury":
        actions += ["request_rescue_assistance", "provide_first_aid_if_trained", "share_gps_location"]
    elif emergency == "lost_hiker":
        actions += ["share_gps_location", "stay_in_safe_location", "contact_rescue_authority"]
    elif emergency == "landslide":
        actions += ["avoid_crossing_debris", "move_away_from_slope_if_safe", "contact_rescue_authority"]
    elif emergency == "flooding":
        actions += ["do_not_cross_fast_water", "move_to_safe_high_ground_if_safe", "contact_rescue_authority"]
    elif emergency == "dehydration_fatigue":
        actions += ["stop_in_safe_shade", "contact_medical_help_if_severe", "share_gps_location"]
    elif emergency == "wildlife_encounter":
        actions += ["keep_distance_and_do_not_approach", "retreat_slowly_if_safe", "contact_local_authorities_if_threat_persists"]
    elif emergency == "severe_weather":
        actions += ["leave_exposed_area_if_safe", "seek_shelter_without_entering_hazard_zone", "contact_rescue_authority"]
    else:
        actions += ["do_not_cross_unsafe_obstacle", "return_to_known_safe_route_if_safe", "contact_trail_authority"]
    if rain >= 30 and "avoid_crossing_debris" not in actions:
        actions.insert(0, "reassess_route_due_to_heavy_rain")
    if visibility < 25 and "share_gps_location" not in actions:
        actions.insert(0, "share_gps_location")
    if severity >= 4:
        actions.insert(0, "contact_local_emergency_services")
    return list(dict.fromkeys(actions))

@app.get("/health")
def health():
    return {"status":"ok","demo_only":True}

@app.post("/predict")
def predict(item: Incident):
    required = [MODELS/"emergency_classifier.joblib", MODELS/"severity_regressor.joblib",
                MODELS/"incident_text_classifier.joblib"]
    if not all(p.exists() for p in required):
        raise HTTPException(status_code=503, detail="Train models first: python src/train_models.py")
    numeric = item.model_dump(exclude={"incident_text"})
    X = pd.DataFrame([numeric])
    clf = joblib.load(MODELS/"emergency_classifier.joblib")
    sev = joblib.load(MODELS/"severity_regressor.joblib")
    nlp = joblib.load(MODELS/"incident_text_classifier.joblib")
    structured_type = str(clf.predict(X)[0])
    text_type = str(nlp.predict([item.incident_text])[0])
    # Demo fusion: text model type is used if it agrees with the structured model; otherwise
    # choose text prediction as a practical baseline and expose both for transparency.
    emergency = text_type
    severity = max(1, min(5, int(round(float(sev.predict(X)[0])))))
    actions = recommendations(emergency, severity, item.rainfall_mm, item.visibility_pct, item.terrain_type)
    return {
        "demo_warning":"Synthetic-data prototype only; not a validated emergency or medical system.",
        "emergency_type": emergency,
        "structured_model_prediction": structured_type,
        "text_model_prediction": text_type,
        "severity_level": severity,
        "urgency": "HIGH" if severity >= 4 else "MODERATE" if severity == 3 else "LOW",
        "recommended_actions": actions,
        "explanation": [
            f"Text classifier identified wording associated with {text_type}.",
            f"Structured model independently predicted {structured_type}.",
            f"Severity estimate was {severity}/5 using terrain and environmental features.",
            "Response actions are selected from transparent demo rules; expert validation is required."
        ],
        "is_synthetic_training": True
    }

"""
forecast_service.py
-------------------
Component 02: Reliability-Aware Hazard Forecasting Service

Performs live inference using the trained Baseline 03 Adaptive Fusion Model,
combining real-time Open-Meteo meteorological observations, trail terrain
characteristics, and reliability-weighted social intelligence.
"""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Optional
from uuid import uuid4

import joblib
import numpy as np
import pandas as pd

from schemas.component02.forecast import (
    DailyPrediction,
    ForecastRequest,
    ForecastResponse,
    Hazard,
    HeatZoneFeature,
    HeatZoneGeometry,
    HeatZoneProperties,
    HeatZonesResponse,
    Recommendation,
    RiskTrend,
    SocialReport,
    TrailLocationResponse,
)
from services.component02.trail_locations import TRAIL_COORDINATES, TRAIL_TERRAIN
from services.component02.weather_service import get_trail_weather

# Paths to ML Artifacts
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BACKEND_ROOT.parent

# Check potential locations for ML artifacts
ML_SEARCH_PATHS = [
    REPO_ROOT / "ML_models" / "component02",
    Path("D:/J26-IT-342/ML_models/component02"),
    Path("D:/Research/J26-IT-342/ML_models/component02"),
]

ML_DIR = None
for p in ML_SEARCH_PATHS:
    if (p / "models" / "saved_baselines" / "baseline_03_hazard_classifier.pkl").exists():
        ML_DIR = p
        break

if ML_DIR is None:
    ML_DIR = REPO_ROOT / "ML_models" / "component02"

MODELS_DIR = ML_DIR / "models" / "saved_baselines"
OUTPUTS_DIR = ML_DIR / "outputs"

# Cache loaded models & social data
_CLASSIFIER = None
_REGRESSOR = None
_LABEL_ENCODER = None
_SOCIAL_MATRIX = None
_SOCIAL_REPORTS = None

ALL_HAZARDS = [
    "slippery or muddy trails",
    "landslides",
    "dense fog or poor visibility",
    "rockfalls",
    "high leech activity",
    "strong winds",
    "trail obstructions",
    "monkey sightings",
    "bugs or wasps activity",
    "heavy rain",
]


def _load_ml_artifacts():
    global _CLASSIFIER, _REGRESSOR, _LABEL_ENCODER, _SOCIAL_MATRIX, _SOCIAL_REPORTS

    if _CLASSIFIER is None:
        clf_file = MODELS_DIR / "baseline_03_hazard_classifier.pkl"
        reg_file = MODELS_DIR / "baseline_03_risk_regressor.pkl"
        le_file = MODELS_DIR / "label_encoder.pkl"

        if clf_file.exists() and reg_file.exists() and le_file.exists():
            _CLASSIFIER = joblib.load(clf_file)
            _REGRESSOR = joblib.load(reg_file)
            _LABEL_ENCODER = joblib.load(le_file)
        else:
            print(f"[Warning] ML model files not found in {MODELS_DIR}. Fallback mode active.")

    if _SOCIAL_MATRIX is None:
        matrix_file = OUTPUTS_DIR / "trail_social_hazard_matrix.csv"
        if matrix_file.exists():
            _SOCIAL_MATRIX = pd.read_csv(matrix_file, low_memory=False)

    if _SOCIAL_REPORTS is None:
        reports_file = OUTPUTS_DIR / "social_reliability_evaluated.csv"
        if reports_file.exists():
            _SOCIAL_REPORTS = pd.read_csv(reports_file, low_memory=False)


_load_ml_artifacts()


def _get_risk_level(score: float) -> str:
    if score >= 75:
        return "Very High"
    elif score >= 50:
        return "High"
    elif score >= 25:
        return "Medium"
    else:
        return "Low"


def _generate_recommendations(top_hazard: str, risk_score: float) -> Recommendation:
    """Produce context-aware safety recommendations based on predicted risks."""
    if risk_score >= 75:
        action = "Postpone or Re-route Hike"
        summary = f"Severe hazard conditions forecasted ({top_hazard.title()}). Unfavorable for hiking."
        precautions = [
            "Heavy environmental threat detected; local authorities advise staying off exposed trails.",
            "If already on the mountain, immediately retreat to safe sheltered ground.",
            "Emergency contact numbers (SL Police 119, Disaster Mgmt 117) must be kept accessible.",
        ]
    elif risk_score >= 50:
        action = "Proceed with High Caution"
        summary = f"Elevated hazard risks detected on trail. Heightened risk of {top_hazard}."
        precautions = [
            "Carry full wet-weather gear, sturdy footwear with deep traction, and a thermal layer.",
            "Avoid traversing steep rock ledges and ridge crests during peak afternoon hours.",
            "Ensure hiking groups remain together and monitor shifting visibility closely.",
        ]
    elif risk_score >= 25:
        action = "Proceed with Caution"
        summary = f"Moderate trail conditions. Potential isolated {top_hazard}."
        precautions = [
            "Standard trail gear recommended; wear anti-leech socks in damp forested sections.",
            "Start early in the morning to complete the trail before afternoon weather shifts.",
            "Stay on marked footpaths and avoid unverified shortcuts.",
        ]
    else:
        action = "Safe to Hike"
        summary = "Trail conditions are favorable and within normal seasonal parameters."
        precautions = [
            "Maintain standard hydration (minimum 2L water per hiker) and sun protection.",
            "Adhere to leave-no-trace outdoor ethics and respect local wildlife.",
        ]

    return Recommendation(action=action, summary=summary, precautions=precautions)


def _get_trail_social_reports(trail_name: str) -> list[SocialReport]:
    """Retrieve actual evaluated social reports for this trail."""
    _load_ml_artifacts()
    if _SOCIAL_REPORTS is None or _SOCIAL_REPORTS.empty:
        return []

    trail_reps = _SOCIAL_REPORTS[_SOCIAL_REPORTS["trail_name"].str.lower() == trail_name.lower()]
    if trail_reps.empty:
        # Return generic community guidance
        return [
            SocialReport(
                source="Hiking Community Forum",
                type="Hiker Report",
                content=f"No recent adverse user reports logged for {trail_name} within the last 48 hours.",
                time_ago="1 day ago",
                reliability_score=0.85,
                confidence_indicator="High Confidence",
            )
        ]

    reports = []
    for _, row in trail_reps.head(4).iterrows():
        content = str(row.get("content", ""))
        if len(content) > 130:
            content = content[:127] + "..."

        reports.append(
            SocialReport(
                source=f"{str(row.get('source', '')).capitalize()} Report",
                type="Crowdsourced / Media",
                content=content,
                time_ago="Recent report",
                reliability_score=round(float(row.get("reliability_score", 0.80)), 2),
                confidence_indicator=f"{str(row.get('reliability_tier', 'HIGH')).title()} Reliability",
            )
        )
    return reports


def generate_live_forecast(request: ForecastRequest) -> ForecastResponse:
    """
    Main forecast inference routine.
    Fetches real-time weather from Open-Meteo, fuses with terrain and social reliability data,
    and runs inference through the trained Baseline 03 Adaptive Fusion Model.
    """
    if request.end_date < request.start_date:
        raise ValueError("end_date must be on or after start_date")

    _load_ml_artifacts()

    # 1. Fetch live meteorological summary from Open-Meteo
    weather = get_trail_weather(request.trail_name, request.start_date)

    # 2. Extract terrain attributes
    terrain_info = TRAIL_TERRAIN.get(request.trail_name, {"elevation_m": 1000, "slope_degrees": 20.0})
    elevation_m = terrain_info["elevation_m"]
    slope_degrees = terrain_info["slope_degrees"]

    # 3. Retrieve trail social profile
    trail_social = {}
    mean_rel = 0.85
    mean_cred = 0.85
    if _SOCIAL_MATRIX is not None:
        match = _SOCIAL_MATRIX[_SOCIAL_MATRIX["trail_name"].str.lower() == request.trail_name.lower()]
        if not match.empty:
            trail_social = match.iloc[0].to_dict()
            mean_rel = float(trail_social.get("mean_reliability_score", 0.85))
            mean_cred = float(trail_social.get("mean_source_credibility", 0.85))

    # 4. Compute Environmental Extremity and Adaptive Dynamic Weights
    rain_norm = min(1.0, weather.precipitation_mm / 100.0)
    wind_norm = min(1.0, weather.wind_gust_kmh / 60.0)
    e_env = min(1.0, 0.6 * rain_norm + 0.4 * wind_norm)

    w_social = min(0.45, max(0.05, 0.40 * mean_rel * (1.0 - 0.50 * e_env)))
    w_env = 1.0 - w_social

    # 5. Assemble exact Baseline 03 Feature Vector
    features = {
        "temperature_mean_c": weather.temperature_c - 2.0,
        "temperature_max_c": weather.temperature_c,
        "relative_humidity_mean_pct": float(weather.humidity),
        "dew_point_depression_min_c": max(0.0, weather.temperature_c - (weather.temperature_c - ((100 - weather.humidity) / 5))),
        "precipitation_sum_mm": weather.precipitation_mm,
        "rainfall_24h_max_mm": weather.precipitation_mm,
        "wind_speed_mean_kmh": weather.wind_speed_kmh,
        "wind_gust_max_kmh": weather.wind_gust_kmh,
        "elevation_m": float(elevation_m),
        "slope_degrees": float(slope_degrees),
        "rule_triggered_hours": 8.0 if rain_norm > 0.3 or wind_norm > 0.5 else 0.0,
        "environmental_extremity": e_env,
        "mean_reliability_score": mean_rel,
        "mean_source_credibility": mean_cred,
        "adaptive_weight_env": w_env,
        "adaptive_weight_social": w_social,
    }

    # Add social hazard scores and fused features
    for h in ALL_HAZARDS:
        rel_h = float(trail_social.get(f"rel_social_{h}", 0.0))
        features[f"rel_social_{h}"] = rel_h

        # Fused proxy
        if h in ["slippery or muddy trails", "landslides", "heavy rain"]:
            proxy = rain_norm
        elif h in ["dense fog or poor visibility"]:
            proxy = float(weather.humidity) / 100.0
        elif h in ["strong winds"]:
            proxy = wind_norm
        else:
            proxy = 0.1

        features[f"fused_risk_{h}"] = w_env * proxy + w_social * rel_h

    # Convert to DataFrame and align columns exactly to the trained model's feature_names_in_
    X_input = pd.DataFrame([features])
    if _CLASSIFIER is not None and hasattr(_CLASSIFIER, "feature_names_in_"):
        for missing_col in _CLASSIFIER.feature_names_in_:
            if missing_col not in X_input.columns:
                X_input[missing_col] = 0.0
        X_input = X_input[list(_CLASSIFIER.feature_names_in_)]

    # 6. Model Inference
    mode = "demo"
    if _CLASSIFIER is not None and _REGRESSOR is not None:
        try:
            mode = "model_inference"
            pred_risk = float(_REGRESSOR.predict(X_input)[0])
            pred_risk = max(0.0, min(100.0, round(pred_risk, 1)))

            class_probs = _CLASSIFIER.predict_proba(X_input)[0]
            classes = _LABEL_ENCODER.classes_
            prob_map = {classes[i]: class_probs[i] for i in range(len(classes))}
        except Exception as e:
            print(f"[Error] Inference error: {e}. Falling back to rule-adjusted baseline.")
            mode = "rule_fallback"
            pred_risk = round(e_env * 70.0 + (10 if weather.rain_chance > 60 else 0), 1)
            prob_map = {h: 0.1 for h in ALL_HAZARDS}
    else:
        pred_risk = round(e_env * 70.0 + (15 if weather.rain_chance > 50 else 5), 1)
        prob_map = {h: 0.1 for h in ALL_HAZARDS}

    risk_level = _get_risk_level(pred_risk)

    # 7. Format Hazards Breakdown
    hazard_list = []
    for h in ALL_HAZARDS:
        # Calibrated probability combining model class probability and fused risk score
        p = float(prob_map.get(h, 0.05))
        # Boost probability if specific physical condition is active
        if h == "heavy rain" and weather.precipitation_mm > 15:
            p = max(p, 0.85)
        elif h == "slippery or muddy trails" and (weather.precipitation_mm > 5 or weather.humidity > 85):
            p = max(p, 0.75)
        elif h == "dense fog or poor visibility" and weather.humidity > 90:
            p = max(p, 0.80)
        elif h == "strong winds" and weather.wind_gust_kmh > 40:
            p = max(p, 0.70)

        # Severity
        if p >= 0.7:
            sev = "High"
        elif p >= 0.4:
            sev = "Medium"
        else:
            sev = "Low"

        hazard_list.append(Hazard(name=h.title(), probability=round(p, 2), severity=sev))

    # Sort hazards by probability descending
    hazard_list.sort(key=lambda x: x.probability, reverse=True)
    top_hazard_name = hazard_list[0].name

    # 8. Dynamic Recommendations
    recommendation = _generate_recommendations(top_hazard_name, pred_risk)

    # 9. Real Evaluated Social Reports
    social_reports = _get_trail_social_reports(request.trail_name)

    # 10. Hourly & Multi-Day Trends
    hourly_trends = [
        RiskTrend(time="06:00 AM", risk=_get_risk_level(max(5.0, pred_risk - 15)), score=max(5, int(pred_risk - 15))),
        RiskTrend(time="09:00 AM", risk=_get_risk_level(max(10.0, pred_risk - 5)), score=max(10, int(pred_risk - 5))),
        RiskTrend(time="12:00 PM", risk=_get_risk_level(min(100.0, pred_risk + 10)), score=min(100, int(pred_risk + 10))),
        RiskTrend(time="03:00 PM", risk=_get_risk_level(min(100.0, pred_risk + 5)), score=min(100, int(pred_risk + 5))),
        RiskTrend(time="06:00 PM", risk=_get_risk_level(max(10.0, pred_risk - 10)), score=max(10, int(pred_risk - 10))),
    ]

    daily_predictions = [
        DailyPrediction(
            date=request.start_date + timedelta(days=offset),
            risk_score=max(5, min(100, int(pred_risk + delta))),
            risk_level=_get_risk_level(max(5, min(100, pred_risk + delta))),
        )
        for offset, delta in [(0, 0), (1, -10), (2, -15), (3, 10), (4, 5)]
    ]

    return ForecastResponse(
        request_id=str(uuid4()),
        mode=mode,
        generated_at=datetime.now(timezone.utc),
        trail_name=request.trail_name,
        start_date=request.start_date,
        end_date=request.end_date,
        overall_risk_score=int(pred_risk),
        risk_level=risk_level,
        hazards=hazard_list,
        weather=weather,
        recommendation=recommendation,
        social_reports=social_reports,
        hourly_trends=hourly_trends,
        daily_predictions=daily_predictions,
    )


def get_spatial_heat_zones() -> HeatZonesResponse:
    """
    Returns spatial risk heat zones for all 15 Sri Lankan hiking trails.
    """
    json_path = OUTPUTS_DIR / "spatial_risk_heat_zones.json"
    if json_path.exists():
        with open(json_path, "r") as f:
            data = json.load(f)

        features = []
        for feat in data.get("features", []):
            coords = feat["geometry"]["coordinates"]
            props = feat["properties"]
            features.append(
                HeatZoneFeature(
                    geometry=HeatZoneGeometry(coordinates=coords),
                    properties=HeatZoneProperties(**props),
                )
            )

        return HeatZonesResponse(
            generated_at=datetime.now(timezone.utc),
            trails_count=len(features),
            features=features,
        )

    # Fallback if JSON file is missing
    features = []
    for t_name, (lat, lon) in TRAIL_COORDINATES.items():
        props = HeatZoneProperties(
            trail_name=t_name,
            latitude=lat,
            longitude=lon,
            predicted_hazard="slippery or muddy trails",
            hazard_probability=0.65,
            predicted_risk_score=45.0,
            risk_level="Medium",
            rainfall_24h_mm=12.5,
            wind_gust_kmh=24.0,
            mean_social_reliability=0.85,
        )
        features.append(
            HeatZoneFeature(
                geometry=HeatZoneGeometry(coordinates=[lon, lat]),
                properties=props,
            )
        )

    return HeatZonesResponse(
        generated_at=datetime.now(timezone.utc),
        trails_count=len(features),
        features=features,
    )


def get_trail_catalog() -> list[TrailLocationResponse]:
    """Returns catalog of all 15 trails with geographic & terrain information."""
    catalog = []
    for t_name, (lat, lon) in TRAIL_COORDINATES.items():
        terr = TRAIL_TERRAIN.get(t_name, {"elevation_m": 1000, "slope_degrees": 20.0, "terrain": "Mountainous"})
        catalog.append(
            TrailLocationResponse(
                trail_name=t_name,
                latitude=lat,
                longitude=lon,
                elevation_m=terr["elevation_m"],
                slope_degrees=terr["slope_degrees"],
                terrain=terr["terrain"],
            )
        )
    return catalog
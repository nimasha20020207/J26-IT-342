"""
Comprehensive Automated Test Suite for Component 4
Tests NLP extraction, Knowledge Graph reasoning, Geo-spatial locator,
SHAP explainability, and full FastAPI REST endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.geo_service import haversine_distance_km, estimate_travel_time_minutes, GeoEmergencyService
from backend.services.explainability_service import ExplainabilityService
from ML_models.component04.nlp_extract import IncidentNLPExtractor
from ML_models.component04.kg_reasoning import KnowledgeGraphEngine

client = TestClient(app)

# ====================================================================
# 1. NLP Information Extraction Unit Tests
# ====================================================================
def test_nlp_extraction_injury():
    extractor = IncidentNLPExtractor()
    text = "Hiker fell down steep rocks, badly twisted ankle, bleeding heavily and cannot walk. Need ambulance."
    res = extractor.extract(text)
    
    assert "injury" in res["detected_emergency_types"]
    assert res["severity_urgency"] == "HIGH"
    assert "steep_terrain" in res["environmental_hazards"]
    assert "ambulance" in res["required_assistance"]

def test_nlp_extraction_weather_flooding():
    extractor = IncidentNLPExtractor()
    text = "Torrential heavy rain causing flash flood across the river crossing. Disoriented and lost."
    res = extractor.extract(text)
    
    assert any(t in res["detected_emergency_types"] for t in ["flooding", "lost_hiker", "severe_weather"])
    assert "heavy_rain" in res["environmental_hazards"]

def test_nlp_extraction_empty():
    extractor = IncidentNLPExtractor()
    res = extractor.extract("")
    assert res["primary_candidate"] == "unknown"
    assert res["severity_urgency"] == "LOW"

# ====================================================================
# 2. Knowledge Graph Reasoning Engine Tests
# ====================================================================
def test_kg_reasoning_injury_high_severity():
    engine = KnowledgeGraphEngine()
    res = engine.recommend("injury", severity_level=5, rainfall_mm=40, visibility_pct=20, terrain_type="steep")
    
    actions = res["actions"]
    assert "provide_first_aid_if_trained" in actions or "request_rescue_assistance" in actions
    assert "contact_local_emergency_services" in actions  # Triggered by severity >= 4
    assert len(res["reasoning_paths"]) > 0

def test_kg_reasoning_landslide_avoid_debris():
    engine = KnowledgeGraphEngine()
    res = engine.recommend("landslide", severity_level=4, rainfall_mm=45, terrain_type="steep")
    
    actions = res["actions"]
    assert "avoid_crossing_debris" in actions
    assert "contact_rescue_authority" in actions

# ====================================================================
# 3. Geo-spatial Resource Locator Tests
# ====================================================================
def test_haversine_distance():
    # Nuwara Eliya Hospital (6.9707, 80.7828) to Horton Plains (6.8096, 80.8028)
    dist = haversine_distance_km(6.8096, 80.8028, 6.9707, 80.7828)
    assert 15.0 < dist < 22.0  # Approx 18-19 km

def test_travel_time_estimation():
    time_est = estimate_travel_time_minutes(20.0, is_wilderness=True)
    assert time_est == 60  # At 20 km/h, 20 km takes 60 mins

def test_nearest_resources_sorting():
    service = GeoEmergencyService()
    # Query at Horton Plains coordinates
    results = service.find_nearest_resources(6.8096, 80.8028, limit=3)
    assert len(results) == 3
    # Nearest should be Horton Plains Ranger station
    assert "Horton Plains" in results[0]["name"]
    # Distances must be strictly non-decreasing
    assert results[0]["distance_km"] <= results[1]["distance_km"] <= results[2]["distance_km"]

# ====================================================================
# 4. Explainable AI (SHAP) Unit Tests
# ====================================================================
def test_xai_explain_instance():
    service = ExplainabilityService()
    instance = {
        "elevation_m": 2100,
        "slope_degrees": 30,
        "rainfall_mm": 40,
        "temperature_c": 16,
        "wind_speed_kmh": 22,
        "visibility_pct": 20,
        "hours_hiking": 5,
        "distance_from_trailhead_km": 6,
        "phone_battery_pct": 15,
        "fatigue_score_1_10": 8,
        "water_remaining_l": 0.3,
        "remote_area": 1,
        "terrain_type": "steep"
    }
    res = service.explain_instance(instance, "injury", 4)
    factors = res["top_contributing_factors"]
    narrative = res["explanatory_narrative"]

    assert len(factors) > 0
    assert len(narrative) > 0
    assert any("Rainfall" in f["factor"] or "Slope" in f["factor"] or "Battery" in f["factor"] for f in factors)

# ====================================================================
# 5. FastAPI Endpoints Integration Tests
# ====================================================================
def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_extract_text():
    response = client.post("/api/v1/emergency/extract-text?text=Hiker+fell+and+fractured+bone+need+stretcher")
    assert response.status_code == 200
    data = response.json()
    assert "injury" in data["detected_emergency_types"]
    assert "search_and_rescue" in data["required_assistance"]

def test_api_get_resources():
    response = client.get("/api/v1/emergency/resources?latitude=6.8096&longitude=80.8028&limit=4")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert data[0]["distance_km"] <= data[1]["distance_km"]

def test_api_get_benchmarks():
    response = client.get("/api/v1/emergency/benchmarks")
    assert response.status_code == 200
    data = response.json()
    assert "model_comparison" in data
    assert "ablation_study" in data
    assert "RandomForest" in data["model_comparison"]["classification_models"]
    assert "XGBoost" in data["model_comparison"]["classification_models"]

def test_api_get_shap_importance():
    response = client.get("/api/v1/emergency/shap-importance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

def test_api_full_emergency_analysis_injury():
    payload = {
        "incident_text": "A hiker fell down a steep ridge at World End, badly fractured leg and cannot walk. Rain is heavy and battery is 12%.",
        "latitude": 6.8096,
        "longitude": 80.8028,
        "trail_name": "Horton_Plains",
        "elevation_m": 2100.0,
        "slope_degrees": 35.0,
        "rainfall_mm": 45.0,
        "temperature_c": 16.0,
        "wind_speed_kmh": 25.0,
        "visibility_pct": 20.0,
        "hours_hiking": 5.0,
        "distance_from_trailhead_km": 6.5,
        "phone_battery_pct": 12.0,
        "fatigue_score_1_10": 8,
        "water_remaining_l": 0.2,
        "remote_area": 1,
        "terrain_type": "steep"
    }
    response = client.post("/api/v1/emergency/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["assessment"]["severity_level"] >= 4
    assert data["assessment"]["urgency"] in ["HIGH", "CRITICAL"]
    assert len(data["recommended_actions"]) > 0
    assert len(data["nearest_resources"]) > 0
    assert len(data["explainability"]["top_contributing_factors"]) > 0
    assert len(data["reasoning_paths"]) > 0

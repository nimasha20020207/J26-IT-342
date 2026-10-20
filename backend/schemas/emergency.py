"""
Pydantic Schemas for Component 4: Emergency Detection & Response Recommendation
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class IncidentInput(BaseModel):
    incident_text: str = Field(
        default="A hiker slipped on steep rocks during heavy rain, suffering acute ankle trauma and cannot walk.",
        description="Unstructured text incident report or distress message"
    )
    latitude: float = Field(default=6.8096, description="User latitude (Sri Lanka)")
    longitude: float = Field(default=80.8028, description="User longitude (Sri Lanka)")
    trail_name: Optional[str] = Field(default="Horton_Plains", description="Known trail name if identified")
    elevation_m: float = Field(default=2100.0, description="Elevation in meters")
    slope_degrees: float = Field(default=28.0, description="Slope inclination in degrees")
    rainfall_mm: float = Field(default=35.0, description="Current rainfall intensity in mm")
    temperature_c: float = Field(default=16.0, description="Ambient temperature in Celsius")
    wind_speed_kmh: float = Field(default=22.0, description="Wind speed in km/h")
    visibility_pct: float = Field(default=25.0, description="Visibility percentage (0-100)")
    hours_hiking: float = Field(default=5.5, description="Hiking duration in hours")
    distance_from_trailhead_km: float = Field(default=6.8, description="Distance from starting trailhead in km")
    phone_battery_pct: float = Field(default=18.0, description="Hiker phone battery remaining percentage")
    fatigue_score_1_10: int = Field(default=7, ge=1, le=10, description="Subjective fatigue score (1-10)")
    water_remaining_l: float = Field(default=0.4, description="Remaining drinking water in liters")
    remote_area: int = Field(default=1, ge=0, le=1, description="1 if remote/poor cell reception, 0 otherwise")
    terrain_type: str = Field(default="rocky", description="steep, rocky, forest, ridge, grassland")

class NLPInformationExtraction(BaseModel):
    detected_emergency_types: List[str]
    primary_candidate: str
    severity_urgency: str
    environmental_hazards: List[str]
    required_assistance: List[str]
    confidence_score: float

class EmergencyAssessment(BaseModel):
    emergency_type: str
    display_title: str
    severity_level: int
    urgency: str
    confidence_pct: float
    requires_rescue: bool
    structured_prediction: str
    nlp_prediction: str

class RecommendedActionItem(BaseModel):
    action_id: str
    title: str
    priority: str
    urgency: str
    effectiveness_pct: int
    reasoning_path: Optional[str] = None
    is_primary: bool = False

class NearestResourceItem(BaseModel):
    id: str
    name: str
    type: str
    distance_km: float
    distance_str: str
    estimated_time_mins: int
    estimated_time_str: str
    phone: str
    latitude: float
    longitude: float
    services: List[str]

class XAIFactorItem(BaseModel):
    factor: str
    impact_percentage: float

class XAIExplanation(BaseModel):
    top_contributing_factors: List[XAIFactorItem]
    explanatory_narrative: List[str]
    model_type: str
    interpretability_framework: str

class ContextSummary(BaseModel):
    trail_name: Optional[str]
    coordinates: str
    weather: str
    terrain: str
    hiker_status: str
    remote_area: bool

class FullEmergencyAnalysisResponse(BaseModel):
    success: bool = True
    timestamp: str
    assessment: EmergencyAssessment
    nlp_extraction: NLPInformationExtraction
    recommended_actions: List[RecommendedActionItem]
    reasoning_paths: List[str]
    active_hazards: List[str]
    nearest_resources: List[NearestResourceItem]
    explainability: XAIExplanation
    context_summary: ContextSummary

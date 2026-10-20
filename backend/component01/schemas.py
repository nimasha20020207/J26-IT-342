from pydantic import BaseModel
from typing import List, Optional

class UserRegistrationRequest(BaseModel):
    name: str
    email: str
    age: int
    weight_kg: float
    height_cm: float
    resting_hr: int = 65
    experience_level: str
    has_medical_issue: bool = False
    medical_notes: Optional[str] = "None"
    preferred_max_hours: float = 6.0
    preferred_scenic: List[str] = ["Waterfalls", "Panoramic Mountain Views"]
    fitness_level: str = "Moderate"

class PeerFitnessSyncRequest(BaseModel):
    predicted_fitness_level: str
    resting_hr: Optional[int] = None
    source_model: str = "Component 3 Physiological Model"

class RecommendationRequest(BaseModel):
    fitness_level: Optional[str] = None
    preferred_scenic: Optional[List[str]] = None
    max_distance_km: Optional[float] = 30.0
    max_elevation_m: Optional[float] = 1500.0
    refresh_social: bool = False
    top_k: int = 5
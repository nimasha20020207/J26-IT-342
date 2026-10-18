from datetime import date, datetime
from typing import Any
from pydantic import BaseModel


class ForecastRequest(BaseModel):
    trail_name: str
    start_date: date
    end_date: date


class Hazard(BaseModel):
    name: str
    probability: float
    severity: str


class WeatherSummary(BaseModel):
    forecast_date: date
    source: str
    temperature_c: float
    feels_like_c: float
    condition: str
    rain_chance: int
    precipitation_mm: float
    wind_speed_kmh: float
    wind_gust_kmh: float
    humidity: int


class SocialReport(BaseModel):
    source: str
    type: str
    content: str
    time_ago: str
    reliability_score: float
    confidence_indicator: str


class RiskTrend(BaseModel):
    time: str
    risk: str
    score: int


class DailyPrediction(BaseModel):
    date: date
    risk_score: int
    risk_level: str


class Recommendation(BaseModel):
    action: str
    summary: str
    precautions: list[str]


class ForecastResponse(BaseModel):
    request_id: str
    mode: str
    generated_at: datetime
    trail_name: str
    start_date: date
    end_date: date
    overall_risk_score: int
    risk_level: str
    hazards: list[Hazard]
    weather: WeatherSummary
    recommendation: Recommendation
    social_reports: list[SocialReport]
    hourly_trends: list[RiskTrend]
    daily_predictions: list[DailyPrediction]


# -------------------------------------------------------------
# Spatial Heat-Zones & Trail Discovery Schemas
# -------------------------------------------------------------
class HeatZoneProperties(BaseModel):
    trail_name: str
    latitude: float
    longitude: float
    predicted_hazard: str
    hazard_probability: float
    predicted_risk_score: float
    risk_level: str
    rainfall_24h_mm: float
    wind_gust_kmh: float
    mean_social_reliability: float


class HeatZoneGeometry(BaseModel):
    type: str = "Point"
    coordinates: list[float]  # [longitude, latitude]


class HeatZoneFeature(BaseModel):
    type: str = "Feature"
    geometry: HeatZoneGeometry
    properties: HeatZoneProperties


class HeatZonesResponse(BaseModel):
    type: str = "FeatureCollection"
    generated_at: datetime
    trails_count: int
    features: list[HeatZoneFeature]


class TrailLocationResponse(BaseModel):
    trail_name: str
    latitude: float
    longitude: float
    elevation_m: int
    slope_degrees: float
    terrain: str
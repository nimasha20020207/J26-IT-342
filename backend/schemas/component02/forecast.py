from datetime import date, datetime

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
    temperature_c: float
    feels_like_c: float
    condition: str
    rain_chance: int
    wind_speed_kmh: int
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
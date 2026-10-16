from datetime import datetime, timedelta, timezone
from uuid import uuid4

from schemas.component02.forecast import ForecastRequest, ForecastResponse


def generate_demo_forecast(request: ForecastRequest) -> ForecastResponse:
    if request.end_date < request.start_date:
        raise ValueError("end_date must be on or after start_date")

    return ForecastResponse(
        request_id=str(uuid4()),
        mode="demo",
        generated_at=datetime.now(timezone.utc),
        trail_name=request.trail_name,
        start_date=request.start_date,
        end_date=request.end_date,
        overall_risk_score=68,
        risk_level="Medium",
        hazards=[
            {"name": "Landslides", "probability": 0.65, "severity": "Medium"},
            {"name": "Floods", "probability": 0.20, "severity": "Low"},
            {"name": "Slippery Trails", "probability": 0.85, "severity": "High"},
            {"name": "Rockfalls", "probability": 0.40, "severity": "Medium"},
            {"name": "Dense Fog", "probability": 0.90, "severity": "High"},
            {"name": "Lightning", "probability": 0.35, "severity": "Low"},
            {"name": "Forest Fires", "probability": 0.10, "severity": "Low"},
            {"name": "Wildlife Activity", "probability": 0.50, "severity": "Medium"},
            {"name": "High Leech Activity", "probability": 0.95, "severity": "High"},
        ],
        weather={
            "temperature_c": 18,
            "feels_like_c": 17,
            "condition": "Partly cloudy",
            "rain_chance": 30,
            "wind_speed_kmh": 12,
            "humidity": 82,
        },
        recommendation={
            "action": "Proceed with Caution",
            "summary": "Hike with heightened awareness. Expect slippery trails and heavy afternoon fog.",
            "precautions": [
                "Wear anti-leech socks and proper grip hiking boots.",
                "Carry rain gear and a portable emergency flashlight for fog.",
                "Complete the loop before 12:00 PM to avoid peak weather risks.",
            ],
        },
        social_reports=[
            {
                "source": "News Article (Daily News LK)",
                "type": "News",
                "content": "Heavy mist and sudden downpours reported across the plateau. Visitors advised caution.",
                "time_ago": "2 hours ago",
                "reliability_score": 0.94,
                "confidence_indicator": "High Confidence",
            },
            {
                "source": "Hiker Review (@kamal_hikes)",
                "type": "Hiker Report",
                "content": "Very slippery near the cliff. High leech activity near the forested trail segment.",
                "time_ago": "4 hours ago",
                "reliability_score": 0.88,
                "confidence_indicator": "Moderate Confidence",
            },
            {
                "source": "Local Guide Report",
                "type": "Hiker Report",
                "content": "A fallen branch blocks the secondary track. Main trail is clear but foggy.",
                "time_ago": "Yesterday",
                "reliability_score": 0.96,
                "confidence_indicator": "High Confidence",
            },
        ],
        hourly_trends=[
            {"time": "06:00 AM", "risk": "Low", "score": 35},
            {"time": "09:00 AM", "risk": "Medium", "score": 55},
            {"time": "12:00 PM", "risk": "High", "score": 78},
            {"time": "03:00 PM", "risk": "Medium", "score": 60},
        ],
        daily_predictions=[
            {
                "date": request.start_date + timedelta(days=offset),
                "risk_score": score,
                "risk_level": level,
            }
            for offset, score, level in [
                (0, 68, "Medium"),
                (1, 45, "Medium"),
                (2, 30, "Low"),
                (3, 72, "High"),
                (4, 50, "Medium"),
            ]
        ],
    )
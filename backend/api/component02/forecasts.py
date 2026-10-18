from datetime import date

from fastapi import APIRouter, HTTPException

from schemas.component02.forecast import (
    ForecastRequest,
    ForecastResponse,
    HeatZonesResponse,
    TrailLocationResponse,
    WeatherSummary,
)
from services.component02.forecast_service import (
    generate_live_forecast,
    get_spatial_heat_zones,
    get_trail_catalog,
)
from services.component02.weather_service import WeatherProviderError, get_trail_weather

router = APIRouter(tags=["Hazard Forecasting & Heat Zones"])


@router.post("/forecasts", response_model=ForecastResponse)
def create_forecast(request: ForecastRequest) -> ForecastResponse:
    """
    Generate reliability-aware hazard forecast for a trail using live weather
    and the trained Baseline 03 Adaptive Fusion Model.
    """
    try:
        return generate_live_forecast(request)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except WeatherProviderError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@router.get("/weather", response_model=WeatherSummary)
def get_weather(trail_name: str, forecast_date: date) -> WeatherSummary:
    """
    Retrieve real-time meteorological observations and Open-Meteo forecasts for a trail.
    """
    try:
        return get_trail_weather(trail_name, forecast_date)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except WeatherProviderError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@router.get("/forecasts/heat-zones", response_model=HeatZonesResponse)
def get_heat_zones() -> HeatZonesResponse:
    """
    Retrieve spatial risk heat zones and GeoJSON features across all 15 Sri Lankan hiking trails
    for visualization in the Flutter mobile application map.
    """
    try:
        return get_spatial_heat_zones()
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Could not load spatial heat zones: {error}") from error


@router.get("/trails", response_model=list[TrailLocationResponse])
def get_trails() -> list[TrailLocationResponse]:
    """
    Retrieve the directory of all 15 monitored hiking trails with terrain metadata.
    """
    return get_trail_catalog()
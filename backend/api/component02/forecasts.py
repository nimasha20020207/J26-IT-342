from datetime import date

from fastapi import APIRouter, HTTPException

from schemas.component02.forecast import ForecastRequest, ForecastResponse, WeatherSummary
from services.component02.forecast_service import generate_demo_forecast
from services.component02.weather_service import WeatherProviderError, get_trail_weather

router = APIRouter()


@router.post("/forecasts", response_model=ForecastResponse)
def create_forecast(request: ForecastRequest) -> ForecastResponse:
    try:
        return generate_demo_forecast(request)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except WeatherProviderError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@router.get("/weather", response_model=WeatherSummary)
def get_weather(trail_name: str, forecast_date: date) -> WeatherSummary:
    try:
        return get_trail_weather(trail_name, forecast_date)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except WeatherProviderError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
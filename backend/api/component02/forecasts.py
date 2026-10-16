from fastapi import APIRouter, HTTPException

from schemas.component02.forecast import ForecastRequest, ForecastResponse
from services.component02.forecast_service import generate_demo_forecast

router = APIRouter()


@router.post("/forecasts", response_model=ForecastResponse)
def create_forecast(request: ForecastRequest) -> ForecastResponse:
    try:
        return generate_demo_forecast(request)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
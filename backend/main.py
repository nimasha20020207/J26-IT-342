from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.component02.forecasts import router as forecasts_router
from database import get_db

app = FastAPI(
    title="Venture Hazard Forecasting & Decision Support API",
    description="Backend API for Component 02: Reliability-Aware Environmental Hazard Forecasting & Spatial Heat Zones",
    version="1.0.0",
)

# Enable CORS for Flutter mobile application & local dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Component 02 Hazard Forecasting & Spatial Heat-Zones Router
app.include_router(forecasts_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def home():
    return {
        "message": "Venture Mobile Application Backend Running",
        "service": "Component 02 - Reliability-Aware Hazard Forecasting",
        "status": "online",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


@app.get("/db-check", tags=["Health"])
def db_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "connected", "database": "healthy"}
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database unreachable or uninitialized: {error}",
        ) from error
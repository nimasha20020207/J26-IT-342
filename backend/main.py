"""
Venture Multi-Modal AI Hiking Safety Platform - Unified Backend
Component 4: Context-Aware Emergency Detection and Response Recommendation System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.emergency import router as emergency_router

app = FastAPI(
    title="Venture Hiking Safety Platform - Emergency Decision Support System",
    description=(
        "Component 4: Context-Aware Emergency Detection and Response Recommendation System. "
        "Provides multi-class emergency classification, severity estimation, NLP incident extraction, "
        "knowledge graph reasoning, SHAP explainability, and Sri Lanka emergency resource mapping."
    ),
    version="1.0.0"
)

# Enable CORS for Flutter mobile app, local emulators, web, and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Component 4 Router
app.include_router(emergency_router)

@app.get("/", tags=["Health"])
def root():
    return {
        "platform": "Venture Hiking Safety Platform",
        "component": "Component 4: Context-Aware Emergency Detection & Response Recommendation System",
        "status": "online",
        "docs_url": "/docs",
        "api_prefix": "/api/v1/emergency"
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "services": {
            "emergency_decision_engine": "operational",
            "knowledge_graph": "active",
            "nlp_extractor": "active",
            "geospatial_locator": "active",
            "xai_shap": "active"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
"""
Component 4 FastAPI Service Bridge
Exposes the complete multi-modal decision support system for Component 4.
Run with: uvicorn ML_models.component04.api:app --reload --port 8000
Or: uvicorn backend.main:app --reload --port 8000
"""
from pathlib import Path
import sys

# Ensure repository root is in python path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ML_models.component04.api:app", host="0.0.0.0", port=8000, reload=True)

"""
generate_spatial_risk.py
------------------------
Component 02: Spatial Risk Heat-Zone and Trail Forecast Generator

Applies the trained Proposed Adaptive Fusion Model (Baseline 03) across all 15
monitored Sri Lankan hiking trails to generate:
1. Trail-specific predicted hazard category
2. Hazard occurrence probability and risk score (0-100)
3. Risk level categorization (Low, Medium, High, Very High)
4. Geospatial heat zone output (CSV and GeoJSON-ready format) for the
   FastAPI backend and Flutter map visualization.
"""

import json
from pathlib import Path
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
MODELS_DIR = ROOT / "models" / "saved_baselines"

B3_DATASET_FILE = OUTPUT_DIR / "dataset_baseline3_adaptive.csv"
WEATHER_DAILY_FILE = OUTPUT_DIR / "weather_daily_features.csv"
TRAIL_TERRAIN_FILE = ROOT / "data" / "trail_terrain.xlsx"


def get_risk_level(score: float) -> str:
    if score >= 75:
        return "Very High"
    elif score >= 50:
        return "High"
    elif score >= 25:
        return "Medium"
    else:
        return "Low"


def generate_spatial_risk_heat_zones():
    print("=" * 65)
    print("SPATIAL RISK HEAT-ZONE GENERATOR (FOR FASTAPI & FLUTTER APP)")
    print("=" * 65)

    clf_path = MODELS_DIR / "baseline_03_hazard_classifier.pkl"
    reg_path = MODELS_DIR / "baseline_03_risk_regressor.pkl"
    le_path = MODELS_DIR / "label_encoder.pkl"

    if not clf_path.exists() or not reg_path.exists():
        raise FileNotFoundError("Trained Baseline 03 models not found. Run train_baseline_models.py first.")

    clf = joblib.load(clf_path)
    reg = joblib.load(reg_path)
    le = joblib.load(le_path)

    # Load latest feature set for all 15 trails from dataset_baseline3_adaptive.csv
    b3_df = pd.read_csv(B3_DATASET_FILE, low_memory=False)

    # Take the latest observation for each unique trail
    latest_per_trail = b3_df.sort_values(by="date").groupby("trail_name").last().reset_index()
    print(f"Loaded latest feature profiles for {len(latest_per_trail)} hiking trails.")

    # Exclude metadata columns
    exclude_cols = [
        "date",
        "trail_name",
        "hazard_type",
        "severity",
        "risk_score",
        "is_hazard",
        "split",
    ]
    feature_cols = [c for c in b3_df.columns if c not in exclude_cols]

    X = latest_per_trail[feature_cols].fillna(0)

    # Predict hazard categories and risk scores
    pred_cats_idx = clf.predict(X)
    pred_cats = le.inverse_transform(pred_cats_idx)
    pred_probs = clf.predict_proba(X).max(axis=1)
    pred_risk_scores = reg.predict(X).clip(0, 100).round(1)

    latest_per_trail["predicted_hazard"] = pred_cats
    latest_per_trail["hazard_probability"] = pred_probs.round(3)
    latest_per_trail["predicted_risk_score"] = pred_risk_scores
    latest_per_trail["risk_level"] = latest_per_trail["predicted_risk_score"].apply(get_risk_level)

    # Load trail coordinates
    trail_coords = {
        "Pidurangala": (7.9658, 80.7624),
        "Sigiriya": (7.9569, 80.7597),
        "Alagalla": (7.2842, 80.4772),
        "Narangala": (7.0289, 80.9968),
        "Hanthana": (7.2287, 80.6384),
        "Lakegala": (7.4578, 80.8847),
        "Manigala": (7.5250, 80.7300),
        "Kirigalpoththa": (6.7972, 80.7811),
        "Little Adam's peak": (6.8622, 81.0556),
        "Pettigala": (6.7028, 80.6558),
        "Peacock hills": (7.1083, 80.6358),
        "Thotupala kanda": (6.8333, 80.8167),
        "Bathalegala": (7.1856, 80.4411),
        "Adam's peak": (6.8094, 80.4994),
        "Ella rock": (6.8536, 81.0450),
    }

    spatial_records = []
    geojson_features = []

    for _, row in latest_per_trail.iterrows():
        t_name = row["trail_name"]
        lat, lon = trail_coords.get(t_name, (7.0, 80.5))

        rec = {
            "trail_name": t_name,
            "latitude": lat,
            "longitude": lon,
            "predicted_hazard": row["predicted_hazard"],
            "hazard_probability": float(row["hazard_probability"]),
            "predicted_risk_score": float(row["predicted_risk_score"]),
            "risk_level": row["risk_level"],
            "rainfall_24h_mm": float(row.get("rainfall_24h_max_mm", 0.0)),
            "wind_gust_kmh": float(row.get("wind_gust_max_kmh", 0.0)),
            "mean_social_reliability": float(row.get("mean_reliability_score", 0.0)),
        }
        spatial_records.append(rec)

        geojson_features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": rec,
        })

    spatial_df = pd.DataFrame(spatial_records)
    out_csv = OUTPUT_DIR / "spatial_risk_heat_zones.csv"
    out_json = OUTPUT_DIR / "spatial_risk_heat_zones.json"

    spatial_df.to_csv(out_csv, index=False)
    with open(out_json, "w") as f:
        json.dump({
            "type": "FeatureCollection",
            "trails_count": len(spatial_records),
            "features": geojson_features,
        }, f, indent=2)

    print(f"\nSaved spatial risk heat zones to:")
    print(f"  - {out_csv.name}")
    print(f"  - {out_json.name}")

    print("\nSummary of Predicted Trail Risks across Sri Lanka:")
    print(spatial_df[["trail_name", "predicted_hazard", "predicted_risk_score", "risk_level"]].to_string(index=False))


if __name__ == "__main__":
    generate_spatial_risk_heat_zones()

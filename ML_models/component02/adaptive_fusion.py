"""
adaptive_fusion.py
------------------
Component 02: Adaptive Reliability-Aware Multi-Source Fusion Module

Merges:
1. Environmental & Terrain features (Weather features + Physical rule baselines)
2. Historical Hazard Ground Truth (100 confirmed events + non-hazard calm days)
3. Social Signal Intelligence (Raw NLP scores vs. Reliability-weighted scores)

Produces 3 distinct baseline datasets according to Table 3.3 of the Research Proposal:
- Baseline 1: Environmental Only (no social features)
- Baseline 2: Fixed Multi-Source Fusion (raw unweighted social features, static equal fusion)
- Baseline 3: Reliability-Aware Adaptive Multi-Source Fusion (dynamic reliability weighting)

Also creates a chronological (time-aware) train/validation/test split
to eliminate temporal data leakage.
"""

from pathlib import Path
import numpy as np
import pandas as pd

# Paths
ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"

HIST_FILE = OUTPUT_DIR / "historical_hazards_integrated.csv"
WEATHER_DAILY_FILE = OUTPUT_DIR / "weather_daily_features.csv"
BASELINE_DAILY_FILE = OUTPUT_DIR / "baseline_daily_by_hazard.csv"
SOCIAL_MATRIX_FILE = OUTPUT_DIR / "trail_social_hazard_matrix.csv"

# Canonical hazard categories
ALL_HAZARDS = [
    "slippery or muddy trails",
    "landslides",
    "dense fog or poor visibility",
    "rockfalls",
    "high leech activity",
    "strong winds",
    "trail obstructions",
    "monkey sightings",
    "bugs or wasps activity",
    "heavy rain",
]

# Core Environmental & Terrain Feature Columns
ENV_NUMERIC_FEATURES = [
    "temperature_mean_c",
    "temperature_max_c",
    "relative_humidity_mean_pct",
    "dew_point_depression_min_c",
    "precipitation_sum_mm",
    "rainfall_24h_max_mm",
    "wind_speed_mean_kmh",
    "wind_gust_max_kmh",
    "elevation_m",
    "slope_degrees",
]


def load_and_prepare_evaluation_samples():
    """
    Combines the 100 positive historical hazard events with 100 sampled calm/non-hazard
    days from the daily weather observation baseline to form a 200-sample balanced dataset.
    """
    print("\n--- 1. Loading Integrated Datasets ---")
    hist_df = pd.read_csv(HIST_FILE, low_memory=False)
    weather_df = pd.read_csv(WEATHER_DAILY_FILE, low_memory=False)
    social_df = pd.read_csv(SOCIAL_MATRIX_FILE, low_memory=False)

    print(f"Loaded {len(hist_df)} historical hazard events.")
    print(f"Loaded {len(weather_df)} daily weather records across {weather_df['trail_name'].nunique()} trails.")
    print(f"Loaded social hazard profiles for {len(social_df)} trails.")

    # Positive samples: 100 historical hazard events
    positives = hist_df.copy()
    positives["is_hazard"] = 1
    if "hazard_type" not in positives.columns and "hazard_key" in positives.columns:
        positives["hazard_type"] = positives["hazard_key"]

    # Negative samples: Sample non-hazard days from weather_df where no hazard occurred
    # Exclude dates that already have an event on that trail
    event_trail_dates = set(zip(positives["trail_name"], positives["date"]))

    weather_df["date"] = weather_df["date_key"]
    candidate_negatives = weather_df[
        ~weather_df.apply(lambda r: (r["trail_name"], r["date"]) in event_trail_dates, axis=1)
    ].copy()

    # Filter for relatively calm days (low rainfall, moderate wind) for realistic negatives
    calm_negatives = candidate_negatives[
        (candidate_negatives["rainfall_24h_max_mm"] <= 2.0)
        & (candidate_negatives["wind_gust_max_kmh"] <= 25.0)
    ]
    if len(calm_negatives) < 100:
        calm_negatives = candidate_negatives

    sampled_negatives = calm_negatives.sample(n=100, random_state=42).copy()
    sampled_negatives["hazard_type"] = "no relevant hiking hazard"
    sampled_negatives["severity"] = "None"
    sampled_negatives["risk_score"] = 0
    sampled_negatives["is_hazard"] = 0
    sampled_negatives["rule_triggered_hours"] = 0
    sampled_negatives["daily_rule_status"] = "RULE_NOT_TRIGGERED"

    # Align columns between positives and sampled negatives
    common_cols = [c for c in positives.columns if c in sampled_negatives.columns]
    full_dataset = pd.concat([positives[common_cols], sampled_negatives[common_cols]], ignore_index=True)

    # Sort chronologically for time-aware splitting
    full_dataset["date"] = pd.to_datetime(full_dataset["date"])
    full_dataset = full_dataset.sort_values(by=["date", "trail_name"]).reset_index(drop=True)

    print(f"\nFormed balanced evaluation dataset: {len(full_dataset)} total samples "
          f"({(full_dataset['is_hazard'] == 1).sum()} hazards, "
          f"{(full_dataset['is_hazard'] == 0).sum()} calm non-hazards).")

    # Merge social features by trail_name
    merged = pd.merge(full_dataset, social_df, on="trail_name", how="left")
    return merged


def build_baseline_datasets(df: pd.DataFrame):
    """
    Constructs the feature matrices for Baseline 1, Baseline 2, and Baseline 3.
    """
    print("\n--- 2. Engineering Features for Baselines 1, 2, and 3 ---")

    # Clean numeric features
    for col in ENV_NUMERIC_FEATURES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(df[col].median())
        else:
            df[col] = 0.0

    # Fill slope and aspect if missing
    df["slope_degrees"] = df["slope_degrees"].fillna(15.0)
    df["rule_triggered_hours"] = pd.to_numeric(df.get("rule_triggered_hours", 0), errors="coerce").fillna(0)

    # -----------------------------------------------------------------
    # Compute Environmental Extremity Factor (E_env in [0, 1])
    # -----------------------------------------------------------------
    # Normalized extremity index from rainfall, wind, and rule trigger
    rain_norm = (df["rainfall_24h_max_mm"] / 100.0).clip(0, 1)
    wind_norm = (df["wind_gust_max_kmh"] / 60.0).clip(0, 1)
    rule_norm = (df["rule_triggered_hours"] / 24.0).clip(0, 1)
    df["environmental_extremity"] = (0.5 * rain_norm + 0.25 * wind_norm + 0.25 * rule_norm).clip(0, 1)

    # -----------------------------------------------------------------
    # Adaptive Dynamic Weighting (for Baseline 3)
    # -----------------------------------------------------------------
    # Social reliability factor
    r_social = df["mean_reliability_score"].fillna(0.50).clip(0, 1)
    e_env = df["environmental_extremity"]

    # When reliability is high and weather is not extreme, social intelligence adds strong value.
    # When physical weather is catastrophic (e.g. flash deluge), physical sensor weights dominate.
    w_social = (0.40 * r_social * (1.0 - 0.50 * e_env)).clip(0.05, 0.45)
    w_env = 1.0 - w_social

    df["adaptive_weight_env"] = w_env
    df["adaptive_weight_social"] = w_social

    # -----------------------------------------------------------------
    # Fused Hazard Indicators
    # -----------------------------------------------------------------
    raw_social_cols = [f"raw_social_{h}" for h in ALL_HAZARDS if f"raw_social_{h}" in df.columns]
    rel_social_cols = [f"rel_social_{h}" for h in ALL_HAZARDS if f"rel_social_{h}" in df.columns]

    for col in raw_social_cols + rel_social_cols:
        df[col] = df[col].fillna(0.0)

    # Compute Baseline 3 Fused Risk Features per Hazard
    for h in ALL_HAZARDS:
        raw_col = f"raw_social_{h}"
        rel_col = f"rel_social_{h}"
        fused_col = f"fused_risk_{h}"

        rel_val = df[rel_col] if rel_col in df.columns else 0.0
        # Environmental proxy: rainfall / humidity / wind proxy depending on hazard
        if h in ["slippery or muddy trails", "landslides", "heavy rain"]:
            env_proxy = rain_norm
        elif h in ["dense fog or poor visibility"]:
            env_proxy = (df["relative_humidity_mean_pct"] / 100.0).clip(0, 1)
        elif h in ["strong winds"]:
            env_proxy = wind_norm
        else:
            env_proxy = rule_norm

        # Adaptive fusion: weighted blend
        df[fused_col] = df["adaptive_weight_env"] * env_proxy + df["adaptive_weight_social"] * rel_val

    # -----------------------------------------------------------------
    # Define Target Labels
    # -----------------------------------------------------------------
    target_cols = ["date", "trail_name", "hazard_type", "severity", "risk_score", "is_hazard"]

    # 1. Baseline 1: Environmental Only
    b1_features = ENV_NUMERIC_FEATURES + ["rule_triggered_hours", "environmental_extremity"]
    b1_df = df[target_cols + b1_features].copy()

    # 2. Baseline 2: Fixed Multi-Source Fusion (Unweighted Social Concatenation)
    b2_features = b1_features + raw_social_cols + ["social_mention_count"]
    b2_df = df[target_cols + b2_features].copy()

    # 3. Baseline 3: Proposed Reliability-Aware Adaptive Fusion
    fused_risk_cols = [f"fused_risk_{h}" for h in ALL_HAZARDS]
    b3_features = b1_features + rel_social_cols + fused_risk_cols + [
        "mean_reliability_score",
        "mean_source_credibility",
        "adaptive_weight_env",
        "adaptive_weight_social",
    ]
    b3_df = df[target_cols + b3_features].copy()

    # -----------------------------------------------------------------
    # Time-Aware Train / Test Split (Cutoff at 2025-07-31)
    # -----------------------------------------------------------------
    cutoff_date = pd.to_datetime("2025-07-31")
    df["split"] = np.where(df["date"] <= cutoff_date, "train", "test")
    b1_df["split"] = df["split"]
    b2_df["split"] = df["split"]
    b3_df["split"] = df["split"]

    print("\nTime-Aware Split Summary:")
    print(df["split"].value_counts().to_string())

    # Save to outputs
    b1_path = OUTPUT_DIR / "dataset_baseline1_env.csv"
    b2_path = OUTPUT_DIR / "dataset_baseline2_fixed.csv"
    b3_path = OUTPUT_DIR / "dataset_baseline3_adaptive.csv"

    b1_df.to_csv(b1_path, index=False)
    b2_df.to_csv(b2_path, index=False)
    b3_df.to_csv(b3_path, index=False)

    print(f"\nSaved Baseline 1 dataset ({b1_df.shape[1]} cols): {b1_path.name}")
    print(f"Saved Baseline 2 dataset ({b2_df.shape[1]} cols): {b2_path.name}")
    print(f"Saved Baseline 3 dataset ({b3_df.shape[1]} cols): {b3_path.name}")

    return b1_df, b2_df, b3_df


def main():
    print("=" * 65)
    print("ADAPTIVE MULTI-SOURCE FUSION PIPELINE")
    print("=" * 65)
    df = load_and_prepare_evaluation_samples()
    build_baseline_datasets(df)
    print("\nFusion pipeline complete. Ready for baseline model evaluation.")


if __name__ == "__main__":
    main()

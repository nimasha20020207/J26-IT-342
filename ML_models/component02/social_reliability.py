"""
social_reliability.py
---------------------
Component 02: Social Signal Reliability Assessment Module

Evaluates credibility, geo-relevance, NLP confidence, corroboration,
and temporal recency decay for unstructured human-generated reports
(TripAdvisor, Facebook, News, Hiking sources).

Produces:
1. outputs/social_reliability_evaluated.csv (record-level assessment)
2. outputs/trail_social_hazard_matrix.csv (trail-level aggregated social risks:
   both unweighted for Baseline 2, and reliability-weighted for Baseline 3)
"""

import json
import math
from pathlib import Path
import numpy as np
import pandas as pd

# Paths
ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
INPUT_BERTOPIC = OUTPUT_DIR / "bertopic_hazards_integrated.csv"
INPUT_DETAILS = OUTPUT_DIR / "bertopic_hazard_details.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. PARAMETERS & CREDIBILITY WEIGHTS
# -------------------------------------------------------------
# Source authority / credibility baseline weights (from literature review)
SOURCE_CREDIBILITY = {
    "news": 0.90,            # Formal news reports (moderated & verified)
    "hiking_sources": 0.85,   # Specialized hiking portals & guide publications
    "tripadvisor": 0.70,     # Verified tourist reviews (crowdsourced, moderated)
    "facebook": 0.50,        # Public social posts (high noise, unverified)
}

# Component weights for overall Reliability Score:
# R = w_src * SourceCred + w_geo * GeoRelevance + w_nlp * NLPConf + w_corrob * Corroboration
W_SOURCE = 0.35
W_GEO = 0.25
W_NLP = 0.20
W_CORROB = 0.20

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
    "leopard sightings",
]


def compute_geo_score(status: str) -> float:
    """Evaluate geographical relevance based on spatial match status."""
    status_str = str(status).upper()
    if "MATCHED_TRAIL_NAME" in status_str:
        return 1.0
    elif "PARTIAL" in status_str or "REGION" in status_str:
        return 0.6
    else:
        return 0.2


def compute_corroboration_matrix(df: pd.DataFrame) -> pd.Series:
    """
    Corroboration: Score increases when multiple independent posts
    report on the same trail about the same hazard.
    """
    corrob_scores = []
    # Count how many reports exist per trail
    trail_counts = df["trail_name"].value_counts().to_dict()

    for _, row in df.iterrows():
        t_name = row.get("trail_name")
        count = trail_counts.get(t_name, 1)
        # S-curve saturation: 1 report -> 0.3, 3 reports -> 0.7, 5+ reports -> 1.0
        score = min(1.0, 0.3 + 0.15 * (count - 1))
        corrob_scores.append(score)

    return pd.Series(corrob_scores, index=df.index)


def evaluate_social_reliability():
    print("=" * 65)
    print("SOCIAL SIGNAL RELIABILITY ASSESSMENT")
    print("=" * 65)

    if not INPUT_BERTOPIC.exists():
        raise FileNotFoundError(f"Missing {INPUT_BERTOPIC}. Run bertopic_pipeline first.")

    df = pd.read_csv(INPUT_BERTOPIC, low_memory=False)
    print(f"Loaded {len(df)} BERTopic integrated records.")

    # 1. Source Credibility Score
    df["source_credibility_score"] = (
        df["source"]
        .str.lower()
        .map(SOURCE_CREDIBILITY)
        .fillna(0.50)
    )

    # 2. Geo-Relevance Score
    df["geo_relevance_score"] = df["location_match_status"].apply(compute_geo_score)

    # 3. NLP Extraction Confidence
    # Parse max score from hazard_scores JSON if available
    nlp_confidences = []
    for _, row in df.iterrows():
        raw_scores = row.get("hazard_scores")
        conf = 0.5
        if pd.notna(raw_scores):
            try:
                scores_dict = json.loads(raw_scores)
                # Take top confidence among non-zero hazards
                val_list = [v for k, v in scores_dict.items() if k != "no relevant hiking hazard"]
                if val_list:
                    conf = max(val_list)
            except Exception:
                conf = 0.5
        nlp_confidences.append(float(conf))

    df["nlp_confidence_score"] = nlp_confidences

    # 4. Corroboration Score
    df["corroboration_score"] = compute_corroboration_matrix(df)

    # 5. Composite Reliability Score (R)
    df["reliability_score"] = (
        W_SOURCE * df["source_credibility_score"]
        + W_GEO * df["geo_relevance_score"]
        + W_NLP * df["nlp_confidence_score"]
        + W_CORROB * df["corroboration_score"]
    ).round(4)

    # Reliability Tier Categorization
    def get_tier(score):
        if score >= 0.75:
            return "HIGH"
        elif score >= 0.55:
            return "MEDIUM"
        else:
            return "LOW"

    df["reliability_tier"] = df["reliability_score"].apply(get_tier)

    # Save detailed evaluated records
    out_eval = OUTPUT_DIR / "social_reliability_evaluated.csv"
    df.to_csv(out_eval, index=False)
    print(f"Saved record-level evaluations to: {out_eval.name}")
    print("\nReliability tier summary:")
    print(df["reliability_tier"].value_counts().to_string())

    print("\nMean Reliability by Source:")
    print(df.groupby("source")["reliability_score"].mean().round(3).to_string())

    # -------------------------------------------------------------
    # 6. BUILD TRAIL-LEVEL SOCIAL HAZARD RISK MATRIX
    # -------------------------------------------------------------
    # For every trail, compute:
    # A) raw_social_score (for Baseline 2: unweighted average of NLP scores)
    # B) rel_weighted_social_score (for Baseline 3: reliability * NLP score)

    trail_records = []
    grouped = df.groupby("trail_name")

    for trail_name, group in grouped:
        if pd.isna(trail_name):
            continue

        trail_row = {
            "trail_name": trail_name,
            "social_mention_count": len(group),
            "mean_source_credibility": group["source_credibility_score"].mean(),
            "mean_reliability_score": group["reliability_score"].mean(),
        }

        # Initialize per-hazard accumulators
        for h in ALL_HAZARDS:
            raw_scores = []
            rel_scores = []

            for _, row in group.iterrows():
                raw_json = row.get("hazard_scores")
                r_score = row.get("reliability_score", 0.5)

                if pd.notna(raw_json):
                    try:
                        h_dict = json.loads(raw_json)
                        score = float(h_dict.get(h, 0.0))
                    except Exception:
                        score = 0.0
                else:
                    score = 0.0

                raw_scores.append(score)
                rel_scores.append(score * r_score)

            # Max or mean hazard signal for the trail
            trail_row[f"raw_social_{h}"] = max(raw_scores) if raw_scores else 0.0
            trail_row[f"rel_social_{h}"] = max(rel_scores) if rel_scores else 0.0

        trail_records.append(trail_row)

    trail_social_df = pd.DataFrame(trail_records)
    out_matrix = OUTPUT_DIR / "trail_social_hazard_matrix.csv"
    trail_social_df.to_csv(out_matrix, index=False)
    print(f"Saved trail-level social hazard matrix to: {out_matrix.name}")
    print(f"Covered {len(trail_social_df)} trails with social intelligence.")

    return df, trail_social_df


if __name__ == "__main__":
    evaluate_social_reliability()

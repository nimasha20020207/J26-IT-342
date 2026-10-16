
from pathlib import Path
import json

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

FEATURE_FILE = OUTPUT_DIR / "weather_features.csv"
CONFIG_FILE = BASE_DIR / "weather_rule_config.json"
OUTPUT_FILE = OUTPUT_DIR / "weather_rule_baseline.csv"


def get_value(row, column):
    value = row.get(column, None)

    if value is None or pd.isna(value):
        return None

    return float(value)


def all_present(row, columns):
    return all(get_value(row, col) is not None for col in columns)


def assess_landslide(row, rules):
    required = [
        "rainfall_24h_mm",
        "rainfall_72h_mm",
        "slope_degrees",
    ]

    thresholds = [
        rules.get("rainfall_24h_threshold_mm"),
        rules.get("rainfall_72h_threshold_mm"),
        rules.get("minimum_slope_degrees"),
    ]

    if any(value is None for value in thresholds):
        return "NOT_CONFIGURED"

    if not all_present(row, required):
        return "INSUFFICIENT_DATA"

    triggered = (
        get_value(row, "rainfall_24h_mm") >= thresholds[0]
        and get_value(row, "rainfall_72h_mm") >= thresholds[1]
        and get_value(row, "slope_degrees") >= thresholds[2]
    )

    return "RULE_TRIGGERED" if triggered else "RULE_NOT_TRIGGERED"


def assess_slippery_trail(row, rules):
    required = ["rainfall_3h_mm", "rainfall_24h_mm"]

    thresholds = [
        rules.get("rainfall_3h_threshold_mm"),
        rules.get("rainfall_24h_threshold_mm"),
    ]

    if any(value is None for value in thresholds):
        return "NOT_CONFIGURED"

    if not all_present(row, required):
        return "INSUFFICIENT_DATA"

    triggered = (
        get_value(row, "rainfall_3h_mm") >= thresholds[0]
        or get_value(row, "rainfall_24h_mm") >= thresholds[1]
    )

    return "RULE_TRIGGERED" if triggered else "RULE_NOT_TRIGGERED"


def assess_dense_fog(row, rules):
    threshold = rules.get("maximum_visibility_m")

    if threshold is None:
        return "NOT_CONFIGURED"

    visibility = get_value(row, "visibility_m")

    if visibility is None:
        return "INSUFFICIENT_DATA"

    triggered = visibility <= threshold

    return "RULE_TRIGGERED" if triggered else "RULE_NOT_TRIGGERED"


def assess_strong_wind(row, rules):
    threshold = rules.get("wind_gust_threshold_kmh")

    if threshold is None:
        return "NOT_CONFIGURED"

    gust = get_value(row, "wind_gust_kmh")

    if gust is None:
        return "INSUFFICIENT_DATA"

    triggered = gust >= threshold

    return "RULE_TRIGGERED" if triggered else "RULE_NOT_TRIGGERED"


def main():
    if not FEATURE_FILE.exists():
        raise FileNotFoundError(
            f"Missing {FEATURE_FILE}. Run "
            "weather_feature_engineering.py first."
        )

    features = pd.read_csv(FEATURE_FILE)

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    rules = config["rules"]

    features["landslide_rule"] = features.apply(
        lambda row: assess_landslide(
            row, rules["landslide"]
        ),
        axis=1,
    )

    features["slippery_trail_rule"] = features.apply(
        lambda row: assess_slippery_trail(
            row, rules["slippery_trail"]
        ),
        axis=1,
    )

    features["dense_fog_rule"] = features.apply(
        lambda row: assess_dense_fog(
            row, rules["dense_fog"]
        ),
        axis=1,
    )

    features["strong_wind_rule"] = features.apply(
        lambda row: assess_strong_wind(
            row, rules["strong_wind"]
        ),
        axis=1,
    )

    features["baseline_type"] = "weather_rule_baseline"
    features["probability_of_occurrence"] = pd.NA

    features.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved rule results to: {OUTPUT_FILE}")
    print("\nRule status counts:")

    for column in [
        "landslide_rule",
        "slippery_trail_rule",
        "dense_fog_rule",
        "strong_wind_rule",
    ]:
        print(f"\n{column}")
        print(features[column].value_counts(dropna=False))

    print(
        "\nNote: rule status is not a calibrated probability "
        "of hazard occurrence."
    )


if __name__ == "__main__":
    main()

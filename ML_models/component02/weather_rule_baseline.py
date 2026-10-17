
from pathlib import Path
import json

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

FEATURE_FILE = OUTPUT_DIR / "weather_features.csv"
CONFIG_FILE = BASE_DIR / "weather_rule_config.json"
CONFIG_FALLBACK_FILE = BASE_DIR / "weather_rule_config.py"
OUTPUT_FILE = OUTPUT_DIR / "weather_rule_baseline.csv"

BASELINE_TYPE = "weather_rule_baseline"

# Shared hazard taxonomy used across the Venture project.
HAZARD_CATEGORIES = [
    "landslide or slope failure",
    "flooding or flash flood",
    "slippery trail or muddy ground",
    "rockfall or falling rocks",
    "fallen trees or branches",
    "heavy rainfall",
    "lightning or thunderstorm",
    "dense fog or poor visibility",
    "forest fire or wildfire",
    "leech activity",
    "dangerous wildlife encounter",
    "strong winds",
    "extreme heat or heat stress",
    "river crossing danger",
    "trail erosion or trail collapse",
    "blocked trail or other trail obstruction",
    "navigation difficulty or getting lost",
    "no relevant hiking hazard",
]

# Only these four categories have assessment functions in this baseline.
CATEGORY_TO_RULE = {
    "landslide or slope failure": "landslide",
    "slippery trail or muddy ground": "slippery_trail",
    "dense fog or poor visibility": "dense_fog",
    "strong winds": "strong_wind",
}

# Each entry maps a configuration threshold to its input feature.
RULE_CONDITIONS = {
    "landslide": [
        ("rainfall_24h_threshold_mm", "rainfall_24h_mm", "min"),
        ("rainfall_72h_threshold_mm", "rainfall_72h_mm", "min"),
        ("minimum_slope_degrees", "slope_degrees", "min"),
    ],
    "slippery_trail": [
        ("rainfall_3h_threshold_mm", "rainfall_3h_mm", "min"),
        ("rainfall_24h_threshold_mm", "rainfall_24h_mm", "min"),
    ],
    "dense_fog": [
        ("maximum_visibility_m", "visibility_m", "max"),
    ],
    "strong_wind": [
        ("wind_gust_threshold_kmh", "wind_gust_kmh", "min"),
    ],
}


def get_value(row, column):
    """Return a finite numeric value, or None if unavailable."""
    value = row.get(column, None)

    if value is None or pd.isna(value):
        return None

    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not pd.notna(number):
        return None

    return number


def assess_rule(row, rules, rule_name):
    """
    Evaluate every configured condition for a rule.

    Unconfigured conditions are skipped. At least one condition
    must be configured. Missing inputs for configured conditions
    produce INSUFFICIENT_DATA.
    """
    conditions = RULE_CONDITIONS[rule_name]
    configured_conditions = []

    for threshold_key, feature, comparison in conditions:
        threshold = rules.get(threshold_key)

        if threshold is None:
            continue

        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            return "INVALID_CONFIGURATION"

        if not pd.notna(threshold):
            return "INVALID_CONFIGURATION"

        configured_conditions.append(
            (threshold_key, feature, comparison, threshold)
        )

    if not configured_conditions:
        return "NOT_CONFIGURED"

    # Every configured condition must have its required input.
    values = []

    for threshold_key, feature, comparison, threshold in configured_conditions:
        value = get_value(row, feature)

        if value is None:
            return "INSUFFICIENT_DATA"

        values.append((value, comparison, threshold))

    # All configured conditions must be satisfied for a trigger.
    triggered = all(
        value >= threshold if comparison == "min"
        else value <= threshold
        for value, comparison, threshold in values
    )

    return "RULE_TRIGGERED" if triggered else "RULE_NOT_TRIGGERED"


def main():
    if not FEATURE_FILE.is_file():
        raise FileNotFoundError(
            f"Missing {FEATURE_FILE}. Run "
            "weather_feature_engineering.py first."
        )

    config_file = (
        CONFIG_FILE if CONFIG_FILE.is_file() else CONFIG_FALLBACK_FILE
    )

    if not config_file.is_file():
        raise FileNotFoundError(
            "Missing rule configuration. Expected "
            f"{CONFIG_FILE} or {CONFIG_FALLBACK_FILE}."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    features = pd.read_csv(FEATURE_FILE)

    required_columns = [
        "trail_id",
        "timestamp",
        "rainfall_24h_mm",
        "rainfall_72h_mm",
        "rainfall_3h_mm",
        "slope_degrees",
        "wind_gust_kmh",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in features.columns
    ]

    if missing_columns:
        raise ValueError(
            "The feature file is missing required columns: "
            + ", ".join(missing_columns)
        )

    with open(config_file, "r", encoding="utf-8") as file:
        config_text = "\n".join(
            line for line in file
            if not line.lstrip().startswith("#")
        )

    config = json.loads(config_text)

    rules = config.get("rules", {})

    for rule_name in RULE_CONDITIONS:
        if rule_name not in rules:
            raise ValueError(
                f"Missing '{rule_name}' in weather_rule_config.json"
            )

    # Keep useful identifying and environmental information.
    context_columns = [
        column for column in [
            "trail_id",
            "timestamp",
            "trail_name",
            "rainfall_3h_mm",
            "rainfall_24h_mm",
            "rainfall_72h_mm",
            "slope_degrees",
            "visibility_m",
            "wind_gust_kmh",
        ]
        if column in features.columns
    ]

    context = features[context_columns].copy()

    # Evaluate the four implemented rules.
    rule_results = {}

    for rule_name in RULE_CONDITIONS:
        rule_results[rule_name] = features.apply(
            lambda row: assess_rule(row, rules[rule_name], rule_name),
            axis=1,
        )

    # Produce one row per weather observation and hazard category.
    output_frames = []

    for category in HAZARD_CATEGORIES:
        rule_name = CATEGORY_TO_RULE.get(category)

        if rule_name is not None:
            statuses = rule_results[rule_name].reset_index(drop=True)
        elif category == "no relevant hiking hazard":
            # This baseline cannot establish that no hazards exist.
            statuses = pd.Series(
                ["NOT_EVALUATED"] * len(features)
            )
        else:
            # No assessment rule exists for this category yet.
            statuses = pd.Series(
                ["NOT_CONFIGURED"] * len(features)
            )

        category_frame = context.reset_index(drop=True).copy()
        category_frame["hazard_category"] = category
        category_frame["rule_name"] = rule_name
        category_frame["rule_status"] = statuses
        category_frame["baseline_type"] = BASELINE_TYPE

        # These are rule indicators, not calibrated probabilities.
        category_frame["probability_of_occurrence"] = pd.NA

        output_frames.append(category_frame)

    results = pd.concat(output_frames, ignore_index=True)
    try:
        results.to_csv(OUTPUT_FILE, index=False)
    except PermissionError as error:
        raise PermissionError(
            f"Cannot write {OUTPUT_FILE}. Close the file if it is open "
            "in Excel or another program, and check that the output "
            "directory is writable."
        ) from error

    print(f"Saved rule results to: {OUTPUT_FILE}")
    print(f"Weather observations: {len(features)}")
    print(f"Hazard categories: {len(HAZARD_CATEGORIES)}")
    print(f"Output rows: {len(results)}")

    print("\nStatus counts by hazard category:")

    counts = (
        results.groupby(["hazard_category", "rule_status"])
        .size()
        .unstack(fill_value=0)
    )
    print(counts.to_string())

    print(
        "\nImportant: RULE_TRIGGERED means the configured "
        "experimental condition was met. It does not confirm "
        "a real hazard event. RULE_NOT_TRIGGERED does not "
        "guarantee safety. Probabilities are not calibrated."
    )


if __name__ == "__main__":
    main()

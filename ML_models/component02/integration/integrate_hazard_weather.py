
import ast
import json
import re
from pathlib import Path

import pandas as pd


# =========================================================
# 1. PATHS
# =========================================================

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"

WEATHER_FILE = OUTPUT_DIR / "weather_features.csv"
BASELINE_FILE = OUTPUT_DIR / "weather_rule_baseline.csv"
HISTORICAL_FILE = DATA_DIR / "historical_hazards.xlsx"
BERTOPIC_FILE = OUTPUT_DIR / "hazard_extraction_results.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# 2. NORMALIZATION HELPERS
# =========================================================

def normalize_trail_id(value):
    """Normalize IDs such as 01, 1, and 1.0 to the same key."""
    if pd.isna(value):
        return None

    value = str(value).strip()

    try:
        number = float(value)
        if number.is_integer():
            return str(int(number))
    except (ValueError, TypeError):
        pass

    return value.casefold()


def normalize_text(value):
    """Normalize names and labels for exact matching."""
    if pd.isna(value):
        return ""

    value = str(value).strip().casefold()
    value = re.sub(r"[_-]+", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value


def date_key(series):
    """Convert timestamps into UTC calendar dates."""
    parsed = pd.to_datetime(series, errors="coerce", utc=True)
    return parsed.dt.strftime("%Y-%m-%d")


HAZARD_ALIASES = {
    "landslide": "landslides",
    "landslides": "landslides",
    "rockfall": "rockfalls",
    "rockfalls": "rockfalls",

    "slippery trail": "slippery or muddy trails",
    "slippery trails": "slippery or muddy trails",
    "slippery or muddy trail": "slippery or muddy trails",
    "slippery or muddy trails": "slippery or muddy trails",
    "slippery muddy trails": "slippery or muddy trails",
    "slipperyor muddy trails": "slippery or muddy trails",

    "dense fog": "dense fog or poor visibility",
    "poor visibility": "dense fog or poor visibility",
    "dense fog or poor visibility": "dense fog or poor visibility",

    "leech activity": "high leech activity",
    "high leech activity": "high leech activity",

    "heavy rain": "heavy rain",
    "strong wind": "strong winds",
    "strong winds": "strong winds",

    "trail obstruction": "trail obstructions",
    "trail obstructions": "trail obstructions",

    "monkey sighting": "monkey sightings",
    "monkey sightings": "monkey sightings",

    "leopard sighting": "leopard sightings",
    "leopard sightings": "leopard sightings",

    "bugs or wasps activity": "bugs or wasps activity",
    "bug activity": "bugs or wasps activity",
    "wasp activity": "bugs or wasps activity",

    "no relevant hiking hazard": "no relevant hiking hazard",
}


def normalize_hazard(value):
    key = normalize_text(value)
    return HAZARD_ALIASES.get(key, key)


def join_unique(values):
    """Join distinct non-empty values into one string."""
    unique_values = {
        str(value).strip()
        for value in values.dropna()
        if str(value).strip()
    }
    return " | ".join(sorted(unique_values))


# =========================================================
# 3. LOAD INPUT FILES
# =========================================================

required_files = [
    WEATHER_FILE,
    BASELINE_FILE,
    HISTORICAL_FILE,
    BERTOPIC_FILE,
]

for file_path in required_files:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Required input file not found: {file_path}"
        )

print("Loading input files...")

weather = pd.read_csv(WEATHER_FILE, low_memory=False)
baseline = pd.read_csv(BASELINE_FILE, low_memory=False)
historical = pd.read_excel(HISTORICAL_FILE)
bertopic = pd.read_csv(BERTOPIC_FILE, low_memory=False)

print(f"Weather rows: {len(weather):,}")
print(f"Baseline rows: {len(baseline):,}")
print(f"Historical rows: {len(historical):,}")
print(f"BERTopic rows: {len(bertopic):,}")


# Check required columns before processing.
required_columns = {
    "weather": {
        "trail_id", "timestamp", "trail_name",
        "temperature_c", "relative_humidity_pct",
        "dew_point_c", "dew_point_depression_c",
        "precipitation_mm", "rainfall_mm",
        "rainfall_3h_mm", "rainfall_24h_mm",
        "rainfall_72h_mm", "rainfall_7d_mm",
        "wind_speed_kmh", "wind_gust_kmh", "weather_code",
        "latitude_x", "longitude_x", "elevation_m",
        "slope_degrees", "aspect_degrees",
        "terrain_type", "terrain_match",
    },
    "baseline": {
        "trail_id", "timestamp", "trail_name",
        "hazard_category", "rule_name", "rule_status",
        "evidence_level", "baseline_type",
    },
    "historical": {
        "event_id", "date", "trail_id", "trail_name",
        "hazard_type", "severity", "risk_score",
    },
    "bertopic": {
        "record_id", "date", "location",
        "hazard_labels", "keyword_labels", "model_labels",
    },
}

for name, required in required_columns.items():
    df = {
        "weather": weather,
        "baseline": baseline,
        "historical": historical,
        "bertopic": bertopic,
    }[name]

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"{name} dataset is missing required columns: "
            f"{sorted(missing)}"
        )


# =========================================================
# 4. PREPARE HOURLY WEATHER AND AGGREGATE DAILY
# =========================================================

weather["date_key"] = date_key(weather["timestamp"])
weather["trail_key"] = weather["trail_id"].map(
    normalize_trail_id
)

if weather["date_key"].isna().any():
    raise ValueError("Weather data contains invalid timestamps.")

if weather["trail_key"].isna().any():
    raise ValueError("Weather data contains missing trail IDs.")

weather_aggregations = {
    "trail_name": ("trail_name", "first"),
    "latitude": ("latitude_x", "mean"),
    "longitude": ("longitude_x", "mean"),

    "temperature_mean_c": ("temperature_c", "mean"),
    "temperature_max_c": ("temperature_c", "max"),

    "relative_humidity_mean_pct": (
        "relative_humidity_pct", "mean"
    ),
    "relative_humidity_max_pct": (
        "relative_humidity_pct", "max"
    ),

    "dew_point_mean_c": ("dew_point_c", "mean"),
    "dew_point_depression_min_c": (
        "dew_point_depression_c", "min"
    ),

    "precipitation_sum_mm": ("precipitation_mm", "sum"),
    "rainfall_sum_mm": ("rainfall_mm", "sum"),

    "rainfall_3h_max_mm": ("rainfall_3h_mm", "max"),
    "rainfall_24h_max_mm": ("rainfall_24h_mm", "max"),
    "rainfall_72h_max_mm": ("rainfall_72h_mm", "max"),
    "rainfall_7d_max_mm": ("rainfall_7d_mm", "max"),

    "wind_speed_mean_kmh": ("wind_speed_kmh", "mean"),
    "wind_speed_max_kmh": ("wind_speed_kmh", "max"),
    "wind_gust_max_kmh": ("wind_gust_kmh", "max"),

    "weather_code_mode": (
        "weather_code",
        lambda s: (
            s.mode().iloc[0] if not s.mode().empty else pd.NA
        ),
    ),

    "elevation_m": ("elevation_m", "first"),
    "slope_degrees": ("slope_degrees", "first"),
    "aspect_degrees": ("aspect_degrees", "first"),
    "terrain_type": ("terrain_type", "first"),
    "terrain_match": ("terrain_match", "first"),

    "hourly_observations": ("timestamp", "count"),
}

weather_daily = (
    weather.groupby(
        ["trail_key", "date_key"],
        as_index=False,
        dropna=False,
    )
    .agg(**weather_aggregations)
)

weather_daily.to_csv(
    OUTPUT_DIR / "weather_daily_features.csv",
    index=False,
)

print("Created weather_daily_features.csv")


# =========================================================
# 5. AGGREGATE WEATHER RULE BASELINE
# =========================================================

baseline["date_key"] = date_key(baseline["timestamp"])
baseline["trail_key"] = baseline["trail_id"].map(
    normalize_trail_id
)
baseline["hazard_key"] = baseline["hazard_category"].map(
    normalize_hazard
)

if baseline["date_key"].isna().any():
    raise ValueError("Baseline data contains invalid timestamps.")

if baseline["trail_key"].isna().any():
    raise ValueError("Baseline data contains missing trail IDs.")

# Keep the original statuses distinct.
baseline_daily = (
    baseline.groupby(
        ["trail_key", "date_key", "hazard_key"],
        as_index=False,
        dropna=False,
    )
    .agg(
        trail_name=("trail_name", "first"),
        hazard_category=("hazard_category", "first"),

        rule_triggered_hours=(
            "rule_status",
            lambda s: int((s == "RULE_TRIGGERED").sum()),
        ),
        rule_not_triggered_hours=(
            "rule_status",
            lambda s: int((s == "RULE_NOT_TRIGGERED").sum()),
        ),
        insufficient_data_hours=(
            "rule_status",
            lambda s: int((s == "INSUFFICIENT_DATA").sum()),
        ),
        not_evaluated_hours=(
            "rule_status",
            lambda s: int((s == "NOT_EVALUATED").sum()),
        ),
        not_configured_hours=(
            "rule_status",
            lambda s: int((s == "NOT_CONFIGURED").sum()),
        ),

        rule_names=("rule_name", join_unique),
        evidence_levels=("evidence_level", join_unique),
        baseline_types=("baseline_type", join_unique),

        hourly_rows=("rule_status", "size"),
    )
)

# Object dtype avoids categorical assignment errors.
baseline_daily["daily_rule_status"] = pd.Series(
    "MIXED_OR_UNCLASSIFIED_STATUS",
    index=baseline_daily.index,
    dtype="object",
)

triggered = baseline_daily["rule_triggered_hours"].gt(0)
no_trigger = baseline_daily["rule_triggered_hours"].eq(0)

baseline_daily.loc[
    triggered,
    "daily_rule_status",
] = "RULE_TRIGGERED_DURING_DAY"

baseline_daily.loc[
    no_trigger
    & baseline_daily["insufficient_data_hours"].gt(0),
    "daily_rule_status",
] = "INSUFFICIENT_DATA_PRESENT"

baseline_daily.loc[
    no_trigger
    & baseline_daily["insufficient_data_hours"].eq(0)
    & baseline_daily["not_evaluated_hours"].gt(0),
    "daily_rule_status",
] = "NOT_EVALUATED_PRESENT"

baseline_daily.loc[
    no_trigger
    & baseline_daily["insufficient_data_hours"].eq(0)
    & baseline_daily["not_evaluated_hours"].eq(0)
    & baseline_daily["not_configured_hours"].gt(0),
    "daily_rule_status",
] = "NOT_CONFIGURED_PRESENT"

fully_evaluated_no_trigger = (
    no_trigger
    & baseline_daily["rule_not_triggered_hours"].eq(
        baseline_daily["hourly_rows"]
    )
)

baseline_daily.loc[
    fully_evaluated_no_trigger,
    "daily_rule_status",
] = "RULE_NOT_TRIGGERED"

baseline_daily.to_csv(
    OUTPUT_DIR / "baseline_daily_by_hazard.csv",
    index=False,
)

print("Created baseline_daily_by_hazard.csv")


# =========================================================
# 6. INTEGRATE HISTORICAL HAZARDS WITH WEATHER AND BASELINE
# =========================================================

historical["date_key"] = date_key(historical["date"])
historical["trail_key"] = historical["trail_id"].map(
    normalize_trail_id
)
historical["hazard_key"] = historical["hazard_type"].map(
    normalize_hazard
)

if historical["date_key"].isna().any():
    raise ValueError("Historical data contains invalid dates.")

historical_weather = historical.merge(
    weather_daily,
    on=["trail_key", "date_key"],
    how="left",
    indicator="weather_join_indicator",
    validate="many_to_one",
)

historical_weather["weather_match_status"] = (
    historical_weather["weather_join_indicator"]
    .map({
        "both": "MATCHED",
        "left_only": "NO_MATCHING_TRAIL_AND_DATE",
        "right_only": "UNEXPECTED_WEATHER_ONLY",
    })
    .astype("object")
)

historical_weather = historical_weather.drop(
    columns=["weather_join_indicator"]
)

historical_integrated = historical_weather.merge(
    baseline_daily,
    on=["trail_key", "date_key", "hazard_key"],
    how="left",
    suffixes=("", "_baseline"),
    indicator="baseline_join_indicator",
    validate="many_to_one",
)

historical_integrated["baseline_match_status"] = (
    historical_integrated["baseline_join_indicator"]
    .map({
        "both": "MATCHED",
        "left_only": "NO_MATCHING_BASELINE_HAZARD",
        "right_only": "UNEXPECTED_BASELINE_ONLY",
    })
    .astype("object")
)

historical_integrated = historical_integrated.drop(
    columns=["baseline_join_indicator"]
)

if len(historical_integrated) != len(historical):
    raise ValueError(
        "Historical integration changed the number of source records."
    )

historical_integrated.to_csv(
    OUTPUT_DIR / "historical_hazards_integrated.csv",
    index=False,
)

print("Created historical_hazards_integrated.csv")


# =========================================================
# 7. MATCH BERTOPIC LOCATIONS AND JOIN DAILY WEATHER
# =========================================================

bertopic["date_key"] = date_key(bertopic["date"])
bertopic["location_key"] = bertopic["location"].map(
    normalize_text
)

if bertopic["date_key"].isna().any():
    raise ValueError("BERTopic data contains invalid dates.")

# Build exact normalized trail-name lookup.
trail_lookup = (
    weather[["trail_name", "trail_key"]]
    .dropna()
    .drop_duplicates()
    .copy()
)

trail_lookup["location_key"] = trail_lookup["trail_name"].map(
    normalize_text
)

# Do not map a name if it refers to multiple trail IDs.
name_counts = trail_lookup.groupby("location_key")[
    "trail_key"
].nunique()

ambiguous_names = set(
    name_counts[name_counts > 1].index
)

trail_lookup = trail_lookup[
    ~trail_lookup["location_key"].isin(ambiguous_names)
].drop_duplicates("location_key")

# Add aliases only after verifying the location is the same trail.
VERIFIED_TRAIL_ALIASES = {
    # "verified alternative name": "canonical trail name",
}

verified_aliases = []

for alias, canonical_name in VERIFIED_TRAIL_ALIASES.items():
    canonical_key = normalize_text(canonical_name)

    matches = trail_lookup[
        trail_lookup["location_key"] == canonical_key
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Alias target '{canonical_name}' does not identify "
            "exactly one trail."
        )

    verified_aliases.append({
        "location_key": normalize_text(alias),
        "trail_name": matches.iloc[0]["trail_name"],
        "trail_key": matches.iloc[0]["trail_key"],
    })

if verified_aliases:
    alias_df = pd.DataFrame(verified_aliases)

    # A verified alias must not conflict with an existing name.
    conflicting = set(alias_df["location_key"]) & set(
        trail_lookup["location_key"]
    )

    if conflicting:
        raise ValueError(
            f"Trail aliases conflict with existing names: {conflicting}"
        )

    trail_lookup = pd.concat(
        [trail_lookup, alias_df],
        ignore_index=True,
    )

bertopic_integrated = bertopic.merge(
    trail_lookup[["location_key", "trail_name", "trail_key"]],
    on="location_key",
    how="left",
    validate="many_to_one",
)

bertopic_integrated["location_match_status"] = pd.Series(
    "UNMATCHED_LOCATION",
    index=bertopic_integrated.index,
    dtype="object",
)

matched_location_mask = bertopic_integrated["trail_key"].notna()

bertopic_integrated.loc[
    matched_location_mask,
    "location_match_status",
] = "MATCHED_TRAIL_NAME"

bertopic_integrated = bertopic_integrated.merge(
    weather_daily,
    on=["trail_key", "date_key"],
    how="left",
    suffixes=("", "_weather"),
    indicator="weather_join_indicator",
    validate="many_to_one",
)

bertopic_integrated["weather_match_status"] = (
    bertopic_integrated["weather_join_indicator"]
    .map({
        "both": "MATCHED",
        "left_only": "NO_MATCHING_TRAIL_AND_DATE",
        "right_only": "UNEXPECTED_WEATHER_ONLY",
    })
    .astype("object")
)

unmatched_location_mask = bertopic_integrated["trail_key"].isna()

bertopic_integrated.loc[
    unmatched_location_mask,
    "weather_match_status",
] = "UNMATCHED_LOCATION"

bertopic_integrated = bertopic_integrated.drop(
    columns=["weather_join_indicator"]
)

# Text-extracted labels are candidates, not confirmed incidents.
bertopic_integrated["evidence_source_type"] = (
    "TEXT_EXTRACTED_CANDIDATE"
)
bertopic_integrated["is_confirmed_incident"] = False

if len(bertopic_integrated) != len(bertopic):
    raise ValueError(
        "BERTopic integration changed the number of source records."
    )

bertopic_integrated.to_csv(
    OUTPUT_DIR / "bertopic_hazards_integrated.csv",
    index=False,
)

print("Created bertopic_hazards_integrated.csv")


# =========================================================
# 8. CREATE ONE ROW PER TEXT RECORD AND HAZARD LABEL
# =========================================================

def parse_label_list(value):
    """Parse JSON/Python list strings without treating scores as probabilities."""
    if isinstance(value, list):
        return value

    if pd.isna(value):
        return []

    text_value = str(value).strip()

    if not text_value or text_value.casefold() in {
        "nan", "none", "[]"
    }:
        return []

    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(text_value)
            if isinstance(parsed, list):
                return parsed
        except (ValueError, SyntaxError, TypeError):
            continue

    # Keep an unparsed value intact instead of silently discarding it.
    return [text_value]


detail_rows = []

for _, row in bertopic_integrated.iterrows():
    labels = parse_label_list(row.get("hazard_labels"))

    if not labels:
        labels = parse_label_list(row.get("keyword_labels"))

    if not labels:
        labels = parse_label_list(row.get("model_labels"))

    for label in labels:
        if not str(label).strip():
            continue

        detail_rows.append({
            "record_id": row.get("record_id"),
            "date": row.get("date"),
            "date_key": row.get("date_key"),
            "location": row.get("location"),
            "trail_name": row.get("trail_name"),
            "trail_key": row.get("trail_key"),
            "location_match_status": row.get(
                "location_match_status"
            ),
            "weather_match_status": row.get(
                "weather_match_status"
            ),
            "hazard_label_raw": str(label),
            "hazard_key": normalize_hazard(label),
            "source": row.get("source"),
            "content": row.get("content"),
            "evidence_source_type": "TEXT_EXTRACTED_CANDIDATE",
            "is_confirmed_incident": False,
        })

detail_columns = [
    "record_id",
    "date",
    "date_key",
    "location",
    "trail_name",
    "trail_key",
    "location_match_status",
    "weather_match_status",
    "hazard_label_raw",
    "hazard_key",
    "source",
    "content",
    "evidence_source_type",
    "is_confirmed_incident",
]

bertopic_details = pd.DataFrame(
    detail_rows,
    columns=detail_columns,
)

bertopic_details.to_csv(
    OUTPUT_DIR / "bertopic_hazard_details.csv",
    index=False,
)

print("Created bertopic_hazard_details.csv")


# =========================================================
# 9. FINAL INTEGRATION SUMMARY
# =========================================================

print("\n" + "=" * 55)
print("INTEGRATION SUMMARY")
print("=" * 55)

print("\nDaily weather rows:", len(weather_daily))
print("Expected for 15 complete trails in 2025: 5,475")

print("\nHourly observations per trail/date:")
print(
    weather_daily["hourly_observations"]
    .value_counts(dropna=False)
    .sort_index()
    .to_string()
)

print("\nBaseline daily rows:", len(baseline_daily))
print("\nDaily rule status counts:")
print(
    baseline_daily["daily_rule_status"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nHistorical source rows:", len(historical))
print("Historical integrated rows:", len(historical_integrated))

print("\nHistorical weather match statuses:")
print(
    historical_integrated["weather_match_status"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nHistorical baseline match statuses:")
print(
    historical_integrated["baseline_match_status"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nBERTopic source rows:", len(bertopic))
print("BERTopic integrated rows:", len(bertopic_integrated))

print("\nBERTopic location match statuses:")
print(
    bertopic_integrated["location_match_status"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nBERTopic weather match statuses:")
print(
    bertopic_integrated["weather_match_status"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nBERTopic hazard-detail rows:", len(bertopic_details))

print("\nGenerated files:")
for filename in [
    "weather_daily_features.csv",
    "baseline_daily_by_hazard.csv",
    "historical_hazards_integrated.csv",
    "bertopic_hazards_integrated.csv",
    "bertopic_hazard_details.csv",
]:
    path = OUTPUT_DIR / filename
    print(f"  {path.name}: {'OK' if path.exists() else 'MISSING'}")

print("\nIntegration finished.")
print("Review all match statuses before model evaluation.")

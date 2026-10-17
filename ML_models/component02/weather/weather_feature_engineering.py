
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

WEATHER_FILE = DATA_DIR / "weather_observations.csv"
TERRAIN_CSV_FILE = DATA_DIR / "trail_terrain.csv"
TERRAIN_EXCEL_FILE = DATA_DIR / "trail_terrain.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "weather_features.csv"


def load_terrain():
    if TERRAIN_CSV_FILE.is_file():
        return pd.read_csv(TERRAIN_CSV_FILE)

    if TERRAIN_EXCEL_FILE.is_file():
        return pd.read_excel(TERRAIN_EXCEL_FILE)

    raise FileNotFoundError(
        "Missing terrain data. Expected "
        f"{TERRAIN_CSV_FILE} or {TERRAIN_EXCEL_FILE}."
    )


def build_weather_features():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    weather = pd.read_csv(WEATHER_FILE)
    terrain = load_terrain()

    required_weather = {
        "trail_id",
        "timestamp",
    }
    required_terrain = {
        "trail_id",
        "latitude",
        "longitude",
        "slope_degrees",
        "elevation_m",
    }

    missing_weather = required_weather - set(weather.columns)
    missing_terrain = required_terrain - set(terrain.columns)

    if missing_weather:
        raise ValueError(
            f"Missing weather columns: {sorted(missing_weather)}"
        )

    if "rainfall_mm" not in weather.columns:
        if "rain_mm" not in weather.columns:
            raise ValueError(
                "Missing weather rainfall column: expected "
                "'rainfall_mm' or 'rain_mm'."
            )
        weather = weather.rename(columns={"rain_mm": "rainfall_mm"})

    if missing_terrain:
        raise ValueError(
            f"Missing terrain columns: {sorted(missing_terrain)}"
        )

    weather["timestamp"] = pd.to_datetime(
        weather["timestamp"], errors="coerce", utc=True
    )

    weather["rainfall_mm"] = pd.to_numeric(
        weather["rainfall_mm"], errors="coerce"
    )

    weather = weather.dropna(
        subset=["trail_id", "timestamp"]
    ).copy()

    weather = weather.sort_values(
        ["trail_id", "timestamp"]
    )

    if weather.duplicated(["trail_id", "timestamp"]).any():
        raise ValueError(
            "Duplicate trail/timestamp weather rows found. "
            "Resolve duplicates before calculating rolling features."
        )

    if (weather["rainfall_mm"].dropna() < 0).any():
        raise ValueError(
            "Negative rainfall values found. Check the source data."
        )

    # Rolling sums below assume one observation per hour.
    # Check this assumption against your actual weather data.
    for trail_id, group in weather.groupby("trail_id"):
        differences = group["timestamp"].diff().dropna()

        if not differences.eq(pd.Timedelta(hours=1)).all():
            raise ValueError(
                f"Weather records for trail {trail_id} are not "
                "consistently hourly. Resample or adapt the rolling "
                "windows to your actual observation interval."
            )

    # Convert optional numeric features safely.
    optional_numeric = [
        "temperature_c",
        "relative_humidity_pct",
        "wind_speed_kmh",
        "wind_gust_kmh",
        "visibility_m",
        "dew_point_c",
    ]

    for column in optional_numeric:
        if column in weather.columns:
            weather[column] = pd.to_numeric(
                weather[column], errors="coerce"
            )

    # Rolling sums: 24, 72, and 168 hourly observations.
    # min_periods requires a complete window, avoiding an incomplete
    # period being mistaken for a complete rainfall total.
    grouped = weather.groupby("trail_id", sort=False)

    weather["rainfall_24h_mm"] = grouped[
        "rainfall_mm"
    ].transform(
        lambda s: s.rolling(24, min_periods=24).sum()
    )

    weather["rainfall_72h_mm"] = grouped[
        "rainfall_mm"
    ].transform(
        lambda s: s.rolling(72, min_periods=72).sum()
    )

    weather["rainfall_7d_mm"] = grouped[
        "rainfall_mm"
    ].transform(
        lambda s: s.rolling(168, min_periods=168).sum()
    )

    # Short-window rainfall intensity.
    weather["rainfall_3h_mm"] = grouped[
        "rainfall_mm"
    ].transform(
        lambda s: s.rolling(3, min_periods=3).sum()
    )

    # Optional feature: dew-point depression.
    if {
        "temperature_c",
        "dew_point_c",
    }.issubset(weather.columns):
        weather["dew_point_depression_c"] = (
            weather["temperature_c"] - weather["dew_point_c"]
        )

    # Join terrain. Each trail must have a single consistent terrain row.
    if terrain["trail_id"].duplicated().any():
        raise ValueError(
            "Multiple terrain rows per trail found. "
            "Aggregate them by trail or use a trail-segment ID."
        )

    result = weather.merge(
        terrain,
        on="trail_id",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    result["terrain_match"] = result["_merge"].eq("both")
    result = result.drop(columns="_merge")

    try:
        result.to_csv(OUTPUT_FILE, index=False)
    except PermissionError as error:
        raise PermissionError(
            f"Cannot write {OUTPUT_FILE}. Close the file if it is open "
            "in Excel or another program, and check that the output "
            "directory is writable."
        ) from error

    print(f"Saved engineered features to: {OUTPUT_FILE}")
    print(f"Weather rows: {len(result)}")
    print(f"Rows without terrain match: {(~result['terrain_match']).sum()}")

    return result


if __name__ == "__main__":
    build_weather_features()

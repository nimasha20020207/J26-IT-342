
# import requests
# import pandas as pd
# from pathlib import Path

# # Open-Meteo historical weather API
# API_URL = "https://archive-api.open-meteo.com/v1/archive"

# # Example location: Knuckles region, Sri Lanka
# LATITUDE = 7.45
# LONGITUDE = 80.75

# # Historical period
# START_DATE = "2020-01-01"
# END_DATE = "2025-12-31"

# # Weather variables for hiking hazard analysis
# HOURLY_VARIABLES = [
#     "temperature_2m",
#     "relative_humidity_2m",
#     "precipitation",
#     "rain",
#     "wind_speed_10m",
#     "wind_gusts_10m",
#     "wind_direction_10m",
#     "weather_code",
# ]

# params = {
#     "latitude": LATITUDE,
#     "longitude": LONGITUDE,
#     "start_date": START_DATE,
#     "end_date": END_DATE,
#     "hourly": ",".join(HOURLY_VARIABLES),
#     "timezone": "Asia/Colombo",
#     "temperature_unit": "celsius",
#     "wind_speed_unit": "kmh",
#     "precipitation_unit": "mm",
# }

# print("Requesting historical weather data...")

# response = requests.get(API_URL, params=params, timeout=120)
# response.raise_for_status()

# data = response.json()

# if "hourly" not in data:
#     raise ValueError(f"Hourly data missing: {data}")

# # Convert the JSON arrays into a tabular dataset
# df = pd.DataFrame(data["hourly"])

# # Add location information
# df["latitude"] = LATITUDE
# df["longitude"] = LONGITUDE

# # Organize columns
# columns = [
#     "time",
#     "latitude",
#     "longitude",
#     *HOURLY_VARIABLES,
# ]
# df = df[columns]

# # Clean and save
# df["time"] = pd.to_datetime(df["time"])
# df = df.sort_values("time").drop_duplicates(subset=["time"])

# output_dir = Path("data")
# output_dir.mkdir(exist_ok=True)

# output_file = output_dir / "historical_weather.csv"
# df.to_csv(output_file, index=False)

# print(f"Collection completed: {len(df)} records")
# print(f"Saved to: {output_file}")
# print(df.head())
# print(df.isnull().sum())


import requests
import pandas as pd
from pathlib import Path
import time

# Open-Meteo Historical Weather API
API_URL = "https://archive-api.open-meteo.com/v1/archive"

# Collect one complete calendar year.
START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

TIMEZONE = "Asia/Colombo"

# Replace these examples with your actual 15 trails.
TRAILS = [
    {
        "trail_id": "01",
        "trail_name": "Pidurangala",
        "latitude": 7.9658,
        "longitude": 80.7624,
    },
    {
        "trail_id": "02",
        "trail_name": "Sigiriya",
        "latitude": 7.956944,
        "longitude": 80.75972,
    },
    {
        "trail_id": "03",
        "trail_name": "Alagalla",
        "latitude": 7.2842,
        "longitude": 80.4772,
    },
    {
        "trail_id": "04",
        "trail_name": "Narangala",
        "latitude": 7.0289,
        "longitude": 80.9968,
    },
    {
        "trail_id": "05",
        "trail_name": "Hanthana",
        "latitude": 7.2287,
        "longitude": 80.6384,
    },
    {
        "trail_id": "06",
        "trail_name": "Lakegala",
        "latitude": 7.46611,
        "longitude": 80.83944,
    },
    {
        "trail_id": "07",
        "trail_name": "Manigala",
        "latitude": 7.5242,
        "longitude": 80.7747,
    },
    {
        "trail_id": "08",
        "trail_name": "Kirigalpoththa",
        "latitude": 6.799,
        "longitude": 80.766,
    },
    {
        "trail_id": "09",
        "trail_name": "Little Adam's peak",
        "latitude": 6.864999,
        "longitude": 81.062963,
    },
    {
        "trail_id": "10",
        "trail_name": "Pettigala",
        "latitude": 7.2863,
        "longitude": 80.7598,
    },
    {
        "trail_id": "11",
        "trail_name": "Peacock hills",
        "latitude": 7.0853,
        "longitude": 80.6327,
    },
    {
        "trail_id": "12",
        "trail_name": "Thotupala kanda",
        "latitude": 6.8331,
        "longitude": 80.8198,
    },
    {
        "trail_id": "13",
        "trail_name": "Bathalegala",
        "latitude": 7.1901,
        "longitude": 80.4339,
    },
    {
        "trail_id": "14",
        "trail_name": "Adam's peak",
        "latitude": 6.8094,
        "longitude": 80.4997,
    },
    {
        "trail_id": "15",
        "trail_name": "Ella rock",
        "latitude": 6.854718,
        "longitude": 81.052445,
    },

    # Add TRAIL_03 through TRAIL_15 here.
]

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "precipitation",
    "rain",
    "wind_speed_10m",
    "wind_gusts_10m",
    "wind_direction_10m",
    "weather_code",
]

# Output directory, relative to this script's working directory.
OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "weather_observations.csv"

# Names required by the downstream feature-engineering pipeline.
COLUMN_RENAME = {
    "time": "timestamp",
    "temperature_2m": "temperature_c",
    "relative_humidity_2m": "relative_humidity_pct",
    "dew_point_2m": "dew_point_c",
    "precipitation": "precipitation_mm",
    "rain": "rain_mm",
    "wind_speed_10m": "wind_speed_kmh",
    "wind_gusts_10m": "wind_gust_kmh",
    "wind_direction_10m": "wind_direction_degrees",
    "weather_code": "weather_code",
}


def collect_trail_weather(trail):
    """Download hourly historical weather for one trail."""

    params = {
        "latitude": trail["latitude"],
        "longitude": trail["longitude"],
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": ",".join(HOURLY_VARIABLES),
        "timezone": TIMEZONE,
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }

    print(
        f"\nCollecting {trail['trail_id']} - "
        f"{trail['trail_name']}"
    )

    response = requests.get(API_URL, params=params, timeout=180)
    response.raise_for_status()

    result = response.json()

    if "hourly" not in result:
        raise ValueError(
            f"Hourly data missing for {trail['trail_id']}: {result}"
        )

    df = pd.DataFrame(result["hourly"])

    if df.empty or "time" not in df.columns:
        raise ValueError(
            f"No usable hourly records for {trail['trail_id']}"
        )

    # Check that the requested variables were returned.
    missing_columns = [
        column for column in HOURLY_VARIABLES
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing variables for {trail['trail_id']}: "
            f"{missing_columns}"
        )

    df["trail_id"] = trail["trail_id"]
    df["trail_name"] = trail["trail_name"]
    df["latitude"] = trail["latitude"]
    df["longitude"] = trail["longitude"]

    df = df.rename(columns=COLUMN_RENAME)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df.sort_values("timestamp")
    df = df.drop_duplicates(
        subset=["trail_id", "timestamp"]
    )

    # Confirm timestamps are hourly and data covers the requested period.
    expected_hours = (
        pd.Timestamp(END_DATE) - pd.Timestamp(START_DATE)
    ).days * 24 + 24

    if len(df) != expected_hours:
        print(
            f"WARNING: {trail['trail_id']} returned {len(df)} "
            f"rows; expected approximately {expected_hours}. "
            "Inspect missing timestamps before modelling."
        )

    print(f"Received {len(df)} hourly records.")
    return df


def main():
    if len(TRAILS) != 15:
        raise ValueError(
            f"TRAILS currently contains {len(TRAILS)} entries. "
            "Add all 15 real hiking trails before collecting."
        )

    trail_ids = [trail["trail_id"] for trail in TRAILS]
    if len(set(trail_ids)) != len(trail_ids):
        raise ValueError("Every trail must have a unique trail_id.")

    all_data = []

    for index, trail in enumerate(TRAILS):
        try:
            trail_df = collect_trail_weather(trail)
            all_data.append(trail_df)

        except (requests.RequestException, ValueError) as error:
            # Stop rather than silently produce an incomplete dataset.
            raise RuntimeError(
                f"Collection failed for {trail['trail_id']}. "
                "Fix the problem and rerun the script."
            ) from error

        # A small pause between API requests.
        if index < len(TRAILS) - 1:
            time.sleep(1)

    combined = pd.concat(all_data, ignore_index=True)

    combined = combined.sort_values(
        ["trail_id", "timestamp"]
    ).reset_index(drop=True)

    # Final schema for weather feature engineering.
    columns = [
        "trail_id",
        "timestamp",
        "latitude",
        "longitude",
        "temperature_c",
        "relative_humidity_pct",
        "dew_point_c",
        "precipitation_mm",
        "rain_mm",
        "wind_speed_kmh",
        "wind_gust_kmh",
        "wind_direction_degrees",
        "weather_code",
        "trail_name",
    ]

    combined = combined[columns]
    combined.to_csv(OUTPUT_FILE, index=False)

    print("\nWeather collection completed.")
    print(f"Trails collected: {combined['trail_id'].nunique()}")
    print(f"Total records: {len(combined)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("\nRecords per trail:")
    print(combined.groupby("trail_id").size())
    print("\nMissing values:")
    print(combined.isnull().sum())
    print("\nFirst five rows:")
    print(combined.head())


if __name__ == "__main__":
    main()


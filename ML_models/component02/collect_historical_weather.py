
import requests
import pandas as pd
from pathlib import Path

# Open-Meteo historical weather API
API_URL = "https://archive-api.open-meteo.com/v1/archive"

# Example location: Knuckles region, Sri Lanka
LATITUDE = 7.45
LONGITUDE = 80.75

# Historical period
START_DATE = "2020-01-01"
END_DATE = "2025-12-31"

# Weather variables for hiking hazard analysis
HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "rain",
    "wind_speed_10m",
    "wind_gusts_10m",
    "wind_direction_10m",
    "weather_code",
]

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "start_date": START_DATE,
    "end_date": END_DATE,
    "hourly": ",".join(HOURLY_VARIABLES),
    "timezone": "Asia/Colombo",
    "temperature_unit": "celsius",
    "wind_speed_unit": "kmh",
    "precipitation_unit": "mm",
}

print("Requesting historical weather data...")

response = requests.get(API_URL, params=params, timeout=120)
response.raise_for_status()

data = response.json()

if "hourly" not in data:
    raise ValueError(f"Hourly data missing: {data}")

# Convert the JSON arrays into a tabular dataset
df = pd.DataFrame(data["hourly"])

# Add location information
df["latitude"] = LATITUDE
df["longitude"] = LONGITUDE

# Organize columns
columns = [
    "time",
    "latitude",
    "longitude",
    *HOURLY_VARIABLES,
]
df = df[columns]

# Clean and save
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").drop_duplicates(subset=["time"])

output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "historical_weather.csv"
df.to_csv(output_file, index=False)

print(f"Collection completed: {len(df)} records")
print(f"Saved to: {output_file}")
print(df.head())
print(df.isnull().sum())

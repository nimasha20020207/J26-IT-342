
from pathlib import Path
import pandas as pd

OUT = Path("outputs")

weather = pd.read_csv(OUT / "weather_daily_features.csv")
baseline = pd.read_csv(OUT / "baseline_daily_by_hazard.csv")
historical = pd.read_csv(OUT / "historical_hazards_integrated.csv")
bertopic = pd.read_csv(OUT / "bertopic_hazards_integrated.csv")

print("=" * 65)
print("VENTURE - INTEGRATION DIAGNOSTICS")
print("=" * 65)

# 1. Check daily weather uniqueness.
print("\n1. DAILY WEATHER UNIQUENESS")

weather["date_key"] = pd.to_datetime(
    weather["date_key"], errors="coerce"
).dt.strftime("%Y-%m-%d")

duplicates = weather.duplicated(
    subset=["trail_key", "date_key"], keep=False
)

print("Weather rows:", len(weather))
print("Duplicate trail/date rows:", int(duplicates.sum()))
print("Unique trails:", weather["trail_key"].nunique())
print("Unique dates:", weather["date_key"].nunique())
print("Date range:", weather["date_key"].min(), "to", weather["date_key"].max())

if duplicates.any():
    print("\nSample duplicate daily weather keys:")
    print(
        weather.loc[duplicates, ["trail_key", "date_key"]]
        .head(20).to_string(index=False)
    )

# 2. Check daily baseline status counts.
print("\n2. DAILY BASELINE STATUS")

print("Baseline rows:", len(baseline))
print("Hazard categories:", baseline["hazard_category"].nunique())

print(
    baseline["daily_rule_status"]
    .fillna("MISSING")
    .value_counts(dropna=False)
    .to_string()
)

# 3. Confirm historical matching.
print("\n3. HISTORICAL MATCHING")

for column in ["weather_match_status", "baseline_match_status"]:
    if column in historical.columns:
        print(f"\n{column}:")
        print(historical[column].value_counts(dropna=False).to_string())

# 4. Investigate text-record date matches.
print("\n4. TEXT-EXTRACTED RECORD DATE DIAGNOSTICS")

bertopic["parsed_date"] = pd.to_datetime(
    bertopic["date"], errors="coerce", utc=True
).dt.strftime("%Y-%m-%d")

weather_dates = set(weather["date_key"].dropna())
weather_trails = set(weather["trail_key"].dropna().astype(str))

print("Text records:", len(bertopic))
print("Invalid/missing dates:", int(bertopic["parsed_date"].isna().sum()))

in_weather_period = bertopic["parsed_date"].isin(weather_dates)

print("Records on dates covered by weather:", int(in_weather_period.sum()))
print("Records on dates outside weather coverage:", int((~in_weather_period).sum()))

print("\nExisting weather match statuses:")
print(
    bertopic["weather_match_status"]
    .fillna("MISSING")
    .value_counts(dropna=False)
    .to_string()
)

# Display unmatched records whose dates are covered by the weather data.
if "weather_match_status" in bertopic.columns:
    unmatched_in_period = bertopic[
        in_weather_period
        & (bertopic["weather_match_status"] != "MATCHED")
    ]

    print(
        "\nUnmatched text records whose dates are covered by weather:",
        len(unmatched_in_period)
    )

    columns_to_show = [
        c for c in [
            "record_id", "date", "location", "trail_name",
            "trail_key", "date_key", "location_match_status",
            "weather_match_status"
        ]
        if c in unmatched_in_period.columns
    ]

    if len(unmatched_in_period):
        print(unmatched_in_period[columns_to_show].head(30).to_string(index=False))
    else:
        print("No unmatched records remain within the weather date coverage.")

print("\nDIAGNOSTICS COMPLETE")

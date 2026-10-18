
from pathlib import Path
import pandas as pd

OUT = Path("outputs")

historical = pd.read_csv(
    OUT / "historical_hazards_integrated.csv",
    low_memory=False
)

baseline = pd.read_csv(
    OUT / "baseline_daily_by_hazard.csv",
    low_memory=False
)

print("=" * 65)
print("HISTORICAL DATASET")
print("=" * 65)

print("\nColumns:")
print(historical.columns.tolist())

for column in [
    "hazard_type",
    "severity",
    "trail_id",
    "trail_name",
    "date",
    "weather_match_status",
    "baseline_match_status",
]:
    if column in historical.columns:
        print(f"\n{column} value counts:")
        print(
            historical[column]
            .fillna("MISSING")
            .astype(str)
            .value_counts()
            .to_string()
        )

print("\nHistorical sample:")
print(historical.head(5).to_string(index=False))

print("\n" + "=" * 65)
print("DAILY BASELINE DATASET")
print("=" * 65)

print("\nColumns:")
print(baseline.columns.tolist())

for column in [
    "hazard_category",
    "daily_rule_status",
    "rule_triggered_hours",
    "rule_not_triggered_hours",
    "insufficient_data_hours",
    "not_evaluated_hours",
    "not_configured_hours",
]:
    if column in baseline.columns:
        print(f"\n{column} summary:")
        if column in ["rule_triggered_hours",
                      "rule_not_triggered_hours",
                      "insufficient_data_hours",
                      "not_evaluated_hours",
                      "not_configured_hours"]:
            print(baseline[column].describe().to_string())
        else:
            print(
                baseline[column]
                .fillna("MISSING")
                .astype(str)
                .value_counts()
                .to_string()
            )

print("\nBaseline sample:")
print(baseline.head(10).to_string(index=False))

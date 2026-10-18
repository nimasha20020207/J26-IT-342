
from pathlib import Path
import pandas as pd

OUTPUT_DIR = Path("outputs")

FILES = {
    "weather_daily": "weather_daily_features.csv",
    "baseline_daily": "baseline_daily_by_hazard.csv",
    "historical": "historical_hazards_integrated.csv",
    "bertopic": "bertopic_hazards_integrated.csv",
    "bertopic_details": "bertopic_hazard_details.csv",
}


def load_csv(filename):
    path = OUTPUT_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing output file: {path}")

    return pd.read_csv(path, low_memory=False)


def show_match_status(df, column, title):
    print(f"\n--- {title} ---")

    if column not in df.columns:
        print(f"Column not found: {column}")
        print("Available columns:", df.columns.tolist())
        return

    print(
        df[column]
        .fillna("MISSING")
        .astype(str)
        .value_counts(dropna=False)
        .to_string()
    )


def main():
    print("=" * 65)
    print("VENTURE - INTEGRATION DATA VALIDATION")
    print("=" * 65)

    data = {}

    for name, filename in FILES.items():
        df = load_csv(filename)
        data[name] = df

        print(f"\n{name}: {filename}")
        print(f"Rows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")

        if "timestamp" in df.columns:
            timestamps = pd.to_datetime(
                df["timestamp"], errors="coerce", utc=True
            )
            print(f"Date range: {timestamps.min()} to {timestamps.max()}")

        elif "date" in df.columns:
            dates = pd.to_datetime(df["date"], errors="coerce")
            print(f"Date range: {dates.min()} to {dates.max()}")

    # 1. Check for duplicate daily weather records.
    weather = data["weather_daily"]

    print("\n--- DAILY WEATHER CHECK ---")

    weather_keys = ["trail_id", "date"]

    if all(c in weather.columns for c in weather_keys):
        duplicates = weather.duplicated(
            subset=weather_keys, keep=False
        ).sum()

        print(f"Duplicate trail/date rows: {duplicates:,}")
    else:
        print("Could not check trail/date uniqueness.")
        print("Available columns:", weather.columns.tolist())

    # 2. Check historical records.
    historical = data["historical"]

    print("\n--- HISTORICAL RECORD CHECK ---")
    print(f"Historical records: {len(historical):,}")

    if len(historical) != 100:
        print("WARNING: Expected 100 historical records.")

    show_match_status(
        historical, "weather_match_status",
        "Historical weather matching"
    )
    show_match_status(
        historical, "baseline_match_status",
        "Historical baseline matching"
    )

    # 3. Check text-extracted records.
    bertopic = data["bertopic"]

    print("\n--- TEXT-EXTRACTED RECORD CHECK ---")
    print(f"BERTopic records: {len(bertopic):,}")

    if len(bertopic) != 141:
        print("WARNING: Expected 141 text-extracted records.")

    show_match_status(
        bertopic, "location_match_status",
        "BERTopic location matching"
    )
    show_match_status(
        bertopic, "weather_match_status",
        "BERTopic weather matching"
    )

    # 4. Check daily rule-result statuses.
    baseline = data["baseline_daily"]

    print("\n--- DAILY BASELINE STATUS CHECK ---")

    if "rule_status" in baseline.columns:
        print(
            baseline["rule_status"]
            .fillna("MISSING")
            .astype(str)
            .value_counts()
            .to_string()
        )
    else:
        print("No rule_status column found.")
        print("Available columns:", baseline.columns.tolist())

    # 5. Check hazard detail candidate labels.
    details = data["bertopic_details"]

    print("\n--- TEXT HAZARD CANDIDATES ---")

    for column in ["hazard_label", "is_confirmed_incident"]:
        if column in details.columns:
            print(f"\n{column}:")
            print(details[column].value_counts(dropna=False).to_string())

    if "is_confirmed_incident" in details.columns:
        confirmed = details["is_confirmed_incident"]

        # Handle booleans and CSV values such as "False".
        confirmed_text = confirmed.astype(str).str.lower()
        print(
            "\nRows marked as confirmed:",
            confirmed_text.isin(["true", "1", "yes"]).sum()
        )

    # 6. Check important missing values.
    print("\n--- MISSING VALUES: KEY OUTPUTS ---")

    for name in ["weather_daily", "historical", "bertopic"]:
        df = data[name]
        print(f"\n{name}:")

        important = [
            "trail_id", "trail_name", "date", "timestamp",
            "weather_match_status", "location_match_status"
        ]

        existing = [c for c in important if c in df.columns]

        if existing:
            missing = df[existing].isna().sum()
            print(missing[missing > 0].to_string() or "No missing values in these fields.")

    print("\n" + "=" * 65)
    print("VALIDATION REPORT COMPLETE")
    print("Review all warnings and match statuses before model evaluation.")
    print("=" * 65)


if __name__ == "__main__":
    main()

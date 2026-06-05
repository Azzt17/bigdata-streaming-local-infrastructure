from pathlib import Path

import pandas as pd


INPUT_PATH = Path("output/sensor_001_hourly.csv")
OUTPUT_PATH = Path("output/sensor_001_features.csv")


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"{INPUT_PATH} not found. Run ml/ml_timeseries_prepare.py first."
        )

    df = pd.read_csv(INPUT_PATH, parse_dates=["hour"])
    df = df.set_index("hour").sort_index()

    print(f"Original shape: {df.shape}")

    ts = df["avg_temp"].copy()

    # Lag features: previous temperature values
    for lag in [1, 2, 3, 6, 12, 24]:
        df[f"lag_{lag}h"] = ts.shift(lag)

    # Rolling statistics
    df["roll_mean_6h"] = ts.rolling(6).mean()
    df["roll_std_6h"] = ts.rolling(6).std()
    df["roll_mean_24h"] = ts.rolling(24).mean()
    df["roll_std_24h"] = ts.rolling(24).std()

    # Time-based features
    df["hour_of_day"] = df.index.hour
    df["day_of_week"] = df.index.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["month"] = df.index.month

    # First-order difference
    df["temp_diff"] = ts.diff(1)

    before_dropna = len(df)
    df = df.dropna()
    after_dropna = len(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH)

    print(f"Rows before dropna: {before_dropna:,}")
    print(f"Rows after dropna: {after_dropna:,}")
    print(f"Features shape: {df.shape}")
    print()
    print("Feature columns:")
    print(df.columns.tolist())
    print()
    print("Sample:")
    print(df.head())
    print()
    print(f"Feature dataset written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

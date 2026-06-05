import argparse
from pathlib import Path

import clickhouse_connect
import pandas as pd


TARGET_COLUMNS = ["event_time", "device_id", "temperature", "humidity", "pressure"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch ingest historical sensor CSV data into ClickHouse."
    )
    parser.add_argument(
        "--csv",
        default="data/raw/dataset_sensor_clickhouse.csv",
        help="Path to CSV dataset.",
    )
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8123)
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Detected CSV columns: {list(df.columns)}")

    missing_columns = set(TARGET_COLUMNS) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    df = df[TARGET_COLUMNS].copy()

    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce")
    df["device_id"] = df["device_id"].astype(str)
    df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
    df["humidity"] = pd.to_numeric(df["humidity"], errors="coerce")
    df["pressure"] = pd.to_numeric(df["pressure"], errors="coerce")

    before_cleaning = len(df)

    df = df.dropna(subset=TARGET_COLUMNS)
    df = df[df["temperature"].between(-50, 80)]
    df = df[df["humidity"].between(0, 100)]
    df = df.drop_duplicates(subset=["event_time", "device_id"])

    after_cleaning = len(df)

    client = clickhouse_connect.get_client(
        host=args.host,
        port=args.port,
        username="default",
        password="",
    )

    client.insert_df("bigdata.sensor_readings", df)

    total_rows = client.query("SELECT count() FROM bigdata.sensor_readings").first_row[
        0
    ]

    print(f"Rows before cleaning: {before_cleaning:,}")
    print(f"Rows inserted: {after_cleaning:,}")
    print(f"Total rows in bigdata.sensor_readings: {total_rows:,}")


if __name__ == "__main__":
    main()

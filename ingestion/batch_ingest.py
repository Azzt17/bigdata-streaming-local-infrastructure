import argparse
from pathlib import Path

import clickhouse_connect
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch ingest historical sensor CSV data into ClickHouse."
    )
    parser.add_argument(
        "--csv",
        default="data/raw/dataset_sensor_clickhouse.csv",
        help="Path to CSV dataset.",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="ClickHouse host.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8123,
        help="ClickHouse HTTP port.",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    client = clickhouse_connect.get_client(
        host=args.host,
        port=args.port,
        username="default",
        password="",
    )

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])

    df = df.rename(
        columns={
            "timestamp": "event_time",
            "value": "temperature",
        }
    )

    df["device_id"] = "sensor-001"
    df["humidity"] = 60.0
    df["pressure"] = 1013.25

    df = df[["event_time", "device_id", "temperature", "humidity", "pressure"]]

    df = df[df["temperature"].between(-50, 80)]
    df = df.dropna(subset=["event_time", "temperature"])
    df = df.drop_duplicates(subset=["event_time", "device_id"])

    client.insert_df("bigdata.sensor_readings", df)

    total_rows = client.query("SELECT count() FROM bigdata.sensor_readings").first_row[0]

    print(f"Inserted rows: {len(df):,}")
    print(f"Total rows in bigdata.sensor_readings: {total_rows:,}")


if __name__ == "__main__":
    main()

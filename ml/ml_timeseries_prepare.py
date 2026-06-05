import clickhouse_connect
import pandas as pd


def main() -> None:
    client = clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username="default",
        password="",
    )

    query = """
    SELECT
        toStartOfHour(event_time) AS hour,
        device_id,
        avg(temperature) AS avg_temp,
        min(temperature) AS min_temp,
        max(temperature) AS max_temp,
        stddevPop(temperature) AS std_temp
    FROM bigdata.sensor_readings
    WHERE device_id = 'sensor-001'
      AND event_time < toDateTime('2015-01-01 00:00:00')
    GROUP BY hour, device_id
    ORDER BY hour
    """

    df = client.query_df(query)

    df["hour"] = pd.to_datetime(df["hour"])
    df = df.set_index("hour").sort_index()

    print(f"Shape: {df.shape}")
    print()
    print("Head:")
    print(df.head())
    print()
    print("Tail:")
    print(df.tail())
    print()
    print("Date range:")
    print(df.index.min(), "→", df.index.max())
    print()
    print("Missing values:")
    print(df.isna().sum())

    output_path = "output/sensor_001_hourly.csv"
    df.to_csv(output_path)

    print()
    print(f"Prepared dataset written to: {output_path}")


if __name__ == "__main__":
    main()

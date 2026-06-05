from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


CH_URL = "jdbc:clickhouse://localhost:8123/bigdata"

CH_OPTS = {
    "driver": "com.clickhouse.jdbc.ClickHouseDriver",
    "user": "default",
    "password": "",
}

OUTPUT_PATH = Path("output/hourly_agg")


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("BigData_ClickHouse_TimeSeries_Aggregation")
        .master("local[*]")
        .config("spark.jars", "jars/clickhouse-jdbc.jar")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    df = spark.read.jdbc(
        url=CH_URL,
        table="(SELECT * FROM sensor_readings) AS sensor_readings",
        properties=CH_OPTS,
    )

    hourly_agg = (
        df.groupBy(
            F.window("event_time", "1 hour"),
            "device_id",
        )
        .agg(
            F.avg("temperature").alias("avg_temp"),
            F.min("temperature").alias("min_temp"),
            F.max("temperature").alias("max_temp"),
            F.stddev("temperature").alias("std_temp"),
            F.count("*").alias("record_count"),
        )
        .select(
            F.col("window.start").alias("window_start"),
            F.col("window.end").alias("window_end"),
            "device_id",
            "avg_temp",
            "min_temp",
            "max_temp",
            "std_temp",
            "record_count",
        )
        .orderBy("window_start", "device_id")
    )

    print("Hourly aggregation sample:")
    hourly_agg.show(20, truncate=False)

    total_rows = hourly_agg.count()
    print(f"Total hourly aggregation rows: {total_rows:,}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    hourly_agg.write.mode("overwrite").parquet(str(OUTPUT_PATH))

    print(f"Output written to: {OUTPUT_PATH}")

    spark.stop()


if __name__ == "__main__":
    main()

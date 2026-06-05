from pyspark.sql import SparkSession
from pyspark.sql import functions as F


CH_URL = "jdbc:clickhouse://localhost:8123/bigdata"

CH_OPTS = {
    "driver": "com.clickhouse.jdbc.ClickHouseDriver",
    "user": "default",
    "password": "",
}


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("BigData_ClickHouse_Sliding_Window_Analysis")
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

    sliding_df = (
        df.groupBy(
            F.window("event_time", "24 hours", "6 hours"),
            "device_id",
        )
        .agg(
            F.avg("temperature").alias("rolling_avg_temp"),
            F.avg("humidity").alias("rolling_avg_humidity"),
            F.stddev("temperature").alias("rolling_std_temp"),
            F.count("*").alias("record_count"),
        )
        .select(
            F.col("window.start").alias("window_start"),
            F.col("window.end").alias("window_end"),
            "device_id",
            "rolling_avg_temp",
            "rolling_avg_humidity",
            "rolling_std_temp",
            "record_count",
        )
        .orderBy("window_start", "device_id")
    )

    print("Sliding window analysis sample:")
    sliding_df.show(30, truncate=False)

    print(f"Total sliding window rows: {sliding_df.count():,}")

    spark.stop()


if __name__ == "__main__":
    main()

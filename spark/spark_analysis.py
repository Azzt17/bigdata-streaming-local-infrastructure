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
        .appName("BigData_ClickHouse_Analysis")
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

    print("Schema:")
    df.printSchema()

    print("Sample data:")
    df.show(10, truncate=False)

    total_records = df.count()
    print(f"Total records: {total_records:,}")

    print("Records per device:")
    (
        df.groupBy("device_id")
        .agg(
            F.count("*").alias("total"),
            F.min("event_time").alias("earliest_event"),
            F.max("event_time").alias("latest_event"),
        )
        .orderBy("device_id")
        .show(truncate=False)
    )

    spark.stop()


if __name__ == "__main__":
    main()

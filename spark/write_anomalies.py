import clickhouse_connect

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import abs as spark_abs


CH_URL = "jdbc:clickhouse://localhost:8123/bigdata"

CH_OPTS = {
    "driver": "com.clickhouse.jdbc.ClickHouseDriver",
    "user": "default",
    "password": "",
}


def reset_anomalies_table() -> None:
    client = clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username="default",
        password="",
    )
    client.command("TRUNCATE TABLE bigdata.anomalies")


def main() -> None:
    reset_anomalies_table()

    spark = (
        SparkSession.builder
        .appName("BigData_ClickHouse_Write_Anomalies")
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

    stats = (
        df.groupBy("device_id")
        .agg(
            F.mean("temperature").alias("mean_temp"),
            F.stddev("temperature").alias("std_temp"),
        )
    )

    anomalies = (
        df.join(stats, on="device_id", how="left")
        .filter(F.col("std_temp").isNotNull() & (F.col("std_temp") > 0))
        .withColumn(
            "z_score",
            spark_abs((F.col("temperature") - F.col("mean_temp")) / F.col("std_temp")),
        )
        .filter(F.col("z_score") > 3.0)
        .select(
            "event_time",
            "device_id",
            "temperature",
            "z_score",
        )
    )

    anomaly_count = anomalies.count()
    print(f"Anomalies to write: {anomaly_count:,}")

    anomalies.write.jdbc(
        url=CH_URL,
        table="anomalies",
        mode="append",
        properties=CH_OPTS,
    )

    print("Anomalies written to bigdata.anomalies")

    spark.stop()


if __name__ == "__main__":
    main()

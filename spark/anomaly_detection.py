from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import abs as spark_abs


CH_URL = "jdbc:clickhouse://localhost:8123/bigdata"

CH_OPTS = {
    "driver": "com.clickhouse.jdbc.ClickHouseDriver",
    "user": "default",
    "password": "",
}


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("BigData_ClickHouse_ZScore_Anomaly_Detection")
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

    df_z = (
        df.join(stats, on="device_id", how="left")
        .filter(F.col("std_temp").isNotNull() & (F.col("std_temp") > 0))
        .withColumn(
            "z_score",
            spark_abs((F.col("temperature") - F.col("mean_temp")) / F.col("std_temp")),
        )
        .withColumn("is_anomaly", F.col("z_score") > 3.0)
    )

    anomalies = df_z.filter(F.col("is_anomaly") == True)

    print("Temperature statistics per device:")
    stats.orderBy("device_id").show(truncate=False)

    print(f"Total records: {df.count():,}")
    print(f"Anomalies found: {anomalies.count():,}")

    print("Top anomalies by z-score:")
    (
        anomalies
        .select("event_time", "device_id", "temperature", "mean_temp", "std_temp", "z_score")
        .orderBy(F.desc("z_score"))
        .show(30, truncate=False)
    )

    spark.stop()


if __name__ == "__main__":
    main()

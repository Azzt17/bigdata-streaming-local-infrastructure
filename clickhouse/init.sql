CREATE DATABASE IF NOT EXISTS bigdata;

CREATE TABLE IF NOT EXISTS bigdata.sensor_readings
(
    event_time DateTime,
    device_id LowCardinality(String),
    temperature Float32,
    humidity Float32,
    pressure Float32
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (device_id, event_time)
TTL event_time + INTERVAL 2 YEAR DELETE
SETTINGS index_granularity = 8192;

CREATE TABLE IF NOT EXISTS bigdata.sensor_kafka
(
    event_time DateTime,
    device_id String,
    temperature Float32,
    humidity Float32,
    pressure Float32
)
ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka:29092',
    kafka_topic_list = 'sensor-data',
    kafka_group_name = 'clickhouse-consumer',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 2;

CREATE MATERIALIZED VIEW IF NOT EXISTS bigdata.sensor_mv
TO bigdata.sensor_readings
AS
SELECT
    event_time,
    device_id,
    temperature,
    humidity,
    pressure
FROM bigdata.sensor_kafka
WHERE temperature BETWEEN -50 AND 80
  AND humidity BETWEEN 0 AND 100;

CREATE TABLE IF NOT EXISTS bigdata.anomalies
(
    event_time DateTime,
    device_id LowCardinality(String),
    temperature Float32,
    z_score Float64
)
ENGINE = MergeTree()
ORDER BY (device_id, event_time);

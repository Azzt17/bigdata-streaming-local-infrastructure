CREATE TABLE IF NOT EXISTS bigdata.forecasts
(
    model_name LowCardinality(String),
    forecast_time DateTime,
    actual Float64,
    forecast Float64,
    absolute_error Float64,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (model_name, forecast_time);

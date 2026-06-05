CREATE OR REPLACE VIEW bigdata.predictions AS
SELECT
    forecast_time AS predict_time,
    'sensor-001' AS device_id,
    model_name,
    forecast AS predicted,
    actual
FROM bigdata.forecasts;

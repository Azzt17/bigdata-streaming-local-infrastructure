-- Aggregasi per jam langsung di ClickHouse
SELECT
    toStartOfHour(event_time) AS hour,
    device_id,
    avg(temperature) AS avg_temp,
    min(temperature) AS min_temp,
    max(temperature) AS max_temp,
    stddevPop(temperature) AS std_temp,
    count() AS record_count
FROM bigdata.sensor_readings
GROUP BY hour, device_id
ORDER BY hour, device_id
LIMIT 30;

-- Moving average berbasis window function
SELECT
    event_time,
    device_id,
    temperature,
    avg(temperature) OVER (
        PARTITION BY device_id
        ORDER BY event_time
        ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
    ) AS moving_avg_24
FROM bigdata.sensor_readings
ORDER BY device_id, event_time
LIMIT 100;

-- Ringkasan jumlah hasil aggregasi per jam
SELECT
    count() AS hourly_aggregation_rows
FROM
(
    SELECT
        toStartOfHour(event_time) AS hour,
        device_id
    FROM bigdata.sensor_readings
    GROUP BY hour, device_id
);

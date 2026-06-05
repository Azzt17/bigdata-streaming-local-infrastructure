-- Jumlah data per device
SELECT
    device_id,
    count() AS total,
    min(event_time) AS earliest_event,
    max(event_time) AS latest_event
FROM bigdata.sensor_readings
GROUP BY device_id
ORDER BY device_id;

-- Statistik deskriptif temperature
SELECT
    avg(temperature) AS avg_temp,
    min(temperature) AS min_temp,
    max(temperature) AS max_temp,
    stddevPop(temperature) AS std_temp
FROM bigdata.sensor_readings;

-- Ukuran tabel dan rasio kompresi
SELECT
    table,
    formatReadableSize(sum(data_compressed_bytes)) AS compressed,
    formatReadableSize(sum(data_uncompressed_bytes)) AS uncompressed,
    round(sum(data_uncompressed_bytes) / sum(data_compressed_bytes), 2) AS compression_ratio,
    sum(rows) AS total_rows
FROM system.parts
WHERE database = 'bigdata'
  AND active = 1
GROUP BY table
ORDER BY table;

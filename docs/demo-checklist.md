# Demo Checklist

This checklist describes the end-to-end demo flow for the local big data streaming and analytics lab.

## 1. Start Infrastructure

Start the Docker Compose stack:

```bash
docker compose up -d
```

Verify running services:

```bash
docker compose ps
```

Expected services:

```text
namenode
datanode
spark-master
spark-worker
zookeeper
kafka
clickhouse
grafana
```

## 2. Verify ClickHouse

Check ClickHouse version:

```bash
docker exec -it clickhouse clickhouse-client --query "SELECT version();"
```

Check database objects:

```bash
docker exec -it clickhouse clickhouse-client --query "
SELECT
    name,
    engine
FROM system.tables
WHERE database = 'bigdata'
ORDER BY name;
"
```

Expected important objects:

```text
sensor_kafka
sensor_mv
sensor_readings
anomalies
forecasts
predictions
```

## 3. Verify Kafka Topic

Describe the Kafka topic:

```bash
docker exec kafka kafka-topics --describe   --topic sensor-data   --bootstrap-server localhost:9092
```

Expected baseline:

```text
PartitionCount: 3
ReplicationFactor: 1
```

## 4. Run Streaming Producer

Run the simulated sensor producer:

```bash
source venv_bigdata/bin/activate
python producer/producer.py --events 30 --interval 0.2
```

Verify that data reached ClickHouse:

```bash
docker exec -it clickhouse clickhouse-client --query "
SELECT
    count(),
    max(event_time)
FROM bigdata.sensor_readings;
"
```

Expected result:

```text
Row count increases after producer runs.
```

## 5. Run Batch Ingestion

Run CSV batch ingestion:

```bash
source venv_bigdata/bin/activate
python ingestion/batch_ingest.py
```

Verify total rows:

```bash
docker exec -it clickhouse clickhouse-client --query "
SELECT
    count() AS total_rows,
    min(event_time) AS earliest_event,
    max(event_time) AS latest_event
FROM bigdata.sensor_readings;
"
```

Expected result:

```text
Total rows: around 21,880
Earliest event: 2013-07-04
Latest event: real-time producer timestamp
```

## 6. Run Basic ClickHouse Queries

Run basic exploration queries:

```bash
docker exec -i clickhouse clickhouse-client --multiquery < clickhouse/basic_queries.sql
```

This should show:

```text
Rows per device
Temperature statistics
Table size and compression ratio
```

## 7. Run Spark Processing

Activate Java 17 and Python environment:

```bash
source scripts/use-java-17.sh
source venv_bigdata/bin/activate
```

Read ClickHouse data with Spark:

```bash
python spark/spark_analysis.py
```

Run hourly aggregation:

```bash
python spark/time_series_aggregation.py
```

Run sliding window analysis:

```bash
python spark/sliding_window_analysis.py
```

Run anomaly detection:

```bash
python spark/anomaly_detection.py
```

Write anomalies back to ClickHouse:

```bash
python spark/write_anomalies.py
```

Verify anomalies:

```bash
docker exec -it clickhouse clickhouse-client --query "
SELECT
    count() AS total_anomalies,
    min(event_time) AS earliest_anomaly,
    max(event_time) AS latest_anomaly
FROM bigdata.anomalies;
"
```

Expected result:

```text
Total anomalies: 72
```

## 8. Run Forecasting Pipeline

Prepare ML dataset:

```bash
python ml/ml_timeseries_prepare.py
```

Generate features:

```bash
python ml/feature_engineering.py
```

Run ARIMA:

```bash
python ml/arima_forecast.py
```

Run LSTM:

```bash
python ml/lstm_forecast.py --epochs 10
```

Compare models:

```bash
python ml/evaluate_forecasts.py
```

Write forecasts to ClickHouse:

```bash
python ml/write_forecasts.py
```

Verify forecasts:

```bash
docker exec -it clickhouse clickhouse-client --query "
SELECT
    model_name,
    count() AS total_rows,
    round(avg(absolute_error), 4) AS avg_absolute_error,
    min(forecast_time) AS earliest_forecast,
    max(forecast_time) AS latest_forecast
FROM bigdata.forecasts
GROUP BY model_name
ORDER BY avg_absolute_error;
"
```

Expected result:

```text
LSTM has lower error than ARIMA.
```

## 9. Open Grafana Dashboard

Open Grafana:

```text
http://localhost:3000
```

Login:

```text
Username: admin
Password: admin123
```

Open dashboard:

```text
Dashboard Analitik Sensor IoT - ClickHouse
```

Expected panels:

```text
Panel 1: Sensor temperature per device
Panel 2: Anomaly timeline
Panel 3: Forecast vs actual
Panel 4: Model error summary
```

## 10. Open Streamlit Dashboard

Run Streamlit:

```bash
source venv_bigdata/bin/activate
streamlit run streamlit/app.py
```

Open:

```text
http://localhost:8501
```

Expected sections:

```text
Summary metrics
Sensor temperature chart
Anomaly table
Forecast model comparison
Forecast vs actual chart
```

## 11. Stop Infrastructure

Stop the Docker Compose stack:

```bash
docker compose down
```

To stop and remove volumes:

```bash
docker compose down -v
```

Use `-v` only when a full reset is intended.

## 12. Demo Narrative

A concise explanation for presentation:

```text
This project demonstrates a local big data streaming and analytics pipeline.
Kafka handles simulated real-time ingestion, ClickHouse stores time-series data
using OLAP-oriented MergeTree tables, Spark performs aggregation and anomaly
detection, and ARIMA/LSTM models produce forecasting results. Grafana provides
an operational dashboard, while Streamlit provides an exploratory dashboard.
```

## 13. Expected Final Evidence

Before submitting or presenting, prepare:

```text
Git commit history
Docker Compose running services
ClickHouse table verification
Kafka topic verification
Grafana dashboard screenshot
Streamlit dashboard screenshot
Model comparison result
Architecture documentation
Demo checklist
```

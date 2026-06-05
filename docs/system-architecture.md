# System Architecture

## Overview

This project implements a local big data streaming and analytics lab using Docker Compose. The system simulates a real-time sensor analytics pipeline with ingestion, storage, processing, machine learning, and visualization layers.

## High-Level Pipeline

```text
CSV Historical Dataset
        │
        ├── Batch Ingestion
        │       └── Python → ClickHouse MergeTree
        │
        └── Streaming Simulation
                └── Python Producer → Kafka → ClickHouse Kafka Engine → Materialized View → MergeTree

ClickHouse
        │
        ├── Raw / historical sensor storage
        ├── Anomaly result storage
        ├── Forecast result storage
        └── Dashboard query layer

Spark
        │
        ├── Read sensor data from ClickHouse
        ├── Time-series aggregation
        ├── Sliding window analysis
        ├── Z-score anomaly detection
        └── Write anomaly results back to ClickHouse

Machine Learning
        │
        ├── ARIMA forecasting
        ├── LSTM forecasting
        ├── Model evaluation
        └── Write forecast results back to ClickHouse

Visualization
        │
        ├── Grafana dashboard
        └── Streamlit dashboard
```

## Component Responsibilities

### Apache Kafka

Kafka is used as the streaming ingestion layer. The Python producer sends simulated sensor events to the `sensor-data` topic.

Current baseline:

```text
Topic: sensor-data
Partitions: 3
Replication factor: 1
```

This baseline follows the local single-broker setup. A future improvement is a three-broker Kafka cluster with replication factor 3 for fault-tolerance simulation.

### ClickHouse

ClickHouse acts as the primary analytical storage layer. It stores sensor readings, anomaly results, and forecasting results.

Main database objects:

```text
bigdata.sensor_kafka      Kafka Engine table
bigdata.sensor_mv         Materialized View
bigdata.sensor_readings   MergeTree table
bigdata.anomalies         MergeTree table
bigdata.forecasts         MergeTree table
bigdata.predictions       View for dashboard compatibility
```

The Kafka Engine table is not permanent storage. It acts as a streaming ingestion window. The Materialized View moves Kafka data into the permanent MergeTree table.

### Apache Spark

Spark is used for analytical processing that is more complex than simple SQL aggregation.

Implemented Spark jobs:

```text
spark_analysis.py              Read ClickHouse data with Spark
time_series_aggregation.py     Hourly aggregation
sliding_window_analysis.py     Sliding window analysis
anomaly_detection.py           Z-score anomaly detection
write_anomalies.py             Write anomalies back to ClickHouse
```

### Machine Learning

Machine learning is applied to the prepared hourly time-series dataset for `sensor-001`.

Implemented ML scripts:

```text
ml_timeseries_prepare.py       Prepare hourly dataset from ClickHouse
feature_engineering.py         Generate lag, rolling, calendar, and diff features
arima_forecast.py              ARIMA forecasting
lstm_forecast.py               LSTM forecasting
evaluate_forecasts.py          Compare model performance
write_forecasts.py             Write forecast results to ClickHouse
```

Model comparison result:

```text
ARIMA(2,1,2): MAE 1.5657 | RMSE 1.8884 | MAPE 8.37%
LSTM        : MAE 0.6585 | RMSE 0.8444 | MAPE 3.47%
Best model  : LSTM
```

### Grafana

Grafana is used as the operational analytics dashboard.

Panels:

```text
Panel 1: Sensor temperature per device
Panel 2: Anomaly timeline
Panel 3: Forecast vs actual
Panel 4: Model error summary
```

### Streamlit

Streamlit is used as the exploratory dashboard and demo app.

Features:

```text
Summary metrics
Device selector
Sensor temperature chart
Anomaly table
Forecast model comparison
Forecast vs actual chart
```

## Data Flow Details

### Streaming Ingestion Flow

```text
Python Producer
        ↓
Kafka topic: sensor-data
        ↓
ClickHouse Kafka Engine table: bigdata.sensor_kafka
        ↓
Materialized View: bigdata.sensor_mv
        ↓
Permanent table: bigdata.sensor_readings
```

### Batch Ingestion Flow

```text
CSV dataset: dataset_sensor_clickhouse.csv
        ↓
Python batch ingestion script
        ↓
ClickHouse MergeTree table: bigdata.sensor_readings
```

### Spark Processing Flow

```text
ClickHouse sensor_readings
        ↓
Spark JDBC read
        ↓
Aggregation / sliding window / anomaly detection
        ↓
ClickHouse anomalies table
```

### Forecasting Flow

```text
ClickHouse sensor_readings
        ↓
Hourly dataset preparation
        ↓
ARIMA and LSTM forecasting
        ↓
Model evaluation
        ↓
ClickHouse forecasts table
        ↓
bigdata.predictions view
```

## Local Environment Notes

This project runs on Fedora Linux using Docker Compose.

Important environment adaptations:

```text
Spark UI remapped from localhost:8080 to localhost:8081
ClickHouse config bind mount uses SELinux relabeling (:ro,Z)
ClickHouse user config is mounted into /etc/clickhouse-server/users.d
Java 17 is used for local PySpark execution
Python 3.11 is used for TensorFlow/PySpark compatibility
```

## Scope

This project is a single-machine local lab. It is not a production-grade distributed cluster.

Production-oriented improvements would include:

```text
Kafka multi-broker replication
Schema registry
Prometheus + JMX metrics
Persistent object storage
Airflow or Dagster orchestration
Kubernetes deployment
Cloud deployment
Secrets management
CI/CD pipeline
Automated integration tests
```

## Current Status

The local baseline is complete:

- Docker Compose infrastructure is running.
- Kafka topic ingestion is working.
- ClickHouse Kafka Engine ingestion is working.
- Batch ingestion from CSV is working.
- Spark can read and write ClickHouse data.
- Anomaly detection results are stored in ClickHouse.
- ARIMA and LSTM forecasts are stored in ClickHouse.
- Grafana dashboard is available.
- Streamlit dashboard is available.

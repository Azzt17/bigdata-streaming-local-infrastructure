# Architecture Notes

## Baseline Pipeline

```text
CSV historical dataset
        ↓
Python replay producer
        ↓
Apache Kafka
        ↓
ClickHouse Kafka Engine
        ↓
ClickHouse MergeTree table
        ↓
Apache Spark processing
        ↓
ClickHouse processed tables
        ↓
Grafana + Streamlit
```

## Local Lab Scope

This repository is a single-machine Docker Compose lab. It is not intended to represent a production-grade distributed cluster.

Initial Engineering Decisions
Use Python 3.11 for compatibility with TensorFlow, PySpark, and the practicum dependency set.
Use Docker Compose before moving to cloud deployment.
Start from the practicum baseline before adding multi-broker Kafka and benchmark/fault-tolerance scenarios.
Keep datasets, generated outputs, local volumes, and virtual environments out of Git.
EOF

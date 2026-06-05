# Big Data Real-Time Streaming Local Lab

Hands-on local lab for building a real-time big data streaming pipeline using Docker Compose.

## Target Pipeline

CSV historical dataset → Python replay producer → Apache Kafka → ClickHouse → Spark → Grafana + Streamlit

## Main Components

- Apache Kafka: event streaming and ingestion layer
- ClickHouse: columnar OLAP storage for time-series analytics
- Apache Spark: processing, aggregation, and anomaly analysis
- Grafana: operational dashboard
- Streamlit: interactive data exploration dashboard
- Docker Compose: single-machine local infrastructure

## Learning Goal

Build a local big data streaming infrastructure before moving to the main cloud-based practicum.

## Reference

Primary reference: Modul Praktikum Sistem Big Data — Analisis Big Data Time Series dengan ClickHouse.
EOF

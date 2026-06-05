#!/usr/bin/env bash
set -euo pipefail

docker exec kafka kafka-topics --create \
  --if-not-exists \
  --topic sensor-data \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

docker exec kafka kafka-topics --describe \
  --topic sensor-data \
  --bootstrap-server localhost:9092

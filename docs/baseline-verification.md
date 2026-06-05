# Baseline Cluster Verification

## Status

Baseline Docker Compose cluster is running successfully.

## Services

| Service | Status | URL / Port |
|---|---|---|
| Hadoop Namenode | Running | http://localhost:9870 |
| Spark Master | Running | http://localhost:8081 |
| ClickHouse HTTP | Running | http://localhost:8123/play |
| ClickHouse Native TCP | Running | localhost:9001 |
| Grafana | Running | http://localhost:3000 |
| Grafana Login | Running | admin / admin123 |

## Notes

The original practicum module maps Spark Master UI to `localhost:8080`, but this local environment already uses port 8080 for another service. Spark Master UI is remapped to `localhost:8081`.

ClickHouse config bind mount requires SELinux relabeling on Fedora. The compose mount uses `:ro,Z` for `./clickhouse-config`.

## Verification Commands

docker compose ps
docker exec -it clickhouse clickhouse-client --query "SELECT version();"

## Verified ClickHouse Version
24.3.18.7


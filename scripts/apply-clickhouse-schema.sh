#!/usr/bin/env bash
set -euo pipefail

docker exec -i clickhouse clickhouse-client --multiquery < clickhouse/init.sql

docker exec clickhouse clickhouse-client --query "
SELECT
    name,
    engine
FROM system.tables
WHERE database = 'bigdata'
ORDER BY name;
"

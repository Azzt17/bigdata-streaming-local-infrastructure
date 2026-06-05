# HDFS Dataset Upload

## Dataset

Dataset file used for the practicum:

```text
dataset_sensor_clickhouse.csv

The dataset is stored locally under data/raw/, but raw datasets are intentionally excluded from Git.
```

## HDFS Path
/bigdata/input/dataset_sensor_clickhouse.csv

## Upload Commands
docker cp data/raw/dataset_sensor_clickhouse.csv namenode:/tmp/dataset_sensor_clickhouse.csv
docker exec namenode hdfs dfs -mkdir -p /bigdata/input
docker exec namenode hdfs dfs -put -f /tmp/dataset_sensor_clickhouse.csv /bigdata/input/
docker exec namenode hdfs dfs -ls /bigdata/input/


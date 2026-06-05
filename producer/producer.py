import argparse
import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer


DEVICES = ["sensor-001", "sensor-002", "sensor-003"]


def generate_data(device_id: str) -> dict:
    return {
        "event_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "device_id": device_id,
        "temperature": round(random.gauss(25.0, 3.0), 2),
        "humidity": round(random.gauss(60.0, 10.0), 2),
        "pressure": round(random.gauss(1013.25, 5.0), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Send simulated sensor data to Kafka.")
    parser.add_argument("--bootstrap-server", default="localhost:9092")
    parser.add_argument("--topic", default="sensor-data")
    parser.add_argument("--events", type=int, default=30)
    parser.add_argument("--interval", type=float, default=0.2)
    args = parser.parse_args()

    producer = KafkaProducer(
        bootstrap_servers=[args.bootstrap_server],
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        key_serializer=lambda key: key.encode("utf-8"),
    )

    print(f"Sending {args.events} events to topic '{args.topic}'...")

    for i in range(args.events):
        device_id = random.choice(DEVICES)
        event = generate_data(device_id)

        producer.send(
            args.topic,
            key=device_id,
            value=event,
        )

        print(f"[{i + 1}/{args.events}] sent: {event}")
        time.sleep(args.interval)

    producer.flush()
    producer.close()
    print("Done.")


if __name__ == "__main__":
    main()

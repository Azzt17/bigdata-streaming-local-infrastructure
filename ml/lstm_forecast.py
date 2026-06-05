import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential


INPUT_PATH = Path("output/sensor_001_hourly.csv")
OUTPUT_PATH = Path("output/lstm_forecast.csv")


def create_sequences(data: np.ndarray, lookback: int) -> tuple[np.ndarray, np.ndarray]:
    x_values = []
    y_values = []

    for i in range(len(data) - lookback):
        x_values.append(data[i : i + lookback])
        y_values.append(data[i + lookback])

    return np.array(x_values), np.array(y_values)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train an LSTM model for temperature forecasting.")
    parser.add_argument("--lookback", type=int, default=24, help="Number of previous hours used as input.")
    parser.add_argument("--epochs", type=int, default=10, help="Training epochs.")
    parser.add_argument("--batch-size", type=int, default=32, help="Training batch size.")
    args = parser.parse_args()

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"{INPUT_PATH} not found. Run ml/ml_timeseries_prepare.py first."
        )

    np.random.seed(42)
    tf.random.set_seed(42)

    df = pd.read_csv(INPUT_PATH, parse_dates=["hour"])
    df = df.set_index("hour").sort_index()

    series = df["avg_temp"].astype(float).values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series)

    x, y = create_sequences(scaled, args.lookback)

    split_idx = int(len(x) * 0.8)

    x_train, x_test = x[:split_idx], x[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    print(f"Total points: {len(series):,}")
    print(f"Lookback: {args.lookback} hours")
    print(f"Train sequences: {len(x_train):,}")
    print(f"Test sequences: {len(x_test):,}")

    model = Sequential(
        [
            LSTM(64, return_sequences=True, input_shape=(args.lookback, 1)),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.2),
            Dense(1),
        ]
    )

    model.compile(optimizer="adam", loss="mse")

    history = model.fit(
        x_train,
        y_train,
        epochs=args.epochs,
        batch_size=args.batch_size,
        validation_split=0.1,
        verbose=1,
    )

    predictions_scaled = model.predict(x_test, verbose=0)

    predictions = scaler.inverse_transform(predictions_scaled).flatten()
    actual = scaler.inverse_transform(y_test).flatten()

    mae = mean_absolute_error(actual, predictions)
    rmse = np.sqrt(mean_squared_error(actual, predictions))

    non_zero_mask = actual != 0
    mape = np.mean(np.abs((actual[non_zero_mask] - predictions[non_zero_mask]) / actual[non_zero_mask])) * 100

    print()
    print("LSTM Evaluation")
    print(f"MAE : {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAPE: {mape:.2f}%")

    test_index = df.index[args.lookback:][split_idx:]

    output = pd.DataFrame(
        {
            "hour": test_index,
            "actual": actual,
            "forecast": predictions,
            "absolute_error": np.abs(actual - predictions),
        }
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH, index=False)

    print()
    print(f"Forecast output written to: {OUTPUT_PATH}")
    print()
    print("Forecast sample:")
    print(output.head(10))


if __name__ == "__main__":
    main()

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller


INPUT_PATH = Path("output/sensor_001_hourly.csv")
OUTPUT_PATH = Path("output/arima_forecast.csv")


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"{INPUT_PATH} not found. Run ml/ml_timeseries_prepare.py first."
        )

    df = pd.read_csv(INPUT_PATH, parse_dates=["hour"])
    df = df.set_index("hour").sort_index()

    series = df["avg_temp"].astype(float).dropna()

    print(f"Total time-series points: {len(series):,}")
    print(f"Date range: {series.index.min()} → {series.index.max()}")

    adf_stat, p_value, *_ = adfuller(series.values)
    print()
    print("ADF Test")
    print(f"ADF Statistic: {adf_stat:.4f}")
    print(f"p-value: {p_value:.4f}")
    print("Status:", "Stationary" if p_value < 0.05 else "Not stationary")

    split_idx = int(len(series) * 0.8)

    train = series.iloc[:split_idx]
    test = series.iloc[split_idx:]

    print()
    print(f"Train size: {len(train):,}")
    print(f"Test size: {len(test):,}")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        model = ARIMA(
            train,
            order=(2, 1, 2),
            enforce_stationarity=False,
            enforce_invertibility=False,
        )

        result = model.fit()

    forecast = result.forecast(steps=len(test))
    forecast.index = test.index

    mae = mean_absolute_error(test, forecast)
    rmse = np.sqrt(mean_squared_error(test, forecast))

    non_zero_mask = test != 0
    mape = np.mean(np.abs((test[non_zero_mask] - forecast[non_zero_mask]) / test[non_zero_mask])) * 100

    print()
    print("ARIMA(2,1,2) Evaluation")
    print(f"MAE : {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAPE: {mape:.2f}%")

    output = pd.DataFrame(
        {
            "actual": test,
            "forecast": forecast,
            "absolute_error": np.abs(test - forecast),
        }
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_PATH)

    print()
    print(f"Forecast output written to: {OUTPUT_PATH}")
    print()
    print("Forecast sample:")
    print(output.head(10))


if __name__ == "__main__":
    main()

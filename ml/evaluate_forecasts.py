from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


ARIMA_PATH = Path("output/arima_forecast.csv")
LSTM_PATH = Path("output/lstm_forecast.csv")


def calculate_metrics(df: pd.DataFrame, model_name: str) -> dict:
    actual = df["actual"].astype(float)
    forecast = df["forecast"].astype(float)

    mae = mean_absolute_error(actual, forecast)
    rmse = np.sqrt(mean_squared_error(actual, forecast))

    non_zero_mask = actual != 0
    mape = np.mean(
        np.abs((actual[non_zero_mask] - forecast[non_zero_mask]) / actual[non_zero_mask])
    ) * 100

    return {
        "model": model_name,
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "rows": len(df),
    }


def main() -> None:
    if not ARIMA_PATH.exists():
        raise FileNotFoundError(f"{ARIMA_PATH} not found. Run ml/arima_forecast.py first.")

    if not LSTM_PATH.exists():
        raise FileNotFoundError(f"{LSTM_PATH} not found. Run ml/lstm_forecast.py first.")

    arima_df = pd.read_csv(ARIMA_PATH)
    lstm_df = pd.read_csv(LSTM_PATH)

    results = pd.DataFrame(
        [
            calculate_metrics(arima_df, "ARIMA(2,1,2)"),
            calculate_metrics(lstm_df, "LSTM"),
        ]
    )

    results = results.sort_values("mape")

    print("Forecast model comparison:")
    print(results.to_string(index=False, formatters={
        "mae": "{:.4f}".format,
        "rmse": "{:.4f}".format,
        "mape": "{:.2f}%".format,
    }))

    best_model = results.iloc[0]["model"]

    print()
    print(f"Best model by MAPE: {best_model}")

    output_path = Path("output/model_evaluation.csv")
    results.to_csv(output_path, index=False)

    print(f"Evaluation output written to: {output_path}")


if __name__ == "__main__":
    main()

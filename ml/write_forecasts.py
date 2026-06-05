from pathlib import Path

import clickhouse_connect
import pandas as pd


ARIMA_PATH = Path("output/arima_forecast.csv")
LSTM_PATH = Path("output/lstm_forecast.csv")


def load_forecast(path: Path, model_name: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{path} not found.")

    df = pd.read_csv(path)

    if "hour" not in df.columns:
        first_col = df.columns[0]
        df = df.rename(columns={first_col: "hour"})

    required_columns = {"hour", "actual", "forecast", "absolute_error"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"{path} is missing columns: {sorted(missing_columns)}"
        )

    df = df[["hour", "actual", "forecast", "absolute_error"]].copy()

    df["model_name"] = model_name
    df["forecast_time"] = pd.to_datetime(df["hour"], errors="coerce")
    df["actual"] = pd.to_numeric(df["actual"], errors="coerce")
    df["forecast"] = pd.to_numeric(df["forecast"], errors="coerce")
    df["absolute_error"] = pd.to_numeric(df["absolute_error"], errors="coerce")

    df = df.dropna(
        subset=["forecast_time", "actual", "forecast", "absolute_error"]
    )

    return df[
        ["model_name", "forecast_time", "actual", "forecast", "absolute_error"]
    ]


def main() -> None:
    arima_df = load_forecast(ARIMA_PATH, "ARIMA(2,1,2)")
    lstm_df = load_forecast(LSTM_PATH, "LSTM")

    forecasts = pd.concat([arima_df, lstm_df], ignore_index=True)

    client = clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username="default",
        password="",
    )

    client.command("TRUNCATE TABLE bigdata.forecasts")
    client.insert_df("bigdata.forecasts", forecasts)

    total_rows = client.query("SELECT count() FROM bigdata.forecasts").first_row[0]

    print(f"Inserted forecast rows: {len(forecasts):,}")
    print(f"Total rows in bigdata.forecasts: {total_rows:,}")


if __name__ == "__main__":
    main()

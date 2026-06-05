import clickhouse_connect
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Big Data Sensor Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Big Data Sensor Analytics")
st.caption("Kafka → ClickHouse → Spark → Grafana + Streamlit")


@st.cache_resource
def get_client():
    return clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username="default",
        password="",
    )


client = get_client()


@st.cache_data(ttl=30)
def query_df(sql: str) -> pd.DataFrame:
    return client.query_df(sql)


summary = query_df("""
SELECT
    count() AS total_rows,
    min(event_time) AS earliest_event,
    max(event_time) AS latest_event,
    uniqExact(device_id) AS total_devices
FROM bigdata.sensor_readings
""")

anomaly_summary = query_df("""
SELECT
    count() AS total_anomalies,
    max(z_score) AS max_z_score
FROM bigdata.anomalies
""")

forecast_summary = query_df("""
SELECT
    model_name,
    count() AS total_rows,
    round(avg(absolute_error), 4) AS mae,
    round(sqrt(avg(pow(absolute_error, 2))), 4) AS rmse
FROM bigdata.forecasts
GROUP BY model_name
ORDER BY mae ASC
""")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total sensor rows", f"{int(summary.loc[0, 'total_rows']):,}")
col2.metric("Total devices", int(summary.loc[0, "total_devices"]))
col3.metric("Total anomalies", int(anomaly_summary.loc[0, "total_anomalies"]))
col4.metric("Max z-score", f"{float(anomaly_summary.loc[0, 'max_z_score']):.2f}")

st.divider()

devices = query_df("""
SELECT DISTINCT device_id
FROM bigdata.sensor_readings
ORDER BY device_id
""")["device_id"].tolist()

selected_devices = st.multiselect(
    "Select device(s)",
    devices,
    default=devices,
)

if selected_devices:
    devices_sql = ",".join([f"'{d}'" for d in selected_devices])

    st.subheader("Sensor Temperature per Device")

    sensor_df = query_df(f"""
    SELECT
        toStartOfHour(event_time) AS time,
        device_id,
        avg(temperature) AS avg_temp
    FROM bigdata.sensor_readings
    WHERE device_id IN ({devices_sql})
      AND event_time < toDateTime('2015-01-01 00:00:00')
    GROUP BY time, device_id
    ORDER BY time, device_id
    """)

    fig = px.line(
        sensor_df,
        x="time",
        y="avg_temp",
        color="device_id",
        title="Hourly Average Temperature",
    )
    fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Anomalies Detected")

anom_df = query_df("""
SELECT
    event_time,
    device_id,
    round(temperature, 2) AS temperature,
    round(z_score, 3) AS z_score
FROM bigdata.anomalies
ORDER BY z_score DESC
LIMIT 100
""")

st.dataframe(anom_df, use_container_width=True)

st.subheader("Forecast Model Comparison")

st.dataframe(forecast_summary, use_container_width=True)

pred_df = query_df("""
SELECT
    predict_time,
    model_name,
    predicted,
    actual
FROM bigdata.predictions
ORDER BY predict_time, model_name
""")

if not pred_df.empty:
    fig2 = go.Figure()

    actual_df = pred_df[["predict_time", "actual"]].drop_duplicates()

    fig2.add_trace(
        go.Scatter(
            x=actual_df["predict_time"],
            y=actual_df["actual"],
            name="Actual",
            mode="lines",
        )
    )

    for model in pred_df["model_name"].unique():
        model_df = pred_df[pred_df["model_name"] == model]

        fig2.add_trace(
            go.Scatter(
                x=model_df["predict_time"],
                y=model_df["predicted"],
                name=f"Forecast ({model})",
                mode="lines",
                line=dict(dash="dash"),
            )
        )

    fig2.update_layout(
        title="Forecast vs Actual",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
    )

    st.plotly_chart(fig2, use_container_width=True)

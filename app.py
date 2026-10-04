import altair as alt
import gspread
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

from waterdata import (
    DEFAULT_THRESHOLDS,
    default_window,
    latest_with_delta,
    out_of_range,
    prepare_data,
    rows_to_frame,
    worksheet_gid,
)

st.set_page_config(page_title="Water Data Pi", page_icon=":droplet:", layout="wide")
st.title("Water Data Pi")


@st.cache_resource
def get_client() -> gspread.Client:
    return gspread.service_account_from_dict(
        dict(st.secrets["gcp_service_account"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )


@st.cache_data(ttl=60, show_spinner="Loading sensor data...")
def get_data(sheet_url: str) -> pd.DataFrame:
    spreadsheet = get_client().open_by_url(sheet_url)
    gid = worksheet_gid(sheet_url)
    worksheet = spreadsheet.get_worksheet_by_id(gid) if gid is not None else spreadsheet.sheet1
    return prepare_data(rows_to_frame(worksheet.get_all_values()))


def temperature_gauge(value: float) -> dict:
    return {
        "series": [
            {
                "type": "gauge",
                "center": ["50%", "60%"],
                "startAngle": 200,
                "endAngle": -20,
                "min": 0,
                "max": 60,
                "splitNumber": 12,
                "itemStyle": {"color": "#FFAB91"},
                "progress": {"show": True, "width": 30},
                "pointer": {"show": False},
                "axisLine": {"lineStyle": {"width": 30}},
                "axisTick": {"distance": -45, "splitNumber": 5, "lineStyle": {"width": 2, "color": "#999"}},
                "splitLine": {"distance": -52, "length": 14, "lineStyle": {"width": 3, "color": "#999"}},
                "axisLabel": {"distance": -20, "color": "#999", "fontSize": 20},
                "anchor": {"show": False},
                "title": {"show": False},
                "detail": {
                    "valueAnimation": True,
                    "width": "60%",
                    "lineHeight": 40,
                    "borderRadius": 8,
                    "offsetCenter": [0, "-15%"],
                    "fontSize": 30,
                    "fontWeight": "bolder",
                    "formatter": "{value} °C",
                    "color": "inherit",
                },
                "data": [{"value": value}],
            },
            {
                "type": "gauge",
                "center": ["50%", "60%"],
                "startAngle": 200,
                "endAngle": -20,
                "min": 0,
                "max": 60,
                "itemStyle": {"color": "#FD7347"},
                "progress": {"show": True, "width": 8},
                "pointer": {"show": False},
                "axisLine": {"show": False},
                "axisTick": {"show": False},
                "splitLine": {"show": False},
                "axisLabel": {"show": False},
                "detail": {"show": False},
                "data": [{"value": value}],
            },
        ]
    }


def area_chart(df: pd.DataFrame, column: str, color: str, domain: list[float]) -> alt.Chart:
    return (
        alt.Chart(df[["Timestamp", column]])
        .mark_area(
            line={"color": color},
            color=alt.Gradient(
                gradient="linear",
                stops=[alt.GradientStop(color="white", offset=0), alt.GradientStop(color=color, offset=1)],
                x1=1,
                x2=1,
                y1=1,
                y2=0,
            ),
        )
        .encode(alt.X("Timestamp"), alt.Y(column, scale=alt.Scale(domain=domain)))
    )


with st.sidebar:
    st.header("Settings")
    if st.button("Refresh now"):
        get_data.clear()
    st.caption("Data is cached for 60 seconds.")
    st.subheader("Alert thresholds")
    slider_bounds = {"Temperature": (0.0, 60.0), "pH": (0.0, 14.0), "EC": (0.0, 2000.0)}
    thresholds = {
        column: st.slider(column, *slider_bounds[column], value=default)
        for column, default in DEFAULT_THRESHOLDS.items()
    }

try:
    data_df = get_data(st.secrets["private_gsheets_url"])
except Exception as exc:
    st.error(f"Could not load data from Google Sheets: {exc}")
    st.stop()

data_length = len(data_df)
if data_length < 2:
    st.warning("Not enough data in the sheet yet.")
    st.stop()

start_index, end_index = st.slider(
    "Select the range of data", 1, data_length, default_window(data_length), step=1
)
window = data_df.iloc[start_index - 1 : end_index]
if window.empty:
    st.warning("The selected range is empty.")
    st.stop()

for message in out_of_range(window, thresholds):
    st.warning(message, icon="⚠️")

metric_columns = st.columns(5)
for container, (column, label, unit) in zip(
    metric_columns,
    [
        ("Temperature", "Temperature", " °C"),
        ("pH", "pH", ""),
        ("EC", "EC", ""),
        ("WaterLevel", "Water level", ""),
        ("LightPercentage", "Light", " %"),
    ],
):
    latest, delta = latest_with_delta(window, column)
    container.metric(label, "—" if latest is None else f"{latest:g}{unit}", None if delta is None else f"{delta:+.2f}")

row1col1, row1col2 = st.columns(2)
with row1col1:
    st.header("Temperature")
    latest_temperature, _ = latest_with_delta(window, "Temperature")
    st_echarts(options=temperature_gauge(latest_temperature or 0), key="temperature_gauge")
with row1col2:
    st.line_chart(window.set_index("Timestamp")["Temperature"])

row2col1, row2col2 = st.columns(2)
with row2col1:
    st.header("EC Level")
    st.altair_chart(area_chart(window, "EC", "darkgreen", [0, 1600]), width="stretch")
with row2col2:
    st.header("pH Level")
    st.altair_chart(area_chart(window, "pH", "#FFD433", [0, 12]), width="stretch")

if "WaterLevel" in window.columns:
    st.header("Water Level")
    st.line_chart(window.set_index("Timestamp")["WaterLevel"])

st.header("pH VS. EC")
scatter_df = data_df.loc[data_df["EC"] * data_df["pH"] != 0]
brush = alt.selection_interval()
ph_vs_ec = (
    alt.Chart(scatter_df)
    .mark_circle()
    .encode(
        x=alt.X("EC"),
        y=alt.Y("pH", scale=alt.Scale(domain=[0, 14])),
        color=alt.condition(brush, alt.value("steelblue"), alt.value("grey")),
    )
    .add_params(brush)
)
st.altair_chart(ph_vs_ec, width="stretch")

st.header("Light Intensity")
st.line_chart(window.set_index("Timestamp")["Light"])

st.header("Raw Data")
st.dataframe(window, width="stretch")
st.download_button(
    "Download selected range as CSV",
    window.to_csv(index=False).encode("utf-8"),
    file_name="water_data.csv",
    mime="text/csv",
)

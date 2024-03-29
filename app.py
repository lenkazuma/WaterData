import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from gsheetsdb import connect
import altair as alt
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Water Data Pi", page_icon=":books:",layout="wide")
st.title("Water Data Pi")
# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

# Perform SQL query on the Google Sheet.

def get_data():
    query = f'SELECT * FROM "{sheet_url}"'
    rows = conn.execute(query)
    # Convert the list of lists to a pandas DataFrame
    df = pd.DataFrame(rows)
    return df

sheet_url = st.secrets["private_gsheets_url"]
data_df = get_data()


def create_database_connection():
    # Assuming you want to return the Google Sheets connection
    return conn

# Use the cached database connection
db_conn = create_database_connection()

# Print results.

data_df = data_df.rename(columns={'_6': 'LightPercentage', '_2': 'EC','_4': 'WaterLevel','_6': 'LightPercentage'})
data_df.Temperature = data_df.Temperature.round(2)
data_df.EC = data_df.EC.round(4)
data_df.pH = data_df.pH.round(4)
data_df.Light = data_df.Light.round(4)
data_df.LightPercentage = data_df.LightPercentage.round(2)


# Get the length of the DataFrame
data_length = len(data_df)

# Add the double range slider to select a range of data
values = st.slider('Select the range of data', 1, data_length, (data_length - 5000, data_length), step=1)

# Extract the selected range
st.write(values)
start_index, end_index = values
df_last_300 = data_df.iloc[start_index:end_index]

# creating a single-element container
placeholder = st.empty()

with placeholder.container():

    # create two columns
    row1col1, row1col2 = st.columns(2)


    with row1col1:
        st.header("Temperature")
        option = {
            "series": [
                {
                    "type": 'gauge',
                    "center": ['50%', '60%'],
                    "startAngle": 200,
                    "endAngle": -20,
                    "min": 0,
                    "max": 60,
                    "splitNumber": 12,
                    "itemStyle": {
                        "color": '#FFAB91'
                    },
                    "progress": {
                        "show": "true",
                        "width": 30
                    },
                    "pointer": {
                        "show": "false"
                    },
                    "axisLine": {
                        "lineStyle": {
                            "width": 30
                        }
                    },
                    "axisTick": {
                        "distance": -45,
                        "splitNumber": 5,
                        "lineStyle": {
                            "width": 2,
                            "color": '#999'
                        }
                    },
                    "splitLine": {
                        "distance": -52,
                        "length": 14,
                        "lineStyle": {
                            "width": 3,
                            "color": '#999'
                        }
                    },
                    "axisLabel": {
                        "distance": -20,
                        "color": '#999',
                        "fontSize": 20
                    },
                    "anchor": {
                        "show": "false"
                    },
                    "title": {
                        "show": "false"
                    },
                    "detail": {
                        "valueAnimation": "true",
                        "width": '60%',
                        "lineHeight": 40,
                        "borderRadius": 8,
                        "offsetCenter": [0, '-15%'],
                        "fontSize": 30,
                        "fontWeight": 'bolder',
                        "formatter": '{value} °C',
                        "color": 'inherit'
                    },
                    "data": [
                        {
                            "value": df_last_300['Temperature'].iloc[-1]
                        }
                    ]
                },
                {
                    "type": 'gauge',
                    "center": ['50%', '60%'],
                    "startAngle": 200,
                    "endAngle": -20,
                    "min": 0,
                    "max": 60,
                    "itemStyle": {
                        "color": '#FD7347'
                    },
                    "progress": {
                        "show": "true",
                        "width": 8
                    },
                    "pointer": {
                        "show": "false"
                    },
                    "axisLine": {
                        "show": "false"
                    },
                    "axisTick": {
                        "show": "false"
                    },
                    "splitLine": {
                        "show": "false"
                    },
                    "axisLabel": {
                        "show": "false"
                    },
                    "detail": {
                        "show": "false"
                    },
                    "data": [
                        {
                            "value": df_last_300['Temperature'].iloc[-1]
                        }
                    ]
                }
            ]
        }
        st_echarts(options=option, key="1")


    with row1col2:
        
        # Draw line chart for Timestamp vs Temperature
        st.line_chart(df_last_300.set_index('Timestamp')['Temperature'])


    row2col1, row2col2 = st.columns(2)

    ec_df = df_last_300[['Timestamp', 'EC']].copy()
    ph_df = df_last_300[['Timestamp', 'pH']].copy()

    ec_chart= alt.Chart(ec_df).mark_area(
            line={'color':'darkgreen'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='white', offset=0),
                    alt.GradientStop(color='darkgreen', offset=1)],
                x1=1,
                x2=1,
                y1=1,
                y2=0
            )
    ).encode(
            alt.X('Timestamp'),
            alt.Y('EC',scale=alt.Scale(domain=[0, 1600]))
    )

    # ph_chart = alt.Chart(ph_df).mark_line(color="#FFD433").encode(
    #     x='Timestamp',
    #     y = alt.Y('pH', scale=alt.Scale(domain=[0, 14]))
    # )
    
    ph_chart= alt.Chart(ph_df).mark_area(
            line={'color':'#FFD433'},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='white', offset=0),
                    alt.GradientStop(color='#FFD433', offset=1)],
                x1=1,
                x2=1,
                y1=1,
                y2=0
            )
    ).encode(
            alt.X('Timestamp'),
            alt.Y('pH',scale=alt.Scale(domain=[0, 12]))
    )
    with row2col1:
        st.header("EC Level")

        # Draw line chart for Timestamp vs EC
        st.altair_chart(ec_chart,use_container_width=True)

    with row2col2:
        st.header("pH Level")
        # Draw line chart for Timestamp vs pH
        st.altair_chart(ph_chart,use_container_width=True)

    st.header("pH VS. EC")
    data_df = data_df.loc[data_df['EC'] * data_df['pH'] != 0]
    brush = alt.selection_interval()

    ph_vs_ec = alt.Chart(data_df).mark_circle().encode(
        x = alt.X('EC'),
        y = alt.Y('pH',scale=alt.Scale(domain=[0, 14])),
        color=alt.condition(brush, alt.value('steelblue'), alt.value('grey'))
    ).add_params(brush)

    st.altair_chart(ph_vs_ec,use_container_width=True)

    st.header("Light Intensity")
    # Draw line chart for Timestamp vs Light
    st.line_chart(df_last_300.set_index('Timestamp')['Light'])

    st.header("Raw Data")
    st.write(df_last_300)
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

df_last_300 = data_df.tail(1370)

# creating a single-element container
placeholder = st.empty()

with placeholder.container():

    # create two columns
    row1col1, row1col2 = st.columns(2)


    with row1col1:
        st.header("Temperature")
        try:
            option = {
                "tooltip": {
                    "formatter": '{a} <br/>{b} : {c}%'
                },
                "series": [{
                    "name": 'Temp',
                    "type": 'gauge',
                    "startAngle": 180,
                    "endAngle": 0,
                    "progress": {
                        "show": "true"
                    },
                    "radius":'100%', 

                    "itemStyle": {
                        "color": '#58D9F9',
                        "shadowColor": 'rgba(0,138,255,0.45)',
                        "shadowBlur": 10,
                        "shadowOffsetX": 1,
                        "shadowOffsetY": 2,
                        "radius": '55%',
                    },
                    "progress": {
                        "show": "true",
                        "roundCap": "true",
                        "width": 15
                    },
                    "pointer": {
                        "length": '60%',
                        "width": 8,
                        "offsetCenter": [0, '5%']
                    },
                    "detail": {
                        "valueAnimation": "true",
                        "formatter": '{value} °C',
                        "backgroundColor": '#58D9F9',
                        "width": '100%',
                        "lineHeight": 100,
                        "height": 50,
                        "borderRadius": 90,
                        "offsetCenter": [0, '50%'],
                        "valueAnimation": "true",
                    },
                    "data": [{
                        "value": df_last_300['Temperature'].iloc[-1],
                        "name": 'Temperature'
                        
                    }]
                }]
            }
            st_echarts(options=option, key="1")
        except Exception as e:
            print(e)

        

    with row1col2:
        
        # Draw line chart for Timestamp vs Temperature
        st.line_chart(df_last_300.set_index('Timestamp')['Temperature'])


    row2col1, row2col2 = st.columns(2)

    ec_df = df_last_300[['Timestamp', 'EC']].copy()
    ph_df = df_last_300[['Timestamp', 'pH']].copy()

    ec_chart = alt.Chart(ec_df).mark_line(color="#FF5733").encode(
        x='Timestamp',
        y = alt.Y('EC', scale=alt.Scale(domain=[0, 1200]))
    )

    ph_chart = alt.Chart(ph_df).mark_line(color="#FFD433").encode(
        x='Timestamp',
        y = alt.Y('pH', scale=alt.Scale(domain=[0, 10]))
    )

    with row2col1:
        st.header("EC Level")
        # Draw line chart for Timestamp vs EC
        st.altair_chart(ec_chart)

    with row2col2:
        st.header("pH Level")
        # Draw line chart for Timestamp vs pH
        st.altair_chart(ph_chart)

    st.header("Light Intensity")
    # Draw line chart for Timestamp vs Light
    st.line_chart(df_last_300.set_index('Timestamp')['Light'])

    st.header("Raw Data")
    st.write(df_last_300)
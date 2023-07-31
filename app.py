import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from gsheetsdb import connect
import altair as alt
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Water Data Pi", page_icon=":books:")
st.title(":books: Water Data Pi :books:")
# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

# Perform SQL query on the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.

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
data_df.Temperature = data_df.Temperature.round(2)

data_df = data_df.rename(columns={'_6': 'LightPercentage', '_2': 'EC','_4': 'WaterLevel','_6': 'LightPercentage'})
st.write(data_df)

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
                "shadowOffsetX": 2,
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
                "formatter": '{value}%',
                "backgroundColor": '#58D9F9',
                #"borderColor": '#999',
                #"borderWidth": 4,
                "width": '90%',
                "lineHeight": 30,
                "height": 20,
                "borderRadius": 90,
                "offsetCenter": [0, '40%'],
                "valueAnimation": "true",
            },
            "data": [{
                "value": data_df['Temperature'].iloc[-1],
                "name": ' C'
            }]
        }]
    }
    st_echarts(options=option, key="1")
except Exception as e:
    print(e)

    


# Draw line chart for Timestamp vs Temperature
st.line_chart(data_df.set_index('Timestamp')['Temperature'])

custom_chart = alt.Chart(data_df).mark_line().encode(
    x='Timestamp',
    y='EC',
    color=alt.Color('animal',
            scale=alt.Scale(
                domain=['antelope', 'velociraptor'],
                range=['blue', 'red'])
                )
)
#st.line_chart(data_df.set_index('Timestamp')['EC'])

# Draw line chart for Timestamp vs EC
st.area_chart(data = data_df, x="Timestamp", y = "EC")

# Draw line chart for Timestamp vs pH
st.line_chart(data_df.set_index('Timestamp')['pH'])

# Draw line chart for Timestamp vs Light
st.line_chart(data_df.set_index('Timestamp')['Light'])

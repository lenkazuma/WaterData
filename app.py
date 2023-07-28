import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from gsheetsdb import connect


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

data_df = data_df.rename(columns={'_6': 'LightPercentage', '_2': 'EC'})
st.write(data_df)

# Draw line chart for Timestamp vs Temperature
st.line_chart(data_df.set_index('Timestamp')['Temperature'])

# Draw line chart for Timestamp vs EC
st.line_chart(data_df.set_index('Timestamp')['_2'])

# Draw line chart for Timestamp vs pH
st.line_chart(data_df.set_index('Timestamp')['pH'])

# Draw line chart for Timestamp vs Light
st.line_chart(data_df.set_index('Timestamp')['Light'])

# streamlit_app.py

import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect


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

@st.cache_data(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

sheet_url = st.secrets["private_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')

@st.cache_resource(allow_output_mutation=True)
def create_database_connection():
    # Code to create and return the database connection
    return conn

# Use the cached database connection
db_conn = create_database_connection()


# Print results.
for row in rows:
    st.write(f"{row.Timestamp} Temperature :{row.Temperature}:")
# Streamlit GoogleSheet Data visualisation
WaterData is a Streamlit dashboard for DFRobot water sensors (temperature, EC, pH, water level, light) whose readings are logged to a Google Sheet, e.g. by a Raspberry Pi. It reads the sheet with a read-only service account and plots the live data.

## Features
- Reads the sheet via [gspread](https://docs.gspread.org/) with a read-only service account (a `#gid=` in the URL selects a specific tab)
- Data is cached for 60 seconds, with a **Refresh now** button
- Latest-reading metric cards with change since the previous reading
- Configurable alert thresholds for temperature, pH and EC
- Temperature gauge, EC / pH / water level / light charts and a brushable pH-vs-EC scatter plot
- Range slider to choose which readings to show, and CSV download of the selected range

## Requirements
- Python 3.10+
- Streamlit, Pandas, gspread, Google Auth, Altair, Streamlit Echarts (see `requirements.txt`)

## Installation

1. Clone the repository:
    ```sh
    git clone git@github.com:lenkazuma/WaterData.git
    cd WaterData
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up your Google Cloud Platform (GCP) service account:
    - Follow the instructions [here](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) to create a service account and download the JSON key file.
    - Share your Google Sheet with the service account email (Viewer access is enough).
    - The first row of the sheet must be the header row, in this column order: timestamp, temperature, EC, pH, water level, light, light %.

4. Add your GCP service account credentials and Google Sheet URL to Streamlit secrets:
    - Create a file named `.streamlit/secrets.toml` in the project root directory.
    - Add the following configuration, replacing the placeholders with your actual credentials and sheet URL. Note that `private_gsheets_url` must be a top-level key, placed before the `[gcp_service_account]` table:
    ```toml
    private_gsheets_url = "https://docs.google.com/spreadsheets/d/your-sheet-id/edit#gid=0"

    [gcp_service_account]
    type = "service_account"
    project_id = "your-project-id"
    private_key_id = "your-private-key-id"
    private_key = "your-private-key"
    client_email = "your-client-email"
    client_id = "your-client-id"
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
    client_x509_cert_url = "your-client-x509-cert-url"
    ```

## Usage

Run the Streamlit app:
```sh
streamlit run app.py
```

## Project Structure

- `app.py`: The Streamlit dashboard.
- `waterdata.py`: Sheet parsing, cleaning, metric and alert helpers (no Streamlit dependency).
- `tests/`: pytest tests for `waterdata.py` (`pip install pytest && pytest -q`).
- `requirements.txt`: The list of required Python packages.
- `.streamlit/secrets.toml`: File to store Streamlit secrets (not included in the repository for security reasons).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License

This project is licensed under the MIT License.

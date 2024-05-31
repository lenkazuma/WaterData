# Water Data 

WaterData  is a Streamlit application that connects to a Google Sheet to read and plot live data updated on the sheet. The project uses Google API for authentication and data retrieval.

## Features
- Connects to a Google Sheet using Google API
- Retrieves and displays live data from the sheet
- Plots data using various visualization libraries including Altair and Streamlit Echarts
- Allows users to select a range of data to visualize

## Requirements
- Python 3.7+
- Streamlit
- Pandas
- Google Auth
- Gsheetsdb
- Altair
- Streamlit Echarts

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
    - Add the service account email to your Google Sheet with edit permissions.

4. Add your GCP service account credentials and Google Sheet URL to Streamlit secrets:
    - Create a file named `.streamlit/secrets.toml` in the project root directory.
    - Add the following configuration, replacing the placeholders with your actual credentials and sheet URL:
    ```toml
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

    [private_gsheets_url]
    sheet_url = "your-google-sheet-url"
    ```

## Usage

Run the Streamlit app:
```sh
streamlit run app.py
```

## Project Structure

- `app.py`: The main application file containing the Streamlit code.
- `requirements.txt`: The list of required Python packages.
- `.streamlit/secrets.toml`: File to store Streamlit secrets (not included in the repository for security reasons).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License

This project is licensed under the MIT License.

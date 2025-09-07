import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# --- Configuration ---
# You need to create a Google Cloud Project, enable the Google Sheets API,
# create a Service Account, and download the JSON credentials file.
# IMPORTANT: Share your Google Sheet with the email address of the Service Account.
# This file should also be added to your .gitignore to keep it private.
SERVICE_ACCOUNT_FILE = 'client_secret.json'

# The key can be found in the URL of your Google Sheet.
# Example URL: https://docs.google.com/spreadsheets/d/your-sheet-key-goes-here/edit
GOOGLE_SHEET_KEY = os.getenv("GOOGLE_SHEET_KEY")

# The file containing the trade data to upload.
JSON_FILE = 'trade_log.json'


def upload_to_gsheet():
    """
    Reads trade data from a JSON file and appends it as a new row
    in the specified Google Sheet.
    """
    try:
        # Step 1: Read the data from the JSON file
        if not os.path.exists(JSON_FILE):
            print(f"Error: {JSON_FILE} not found. Exiting.")
            return

        with open(JSON_FILE, 'r') as f:
            trade_data = json.load(f)
        
        # --- NEW: Print the entire dictionary for debugging ---
        print("DEBUGGING: Contents of trade_log.json:", trade_data)
        
        print(f"Successfully read data from {JSON_FILE}.")

        # Step 2: Authenticate with Google Sheets API using the service account
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)
        print("Authentication with Google Sheets successful.")

        # Step 3: Open the Google Sheet and select the first worksheet
        sheet = client.open_by_key(GOOGLE_SHEET_KEY).sheet1
        print("Google Sheet opened successfully.")

        # Step 4: Prepare the data as a list for a new row.
        # This assumes your sheet columns are in this order:
        # timestamp, trading_pair, side, trade_price, trade_amount, total_usd_cost, fee_cost, fee_currency, initial_crypto_asset_balance, final_crypto_asset_balance, final_sgd_balance
        row_data = [
            trade_data.get("timestamp", ""),
            trade_data.get("trading_pair", ""),
            trade_data.get("side", ""),
            trade_data.get("trade_price", ""),
            trade_data.get("trade_amount", ""),
            trade_data.get("total_usd_cost", ""),
            trade_data.get("fee_cost", ""),
            trade_data.get("fee_currency", ""),
        ]

        # Step 5: Append the new row to the worksheet
        sheet.append_row(row_data)
        print("Trade data successfully appended to Google Sheet.")
        
    except FileNotFoundError as e:
        print(f"An error occurred: {e}. Make sure the file exists and the path is correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    upload_to_gsheet()

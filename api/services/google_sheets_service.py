"""
Google Sheets Service
Handles Google Sheets API v4 integration: token refresh, spreadsheet creation, appending lead rows, and reading recent rows.
"""
import os
import logging
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
SHEETS_API_BASE = "https://sheets.googleapis.com/v4/spreadsheets"

def _get_credentials():
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except Exception:
        pass

    return {
        "client_id": os.environ.get("GMAIL_CLIENT_ID", ""),
        "client_secret": os.environ.get("GMAIL_CLIENT_SECRET", ""),
        "redirect_uri": os.environ.get("GOOGLE_SHEETS_REDIRECT_URI") or os.environ.get("GMAIL_REDIRECT_URI", "http://localhost:8080/api/auth/gmail/callback"),
    }

def get_valid_sheets_token(client_obj):
    """
    Get a valid access token for Google Sheets API.
    Refreshes automatically if expired.
    """
    config = client_obj.google_sheets_config or {}
    access_token = config.get("access_token")
    refresh_token = config.get("refresh_token")
    token_expires_at = config.get("token_expires_at", 0)

    now_ts = datetime.now(timezone.utc).timestamp()
    if access_token and token_expires_at > (now_ts + 300):
        return access_token

    if not refresh_token:
        raise ValueError("Google Sheets refresh token missing. Please re-authenticate.")

    creds = _get_credentials()
    payload = {
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    resp = requests.post(GOOGLE_TOKEN_ENDPOINT, data=payload, timeout=20)
    if resp.status_code != 200:
        logger.error("Failed to refresh Google Sheets token: %s", resp.text)
        raise ValueError(f"Failed to refresh Google token: {resp.text}")

    data = resp.json()
    new_access_token = data.get("access_token")
    expires_in = data.get("expires_in", 3600)

    config["access_token"] = new_access_token
    config["token_expires_at"] = now_ts + expires_in
    client_obj.google_sheets_config = config
    client_obj.save(update_fields=["google_sheets_config"])

    return new_access_token

def create_default_spreadsheet(client_obj):
    """
    Create a new Google Spreadsheet titled 'UWOConnect Leads & Messages' with standard headers.
    """
    token = get_valid_sheets_token(client_obj)

    body = {
        "properties": {
            "title": f"UWOConnect Leads ({client_obj.business_name})",
        },
        "sheets": [
            {
                "properties": {
                    "title": "Leads & Messages",
                    "gridProperties": {
                        "frozenRowCount": 1
                    }
                },
                "data": [
                    {
                        "startRow": 0,
                        "startColumn": 0,
                        "rowData": [
                            {
                                "values": [
                                    {"userEnteredValue": {"stringValue": "Timestamp"}},
                                    {"userEnteredValue": {"stringValue": "Channel"}},
                                    {"userEnteredValue": {"stringValue": "Contact Name"}},
                                    {"userEnteredValue": {"stringValue": "Phone / Email"}},
                                    {"userEnteredValue": {"stringValue": "Lead Type"}},
                                    {"userEnteredValue": {"stringValue": "Message / Content"}},
                                    {"userEnteredValue": {"stringValue": "Status"}},
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    resp = requests.post(SHEETS_API_BASE, json=body, headers=headers, timeout=20)
    if resp.status_code not in (200, 201):
        logger.error("Failed to create Google Spreadsheet: %s", resp.text)
        if "SERVICE_DISABLED" in resp.text or "has not been used in project" in resp.text:
            raise ValueError("Google Sheets API is disabled in your Google Cloud Console. Please enable Google Sheets API in Google Cloud Console.")
        raise ValueError(f"Failed to create Google Spreadsheet: {resp.text}")

    data = resp.json()
    spreadsheet_id = data.get("spreadsheetId")
    spreadsheet_url = data.get("spreadsheetUrl")

    config = client_obj.google_sheets_config or {}
    config["spreadsheet_id"] = spreadsheet_id
    config["spreadsheet_name"] = f"UWOConnect Leads ({client_obj.business_name})"
    config["sheet_name"] = "Leads & Messages"
    config["spreadsheet_url"] = spreadsheet_url
    client_obj.google_sheets_config = config
    client_obj.save(update_fields=["google_sheets_config"])

    return spreadsheet_id, spreadsheet_url

def append_lead_row(client_obj, channel, name, contact_info, lead_type, content, status="NEW"):
    """
    Append a single lead/message row to the connected Google Spreadsheet.
    """
    token = get_valid_sheets_token(client_obj)
    config = client_obj.google_sheets_config or {}
    spreadsheet_id = config.get("spreadsheet_id")

    if not spreadsheet_id:
        spreadsheet_id, _ = create_default_spreadsheet(client_obj)

    sheet_name = config.get("sheet_name", "Leads & Messages")
    range_name = f"'{sheet_name}'!A:G"

    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    row_values = [timestamp_str, str(channel), str(name), str(contact_info), str(lead_type), str(content), str(status)]

    url = f"{SHEETS_API_BASE}/{spreadsheet_id}/values/{range_name}:append?valueInputOption=USER_ENTERED"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {"values": [row_values]}

    resp = requests.post(url, json=body, headers=headers, timeout=20)
    if resp.status_code != 200:
        logger.error("Failed appending row to Google Sheets: %s", resp.text)
        raise ValueError(f"Failed to append row to Google Sheets: {resp.text}")

    # Update synced row count
    config["rows_synced"] = config.get("rows_synced", 0) + 1
    config["last_sync_time"] = datetime.now(timezone.utc).isoformat()
    client_obj.google_sheets_config = config
    client_obj.save(update_fields=["google_sheets_config"])

    return True

def read_sheet_rows(client_obj, max_rows=20):
    """
    Read the most recent rows from the connected Google Spreadsheet.
    """
    token = get_valid_sheets_token(client_obj)
    config = client_obj.google_sheets_config or {}
    spreadsheet_id = config.get("spreadsheet_id")

    if not spreadsheet_id:
        return []

    sheet_name = config.get("sheet_name", "Leads & Messages")
    range_name = f"'{sheet_name}'!A1:G100"

    url = f"{SHEETS_API_BASE}/{spreadsheet_id}/values/{range_name}"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(url, headers=headers, timeout=20)
    if resp.status_code != 200:
        logger.error("Failed reading rows from Google Sheets: %s", resp.text)
        return []

    values = resp.json().get("values", [])
    if len(values) <= 1:
        return []

    headers_row = values[0]
    data_rows = values[1:]
    
    formatted_rows = []
    for r in reversed(data_rows[-max_rows:]):
        formatted_rows.append({
            "timestamp": r[0] if len(r) > 0 else "",
            "channel": r[1] if len(r) > 1 else "",
            "name": r[2] if len(r) > 2 else "",
            "contact": r[3] if len(r) > 3 else "",
            "lead_type": r[4] if len(r) > 4 else "",
            "content": r[5] if len(r) > 5 else "",
            "status": r[6] if len(r) > 6 else "",
        })

    return formatted_rows

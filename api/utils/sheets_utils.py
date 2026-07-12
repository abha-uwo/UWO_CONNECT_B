import requests
import json

def sync_lead_to_google_sheet(client, contact):
    """
    Client properties settings checks and triggers REST API call
    to sync contact details to Google Sheets.
    """
    settings = getattr(client, 'settings', {}) or {}
    sheets_config = settings.get('google_sheets', {})
    
    if not sheets_config or not sheets_config.get('enabled'):
        return False
        
    spreadsheet_id = sheets_config.get('spreadsheet_id')
    access_token = sheets_config.get('access_token')
    
    if not spreadsheet_id or not access_token:
        return False
        
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/A1:append?valueInputOption=RAW"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    tags_str = ", ".join(contact.tags) if isinstance(contact.tags, list) else str(contact.tags)
    
    body = {
        "range": "A1",
        "majorDimension": "ROWS",
        "values": [
            [
                contact.name or "N/A",
                contact.phone_number or "N/A",
                contact.email or "N/A",
                contact.stage or "NEW",
                tags_str,
                contact.created_at.strftime('%Y-%m-%d %H:%M:%S') if contact.created_at else "N/A"
            ]
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=5)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        print(f"[Sheets Sync Error] {str(e)}")
        return False

import os
import time
import logging
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DOCS_API_BASE = "https://docs.googleapis.com/v1/documents"
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3/files"
TOKEN_URL = "https://oauth2.googleapis.com/token"

def get_valid_docs_token(client_obj):
    """
    Retrieves a valid Google Docs OAuth access token for the given client.
    Refreshes automatically if expired.
    """
    config = client_obj.google_docs_config or {}
    access_token = config.get("access_token")
    refresh_token = config.get("refresh_token")
    expires_at = config.get("token_expires_at", 0)

    # Return access token if still valid (with 60s buffer)
    if access_token and time.time() < (expires_at - 60):
        return access_token

    if not refresh_token:
        raise ValueError("Google Docs refresh token missing. Please re-authenticate.")

    client_id = os.getenv("GMAIL_CLIENT_ID")
    client_secret = os.getenv("GMAIL_CLIENT_SECRET")

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    resp = requests.post(TOKEN_URL, data=payload, timeout=15)
    if resp.status_code != 200:
        logger.error("Failed to refresh Google Docs token: %s", resp.text)
        raise ValueError("Failed to refresh Google Docs access token.")

    token_data = resp.json()
    new_access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in", 3600)

    config["access_token"] = new_access_token
    config["token_expires_at"] = time.time() + expires_in
    client_obj.google_docs_config = config
    client_obj.save(update_fields=["google_docs_config"])

    return new_access_token


def create_google_doc(client_obj, title=None, content=None):
    """
    Creates a new Google Document in Google Drive with initial text content.
    Returns (doc_id, doc_url).
    """
    token = get_valid_docs_token(client_obj)

    if not title:
        biz_name = getattr(client_obj, 'business_name', 'Client') or 'Client'
        title = f"UWOConnect Document ({biz_name})"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # 1. Create blank document
    body = {"title": title}
    resp = requests.post(DOCS_API_BASE, json=body, headers=headers, timeout=20)
    if resp.status_code not in (200, 201):
        logger.error("Failed to create Google Document: %s", resp.text)
        if "SERVICE_DISABLED" in resp.text or "has not been used in project" in resp.text:
            raise ValueError("Google Docs API is disabled in your Google Cloud Console. Please enable Google Docs API.")
        raise ValueError(f"Failed to create Google Document: {resp.text}")

    data = resp.json()
    doc_id = data.get("documentId")
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    # 2. Insert initial content if provided
    if content:
        insert_req = {
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": content + "\n\n"
                    }
                }
            ]
        }
        requests.post(f"{DOCS_API_BASE}/{doc_id}:batchUpdate", json=insert_req, headers=headers, timeout=15)

    # 3. Update client config with document metadata
    config = client_obj.google_docs_config or {}
    config["default_doc_id"] = doc_id
    config["default_doc_name"] = title
    config["default_doc_url"] = doc_url
    config["docs_created_count"] = config.get("docs_created_count", 0) + 1
    config["last_sync_time"] = datetime.now(timezone.utc).isoformat()

    recent_docs = config.get("recent_docs", [])
    doc_entry = {
        "doc_id": doc_id,
        "title": title,
        "url": doc_url,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    recent_docs.insert(0, doc_entry)
    config["recent_docs"] = recent_docs[:10]  # keep top 10

    client_obj.google_docs_config = config
    client_obj.save(update_fields=["google_docs_config"])

    return doc_id, doc_url


def append_text_to_doc(client_obj, doc_id=None, text=""):
    """
    Appends text content to an existing Google Document.
    """
    token = get_valid_docs_token(client_obj)
    config = client_obj.google_docs_config or {}

    if not doc_id:
        doc_id = config.get("default_doc_id")
        if not doc_id:
            doc_id, _ = create_google_doc(client_obj)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Fetch document structure to find end index
    resp = requests.get(f"{DOCS_API_BASE}/{doc_id}", headers=headers, timeout=15)
    if resp.status_code != 200:
        logger.error("Failed to read Google Document %s: %s", doc_id, resp.text)
        raise ValueError("Failed to read Google Document.")

    doc_data = resp.json()
    content_list = doc_data.get("body", {}).get("content", [])
    end_index = 1
    if content_list:
        end_index = content_list[-1].get("endIndex", 1) - 1
        if end_index < 1:
            end_index = 1

    timestamp_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
    formatted_text = f"\n--- [{timestamp_str}] ---\n{text}\n"

    batch_req = {
        "requests": [
            {
                "insertText": {
                    "location": {"index": end_index},
                    "text": formatted_text
                }
            }
        ]
    }

    append_resp = requests.post(f"{DOCS_API_BASE}/{doc_id}:batchUpdate", json=batch_req, headers=headers, timeout=15)
    if append_resp.status_code != 200:
        logger.error("Failed appending text to Google Document %s: %s", doc_id, append_resp.text)
        return False

    config["last_sync_time"] = datetime.now(timezone.utc).isoformat()
    client_obj.google_docs_config = config
    client_obj.save(update_fields=["google_docs_config"])

    return True


def list_client_docs(client_obj):
    """
    Returns recent documents generated by the client.
    """
    config = client_obj.google_docs_config or {}
    return config.get("recent_docs", [])

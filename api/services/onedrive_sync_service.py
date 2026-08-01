"""
OneDrive Sync Service
Handles downloading media from WhatsApp/Facebook/Instagram and uploading to OneDrive.
Called from the webhook pipeline whenever a media message arrives.
"""
import os
import io
import logging
import threading
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)


# ── Media download helpers ──────────────────────────────────────────

def _download_whatsapp_media(media_id, access_token):
    """
    Download a WhatsApp media file and return (bytes, filename, mime_type).
    Returns (None, None, None) on failure.
    """
    try:
        # Step 1: Get media URL
        url_resp = requests.get(
            f"https://graph.facebook.com/v18.0/{media_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        if url_resp.status_code != 200:
            logger.warning("Failed to get WA media URL for %s: %s", media_id, url_resp.text)
            return None, None, None

        data = url_resp.json()
        media_url = data.get("url")
        mime_type = data.get("mime_type", "application/octet-stream")

        if not media_url:
            return None, None, None

        # Step 2: Download the actual file
        file_resp = requests.get(
            media_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=60,
        )
        if file_resp.status_code != 200:
            logger.warning("Failed to download WA media %s", media_url)
            return None, None, None

        # Infer extension from mime type
        ext = _mime_to_ext(mime_type)
        filename = f"wa_{media_id}{ext}"
        return file_resp.content, filename, mime_type

    except Exception as e:
        logger.error("WhatsApp media download failed: %s", e)
        return None, None, None


def _download_fb_ig_media(media_url, access_token):
    """
    Download a Facebook/Instagram media file from a URL.
    Returns (bytes, filename, mime_type).
    """
    try:
        resp = requests.get(
            media_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=60,
        )
        if resp.status_code != 200:
            logger.warning("Failed to download FB/IG media: %s", media_url)
            return None, None, None

        mime_type = resp.headers.get("Content-Type", "application/octet-stream").split(";")[0].strip()
        ext = _mime_to_ext(mime_type)
        # Use last segment of URL as base name
        base = media_url.rstrip("/").split("/")[-1].split("?")[0] or "media"
        filename = f"{base}{ext}" if not base.endswith(ext) else base
        return resp.content, filename, mime_type

    except Exception as e:
        logger.error("FB/IG media download failed: %s", e)
        return None, None, None


def _mime_to_ext(mime_type):
    """Map MIME type to file extension."""
    MIME_MAP = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "audio/mpeg": ".mp3",
        "audio/ogg": ".ogg",
        "audio/opus": ".opus",
        "audio/amr": ".amr",
        "audio/aac": ".aac",
        "video/mp4": ".mp4",
        "video/mpeg": ".mpeg",
        "video/3gpp": ".3gp",
        "application/pdf": ".pdf",
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.ms-excel": ".xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/vnd.ms-powerpoint": ".ppt",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
        "text/plain": ".txt",
        "text/csv": ".csv",
        "application/zip": ".zip",
        "application/x-rar-compressed": ".rar",
        "application/octet-stream": ".bin",
    }
    return MIME_MAP.get(mime_type, "")


# ── Sync dispatcher ─────────────────────────────────────────────────

def sync_whatsapp_media_to_onedrive(client, msg_data):
    """
    Called from the WhatsApp webhook pipeline.
    Runs in a background thread to avoid blocking the webhook response.

    msg_data: raw message dict from the WhatsApp webhook payload
    """
    if not client.onedrive_enabled:
        return

    msg_type = msg_data.get("type", "text")

    # Only handle media types
    MEDIA_TYPES = {"image", "document", "audio", "video", "sticker"}
    if msg_type not in MEDIA_TYPES:
        return

    # Run async
    t = threading.Thread(
        target=_do_whatsapp_sync,
        args=(client.id, msg_data, msg_type),
        daemon=True,
    )
    t.start()


def _do_whatsapp_sync(client_id, msg_data, msg_type):
    """Background thread: download & upload WhatsApp media to OneDrive."""
    try:
        from api.models import Client
        client = Client.objects.get(id=client_id)
        access_token = client.whatsapp_access_token

        # Get media payload
        media_payload = msg_data.get(msg_type, {})
        media_id = media_payload.get("id")
        if not media_id or not access_token:
            return

        file_bytes, downloaded_filename, mime_type = _download_whatsapp_media(media_id, access_token)
        if not file_bytes:
            logger.warning("WA media download returned nothing for id=%s", media_id)
            return

        # Prefer original filename if present in WhatsApp payload
        filename = media_payload.get("filename") or downloaded_filename

        from api.views.onedrive_views import upload_file_to_onedrive
        result = upload_file_to_onedrive(
            client_obj=client,
            file_bytes=file_bytes,
            file_name=filename,
            connector="WHATSAPP",
        )
        logger.info("OneDrive WA sync: %s → %s", filename, result.get("target_path"))

        # Update synced_count
        config = client.onedrive_config or {}
        config["synced_count"] = config.get("synced_count", 0) + 1
        client.onedrive_config = config
        client.save(update_fields=["onedrive_config"])

    except Exception as e:
        logger.error("OneDrive WhatsApp sync failed: %s", e)


def sync_fb_ig_media_to_onedrive(client, msg_data, platform="FACEBOOK"):
    """
    Called from the Facebook/Instagram webhook pipeline.
    Runs in a background thread.

    msg_data: the message dict from the FB/IG messaging event
    platform: "FACEBOOK" or "INSTAGRAM"
    """
    if not client.onedrive_enabled:
        return

    # Check for attachments with media URLs
    attachments = msg_data.get("attachments", [])
    if not attachments:
        return

    t = threading.Thread(
        target=_do_fb_ig_sync,
        args=(client.id, attachments, platform),
        daemon=True,
    )
    t.start()


def _do_fb_ig_sync(client_id, attachments, platform):
    """Background thread: download & upload FB/IG media to OneDrive."""
    try:
        from api.models import Client
        client = Client.objects.get(id=client_id)
        config = client.facebook_config or {}
        access_token = config.get("page_access_token") or config.get("user_access_token", "")

        for attachment in attachments:
            payload = attachment.get("payload", {})
            media_url = payload.get("url")
            if not media_url:
                continue

            file_bytes, filename, mime_type = _download_fb_ig_media(media_url, access_token)
            if not file_bytes:
                continue

            from api.views.onedrive_views import upload_file_to_onedrive
            result = upload_file_to_onedrive(
                client_obj=client,
                file_bytes=file_bytes,
                file_name=filename,
                connector=platform,
            )
            logger.info("OneDrive %s sync: %s → %s", platform, filename, result.get("target_path"))

            od_config = client.onedrive_config or {}
            od_config["synced_count"] = od_config.get("synced_count", 0) + 1
            client.onedrive_config = od_config
            client.save(update_fields=["onedrive_config"])

    except Exception as e:
        logger.error("OneDrive %s sync failed: %s", platform, e)


def sync_team_file_to_onedrive(client, file_bytes, filename, uploader_name=None):
    """
    Sync a team file upload to OneDrive.
    Called from team file upload views.
    uploader_name: the team member's name/username for routing to Team/<name>/
    """
    if not client.onedrive_enabled:
        return

    t = threading.Thread(
        target=_do_team_file_sync,
        args=(client.id, file_bytes, filename, uploader_name),
        daemon=True,
    )
    t.start()


def _do_team_file_sync(client_id, file_bytes, filename, uploader_name):
    try:
        from api.models import Client
        client = Client.objects.get(id=client_id)

        from api.views.onedrive_views import upload_file_to_onedrive
        result = upload_file_to_onedrive(
            client_obj=client,
            file_bytes=file_bytes,
            file_name=filename,
            connector="TEAM",
            employee_name=uploader_name,
        )
        logger.info("OneDrive team sync: %s → %s", filename, result.get("target_path"))

        config = client.onedrive_config or {}
        config["synced_count"] = config.get("synced_count", 0) + 1
        client.onedrive_config = config
        client.save(update_fields=["onedrive_config"])

    except Exception as e:
        logger.error("OneDrive team sync failed: %s", e)

import json
import mimetypes
import uuid
from functools import lru_cache
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from app.core.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@lru_cache
def get_credentials():
    if settings.google_service_account_json:
        info = json.loads(settings.google_service_account_json)
        return Credentials.from_service_account_info(info, scopes=SCOPES)

    if settings.google_service_account_file:
        return Credentials.from_service_account_file(
            settings.google_service_account_file,
            scopes=SCOPES,
        )

    raise RuntimeError("Google service account is not configured")


@lru_cache
def get_sheets_service():
    return build("sheets", "v4", credentials=get_credentials())


@lru_cache
def get_drive_service():
    return build("drive", "v3", credentials=get_credentials())


def read_sheet_rows(tab_name: str) -> list[dict]:
    service = get_sheets_service()

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=settings.google_sheet_id,
            range=f"{tab_name}!A1:Z",
        )
        .execute()
    )

    values = result.get("values", [])
    if not values:
        return []

    headers = [h.strip() for h in values[0]]
    rows = []

    for index, row in enumerate(values[1:], start=2):
        item = {"_row_number": index}

        for header_index, header in enumerate(headers):
            item[header] = row[header_index] if header_index < len(row) else ""

        rows.append(item)

    return rows


def append_sheet_row(tab_name: str, row: list):
    service = get_sheets_service()

    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=settings.google_sheet_id,
            range=f"{tab_name}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [row]},
        )
        .execute()
    )

    return result


def update_sheet_row(tab_name: str, row_number: int, row: list):
    service = get_sheets_service()

    return (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=settings.google_sheet_id,
            range=f"{tab_name}!A{row_number}:Z{row_number}",
            valueInputOption="USER_ENTERED",
            body={"values": [row]},
        )
        .execute()
    )


def upload_file_to_drive(file_path: str, filename: str, content_type: str | None = None) -> str:
    if not settings.google_drive_folder_id:
        raise RuntimeError("GOOGLE_DRIVE_FOLDER_ID is not configured")

    mime_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"

    service = get_drive_service()

    file_metadata = {
        "name": f"{uuid.uuid4()}-{filename}",
        "parents": [settings.google_drive_folder_id],
    }

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    uploaded_file = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink",
        )
        .execute()
    )

    file_id = uploaded_file["id"]

    if settings.google_drive_public_links:
        service.permissions().create(
            fileId=file_id,
            body={"role": "reader", "type": "anyone"},
        ).execute()

    return uploaded_file.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view"
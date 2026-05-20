import json
import mimetypes
import uuid
from functools import lru_cache

from fastapi import HTTPException, status
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from app.core.config import settings


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _google_config_error(message: str):
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Google configuration error: {message}",
    )


@lru_cache
def get_credentials():
    try:
        service_account_json = (settings.google_service_account_json or "").strip()
        service_account_file = (settings.google_service_account_file or "").strip().strip('"').strip("'")

        if service_account_json:
            info = json.loads(service_account_json)
            return Credentials.from_service_account_info(info, scopes=SCOPES)

        if service_account_file:
            return Credentials.from_service_account_file(
                service_account_file,
                scopes=SCOPES,
            )

        _google_config_error(
            "Set GOOGLE_SERVICE_ACCOUNT_FILE locally or GOOGLE_SERVICE_ACCOUNT_JSON in deployment."
        )

    except HTTPException:
        raise
    except Exception as exc:
        _google_config_error(str(exc))

@lru_cache
def get_sheets_service():
    return build("sheets", "v4", credentials=get_credentials())


@lru_cache
def get_drive_service():
    return build("drive", "v3", credentials=get_credentials())


def read_sheet_rows(tab_name: str) -> list[dict]:
    if not settings.google_sheet_id:
        _google_config_error("GOOGLE_SHEET_ID is missing.")

    try:
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

        headers = [str(header).strip() for header in values[0]]
        rows: list[dict] = []

        for row_number, row in enumerate(values[1:], start=2):
            item = {"_row_number": row_number}

            for index, header in enumerate(headers):
                item[header] = row[index] if index < len(row) else ""

            rows.append(item)

        return rows

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read Google Sheet tab '{tab_name}': {exc}",
        )


def append_sheet_row(tab_name: str, row: list):
    if not settings.google_sheet_id:
        _google_config_error("GOOGLE_SHEET_ID is missing.")

    try:
        service = get_sheets_service()

        return (
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

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to append Google Sheet tab '{tab_name}': {exc}",
        )


def update_sheet_row(tab_name: str, row_number: int, row: list):
    if not settings.google_sheet_id:
        _google_config_error("GOOGLE_SHEET_ID is missing.")

    try:
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

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update Google Sheet tab '{tab_name}': {exc}",
        )


def upload_file_to_drive(
    file_path: str,
    filename: str,
    content_type: str | None = None,
) -> str:
    if not settings.google_drive_folder_id:
        _google_config_error("GOOGLE_DRIVE_FOLDER_ID is missing.")

    try:
        service = get_drive_service()

        mime_type = (
            content_type
            or mimetypes.guess_type(filename)[0]
            or "application/octet-stream"
        )

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

        return uploaded_file.get("webViewLink") or (
            f"https://drive.google.com/file/d/{file_id}/view"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to Google Drive: {exc}",
        )
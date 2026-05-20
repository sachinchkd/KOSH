import json
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from app.core.config import get_settings
from app.models.contribution import Contribution
from app.models.user import User

settings = get_settings()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


def google_is_configured() -> bool:
    return bool(
        settings.google_enabled
        and settings.google_sheet_id
        and (settings.google_service_account_file or settings.google_service_account_json)
    )


def _credentials():
    if settings.google_service_account_json:
        info: dict[str, Any] = json.loads(settings.google_service_account_json)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    if settings.google_service_account_file:
        return service_account.Credentials.from_service_account_file(settings.google_service_account_file, scopes=SCOPES)
    raise RuntimeError("Google service account credentials are not configured")


def append_contribution_to_sheet(contribution: Contribution, member: User, approved_by_name: str | None = None) -> str | None:
    if not google_is_configured():
        return None

    service = build("sheets", "v4", credentials=_credentials())
    values = [[
        contribution.id,
        member.name,
        contribution.month,
        contribution.amount,
        contribution.payment_method,
        contribution.status,
        contribution.photo_url or "",
        contribution.submitted_at.isoformat() if contribution.submitted_at else "",
        contribution.approved_at.isoformat() if contribution.approved_at else "",
        approved_by_name or "",
        contribution.remarks or "",
    ]]

    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=settings.google_sheet_id,
            range="Contributions!A:K",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        )
        .execute()
    )
    return result.get("updates", {}).get("updatedRange")


def upload_file_to_drive(local_path: str | Path, filename: str, mimetype: str | None = None) -> str | None:
    if not google_is_configured() or not settings.google_drive_folder_id:
        return None

    drive = build("drive", "v3", credentials=_credentials())
    metadata = {
        "name": filename,
        "parents": [settings.google_drive_folder_id],
    }
    media = MediaFileUpload(str(local_path), mimetype=mimetype or "application/octet-stream", resumable=False)
    uploaded = drive.files().create(body=metadata, media_body=media, fields="id, webViewLink").execute()

    if settings.google_drive_public_links:
        drive.permissions().create(
            fileId=uploaded["id"],
            body={"type": "anyone", "role": "reader"},
        ).execute()
        uploaded = drive.files().get(fileId=uploaded["id"], fields="id, webViewLink").execute()

    return uploaded.get("webViewLink")

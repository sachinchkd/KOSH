from functools import lru_cache

from fastapi import HTTPException, status
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from app.core.config import settings


SHEETS_SCOPE = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


@lru_cache
def get_sheets_service():
    if not settings.google_sheet_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_SHEET_ID is not configured",
        )

    if not settings.google_service_account_file:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_SERVICE_ACCOUNT_FILE is not configured",
        )

    credentials = Credentials.from_service_account_file(
        settings.google_service_account_file,
        scopes=SHEETS_SCOPE,
    )

    return build("sheets", "v4", credentials=credentials)


def _normalize_header(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


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

    headers = [_normalize_header(header) for header in values[0]]
    rows: list[dict] = []

    for row in values[1:]:
        item = {}

        for index, header in enumerate(headers):
            item[header] = row[index] if index < len(row) else ""

        rows.append(item)

    return rows


def get_member_by_email(email: str) -> dict | None:
    email = email.strip().lower()
    members = read_sheet_rows("Members")

    for member in members:
        member_email = str(member.get("email", "")).strip().lower()

        if member_email == email:
            return member

    return None
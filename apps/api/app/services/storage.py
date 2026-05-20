from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings

settings = get_settings()


class StoredFile:
    def __init__(self, path: Path, public_url: str, filename: str):
        self.path = path
        self.public_url = public_url
        self.filename = filename


async def save_upload(file: UploadFile) -> StoredFile:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = file.filename or "receipt"
    suffix = Path(original_name).suffix.lower() or ".jpg"
    safe_name = f"{uuid4().hex}{suffix}"
    destination = upload_dir / safe_name

    contents = await file.read()
    destination.write_bytes(contents)

    public_url = f"{settings.public_upload_base_url.rstrip('/')}/{safe_name}"
    return StoredFile(destination, public_url, safe_name)

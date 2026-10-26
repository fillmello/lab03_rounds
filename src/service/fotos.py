import uuid
from pathlib import Path

from fastapi import UploadFile

from src.service.errors import ServiceError
from src.settings import settings

_SIGNATURES = {b"\x89PNG\r\n\x1a\n": ".png", b"\xff\xd8\xff": ".jpg"}


def upload_dir() -> Path:
    path = Path(settings.upload_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_photo(upload: UploadFile) -> str:
    data = upload.file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise ServiceError(413, f"A foto deve ter no máximo {settings.max_upload_bytes // (1024 * 1024)} MB.")
    extension = next((ext for sig, ext in _SIGNATURES.items() if data.startswith(sig)), None)
    if extension is None:
        raise ServiceError(400, "A foto deve ser uma imagem JPG ou PNG.")
    name = f"{uuid.uuid4().hex}{extension}"
    (upload_dir() / name).write_bytes(data)
    return name


def delete_photo(name: str) -> None:
    if name:
        (upload_dir() / Path(name).name).unlink(missing_ok=True)

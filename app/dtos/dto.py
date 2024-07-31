from uuid import UUID

from pydantic import BaseModel


class FileIn(BaseModel):
    """Объект с метаданными файла"""
    uid: str | None = None
    filename: str | None = None
    extension: str | None = None
    size: int | None = None
    local_path: str | None = None
    cloud_path: str | None = None

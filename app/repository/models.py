import uuid
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column
)

from app.repository.session import engine


class Base(DeclarativeBase):
    """Базовый класс таблиц"""
    ...


class Files(Base):
    """Таблица для хранения метаданных файлов"""
    __tablename__ = 'files'

    id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    uid: Mapped[uuid.UUID] = mapped_column(index=True, unique=True)
    filename: Mapped[str] = mapped_column(nullable=True)
    extension: Mapped[str] = mapped_column(nullable=True)
    size: Mapped[int] = mapped_column(nullable=True)
    local_path: Mapped[str]
    cloud_path: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


async def create_table() -> None:
    """Функция создания таблицы"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

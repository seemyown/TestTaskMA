import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select, delete, Result, Select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import ReturningDelete

from app.dtos.dto import FileIn
from app.repository.exceptions import (
    PathNotFoundDB, FileAlreadyExistsDB, FileNotFoundDB
)
from app.repository.models import Files


class FileRepository:
    """Репозиторий для работы с файлами в БД"""
    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория

        Аргументы:
            - session (AsyncSession): асинхронная сессия
        """
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)

    async def save_file_data(self, file: FileIn) -> None:
        """
        Метод для сохранения метаинформации в БД

        Аргументы:
            - file (FileIn): Объект с данными файла

        Ошибки:
            - FileAlreadyExistsDB: Файл с таким UID уже существует
        """
        self.logger.info(f"Сохранение метаданных файла: {file.uid}")
        file_obj: Files = Files(
            **file.model_dump()
        )
        try:
            self.session.add(file_obj)
            await self.session.flush()
            self.logger.info(f"Файл сохранен с ID: {file_obj.id}")
            await self.session.commit()
        except IntegrityError as e:
            self.logger.error(
                f"Ошибка добавления файла {file_obj.id}. "
                f"Детали: {e.orig.args}"
            )
            raise FileAlreadyExistsDB(uid=file_obj.uid)

    async def get_file_local_path(self, uid: UUID) -> str:
        """
        Метод для получения локального пути файла.

        Аргументы:
            - uid (UUID): уникальный идентификатор файла

        Возвращает:
            - str: путь для файла для апи

        Ошибки:
            - LocalPathNotFound: путь не найден
        """
        self.logger.info(f"Получение локального пути файла: {uid}")
        statement: Select[tuple[Any]] = select(
            Files.local_path
        ).filter_by(uid=uid)
        result: Result[tuple[Any]] = await self.session.execute(statement)
        local_file_path: str | None = result.scalar_one_or_none()
        if local_file_path is not None:
            self.logger.info(f"Файл {uid=} получен локальный путь: {local_file_path}")
            return local_file_path
        else:
            self.logger.error(f"Файл {uid=} не найден")
            raise PathNotFoundDB(uid=uid)

    async def get_file_cloud_path(self, uid: UUID) -> str:
        """
        Метод для получения облачного пути файла.

        Аргументы:
            - uid (UUID): уникальный идентификатор файла

        Возвращает:
            - str: путь для файла для апи

        Ошибки:
            - LocalPathNotFound: путь не найден
        """
        self.logger.info(f"Получение облачного пути файла: {uid}")
        statement: Select[tuple[Any]] = select(
            Files.cloud_path
        ).filter_by(uid=uid)
        result: Result[tuple[Any]] = await self.session.execute(statement)
        cloud_file_path: str | None = result.scalar_one_or_none()
        if cloud_file_path is not None:
            self.logger.info(f"Файл {uid=} получен облачный путь: {cloud_file_path}")
            return cloud_file_path
        else:
            self.logger.error(f"Файл {uid=} не найден")
            raise PathNotFoundDB(uid=uid)
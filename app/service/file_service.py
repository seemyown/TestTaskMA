import logging
import os
import uuid
from io import BytesIO
from typing import Union
from uuid import UUID

import PyPDF2
import magic
import docx
from PIL import Image
from fastapi import UploadFile

from app.dtos.dto import FileIn
from app.repository.exceptions import FileAlreadyExistsDB, PathNotFoundDB
from app.repository.repository import FileRepository
from app.service.exceptions import FileNotFoundLocal, FileNotFound
from app.settings import settings


class FileService:
    """Сервис для работы с файлами"""
    def __init__(self, file_repository: FileRepository):
        """Инициализация"""
        self.file_repository = file_repository
        self.logger = logging.getLogger(self.__class__.__name__)

    async def create_new_file(self, file: UploadFile) -> dict[
        str, Union[str, UUID, bytes]
    ]:
        """
        Метод для создания нового файла и объекта

        Аргументы:
            - file(UploadFile): Объект файла

        Возвращает:
            - dict[str, Union[str, UUID, bytes]]:
                Словарь с названием файла его UID и байт строку

        Логика:
            - Получаем всю необходимую информацию
            - Создаем объект для передачи репозиторию
        """
        self.logger.info("Сохранение нового файла")
        file_uid: UUID = uuid.uuid4()
        extension_dot_index = file.filename.rfind(".")
        filename = file.filename[:extension_dot_index]
        file_extension = file.filename[extension_dot_index + 1:]
        file_obj = FileIn(
            uid=str(file_uid),
            filename=filename,
            extension=file_extension,
            size=file.size,
            local_path=f"./static/{file_uid}.{file_extension}",
            cloud_path=f"{settings.S3_PUBLIC_URL}/{file_uid}.{file_extension}"
        )
        return await self.__save(file_obj, file.file.read())

    async def create_new_file_chunk(self, file: bytes) -> dict[
        str, Union[str, UUID, bytes]
    ]:
        """
        Метод для создания нового файла из байт строки

        Аргументы:
            - file(UploadFile): Объект файла

        Возвращает:
            - dict[str, Union[str, UUID, bytes]]:
                Словарь с названием файла его UID и байт строку

        Логика:
            - Получаем MIME-формат
            - Передаем байт строку в функцию для получения меты
            - Формируем объект для передачи репозиторию
        """
        byte_io = BytesIO(file)
        file_type = magic.from_buffer(byte_io.read(), mime=True)
        file_uid = uuid.uuid4()
        meta: dict[str, str] = await self.__extract_meta(
            byte_io, file_type
        )
        file_obj = FileIn.model_validate(meta)
        file_obj.uid = str(file_uid)
        file_obj.size = byte_io.getbuffer().nbytes
        file_obj.local_path = f"./static/{file_uid}.{file_obj.extension}"
        file_obj.cloud_path = (
            f"{settings.S3_PUBLIC_URL}/{file_uid}.{file_obj.extension}"
        )
        return await self.__save(file_obj, file)

    async def __save(self, file_obj: FileIn, binary_file: bytes) -> dict[
        str, Union[str, UUID, bytes]
    ]:
        """
        Метод сохранения данных о файле в БД и файла в локальное хранилище

        Аргументы:
            - file_obj(FileIn): объект с данными файла
            - binary_file(bytes): бинарная строка

        Возвращает:
            - dict[str, Union[str, UUID, bytes]]:
                Словарь с названием файла его UID и байт строку

        Логика:
            - Запускаем цикл и пробуем сохранить данные в БД.
            - Если файл с таким UID существует меняем его и пробуем снова.
            - Сохраняем файл локально.
        """
        while True:
            try:
                self.logger.info("Попытка сохранить информацию о файле в БД")
                await self.file_repository.save_file_data(file_obj)
                self.logger.info(f"Файл успешно сохранен с UID: {file_obj.uid}")
                break
            except FileAlreadyExistsDB as e:
                self.logger.warning(f"{e} Замена")
            file_obj.uid = uuid.uuid4()
            file_obj.local_path = (
                f"./static/{file_obj.uid}.{file_obj.extension}"
            )
            file_obj.cloud_path = (
                f"{settings.S3_PUBLIC_URL}/{file_obj.uid}.{file_obj.extension}"
            )

        with open(f"{file_obj.local_path}", "wb") as f:
            f.write(binary_file)
        self.logger.info(
            f"Файл успешно сохранен с названием:"
            f" {file_obj.uid}.{file_obj.extension}."
        )
        return {
            "file_uid": file_obj.uid,
            "file_key": f"{file_obj.uid}.{file_obj.extension}",
            "binary_file": binary_file,
        }

    @staticmethod
    async def __extract_meta(file: BytesIO, mime_type: str) -> dict[str, str]:
        """
        Метод получения меты

        Аргументы:
            - file(ByteIO): байт строка
            - mime_type(str): тип файла

        Возвращает:
            - dict[str, str]: Словарь с названием, расширением

        Логика:
            - Проверяем MIME и выбираем подходящую библиотеку.
            - Получаем нужные данные

        PS: Для некоторых типов не смог найти подходящую библиотеку
        """
        if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(file)
            props = doc.core_properties
            return {
                "filename": props.title,
                "extension": "docs",
            }
        elif mime_type.startswith("audio"):
            return {
                "filename": "unknown",
                "extension": mime_type[mime_type.rfind("/") + 1:],
            }
        elif mime_type.startswith("video"):
            return {
                "filename": "unknown",
                "extension": mime_type[mime_type.rfind("/") + 1:],
            }
        elif mime_type.startswith("image"):
            image = Image.open(file)
            return {
                "filename": image.filename,
                "extension": image.format.lower(),
            }
        elif mime_type == "application/pdf":
            pdf_file = PyPDF2.PdfReader(file)
            info = pdf_file.metadata
            return {
                "filename": info.title,
                "extension": "pdf",
            }

    async def get_file_by_uid_local(self, uid: UUID) -> dict[str, str]:
        """
        Метод для получения файла локально по UID

        Аргументы:
            - uid(UUID): UID файла

        Возвращает:
            - dict[str, str]: название и путь

        Логика:
            - Получаем локальный путь из БД
            - Проверяем существует ли он, если да, возвращаем название и путь

        Ошибки:
            - FileNotFoundLocal: Файла нет локально
        """
        self.logger.info(f"Получение пути сохранения файла с {uid=}")
        try:
            path = await self.file_repository.get_file_local_path(uid)
        except PathNotFoundDB as e:
            self.logger.error(e)
            raise FileNotFoundLocal(uid)

        if os.path.exists(path):
            self.logger.info(f"Файл найден по пути: {path}")
            filename = path[path.rfind("/") + 1:]
            return {
                "path": path,
                "filename": filename
            }
        else:
            self.logger.info(f"Файл не найден по пути: {path}")
            raise FileNotFoundLocal(uid, path)

    async def get_file_by_uid_cloud(self, uid: UUID) -> str:
        """
        Метод получения ссылки на файл в облаке

        Аргументы:
            - uid(UUID): UID файла

        Возвращает:
            - str: ссылку на файл

        Ошибки:
            - FileNotFound: файла нет
        """
        self.logger.info(f"Получение ссылки для файла с {uid=}")
        try:
            link = await self.file_repository.get_file_cloud_path(uid)
            return link
        except PathNotFoundDB as e:
            self.logger.error(e)
            raise FileNotFound(uid)

import logging
from typing import Union
from uuid import UUID

from fastapi import (
    APIRouter, BackgroundTasks, Depends, UploadFile, HTTPException
)
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from starlette.requests import Request

from app.api.v1.dependencies import ServiceTools, get_tools
from app.service.exceptions import FileNotFound, FileNotFoundLocal
from app.settings import settings

router = APIRouter(
    prefix="/files"
)
logger = logging.getLogger("FileRouter")


@router.post(
    "/", status_code=201,
    summary="Добавление нового файла"
)
async def create_file(
        file: UploadFile,
        bg_tasks: BackgroundTasks,
        tools: ServiceTools = Depends(get_tools)
):
    """
    Функция обработчик запроса на добавление нового файла

    Аргументы:
        *file(UploadFile)*: Файл для загрузки;
        *bg_tasks(BackgroundTasks)*: Класс для фоновых задач;
        *tools(ServiceTools)*: Класс с сервисами;

    Логика:
        - Передаем файл сервису
        - Получаем от него UID и бинарную строку
        - Добавляем асинхронную задачу загрузки в S3

    Возвращает:
        - JSONResponse(201): Файл успешно сохранен.

    Ошибки:
        - HTTPException(500): Баг
    """
    try:
        result: dict[str, Union[str, UUID, bytes]] = (
            await tools.file_service.create_new_file(file)
        )
        await tools.cloud_service.session()
        bg_tasks.add_task(
            tools.cloud_service.save_file,
            binary_file=result["binary_file"],
            key=result["file_key"],
            mock=settings.DEBUG
        )
        return JSONResponse(
            {
                "success": True,
                "fileUID": result["file_uid"]
            },
            status_code=201
        )
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post(
    "/stream", status_code=201,
    summary="Потоковое добавление нового файла"
)
async def stream_file(
        request: Request,
        bg_tasks: BackgroundTasks,
        tools: ServiceTools = Depends(get_tools)
):
    """
        Функция обработчик запроса на добавление нового файла

        Аргументы:
            *request(Request)*: Объект запроса;
            *bg_tasks(BackgroundTasks)*: Класс для фоновых задач;
            *tools(ServiceTools)*: Класс с сервисами;

        Логика:
            - итерируемся по стриму и собираем бинарную строку
            - Передаем стоку сервису
            - Получаем от него UID и бинарную строку
            - Добавляем асинхронную задачу загрузки в S3

        Возвращает:
            - JSONResponse(201): Файл успешно сохранен.

        Ошибки:
            - HTTPException(500): Баг
        """
    file = b""
    async for chunk in request.stream():
        file += chunk

    try:
        result = await tools.file_service.create_new_file_chunk(file)
        await tools.cloud_service.session()
        bg_tasks.add_task(
            tools.cloud_service.save_file,
            binary_file=result["binary_file"],
            key=result["file_key"],
            mock=settings.DEBUG
        )
        return JSONResponse(
            {
                "success": True,
                "fileUID": result["file_uid"]
            },
            status_code=201
        )
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/{uid}", status_code=308,
    summary="Получение и загрузка(опционально) по UID"
)
async def get_file(
        uid: UUID,
        download: bool = False,
        tools: ServiceTools = Depends(get_tools),
):
    """
    Функция обработчик запроса на получение файла.

    Аргументы:
        *uid(UUID)*: Уникальный UID файла;
        *download(bool)*: Флаг нужно ли загружать файл;
        *tools(ServiceTools)*: Объект с сервисами;

    Логика:
        - Получаем путь до файла и его название

    Возвращает:
        - FileResponse(200): файл
        - RedirectResponse(308): из облака

    Ошибки:
        HTTPException(500, 404): Баг, Файл не найден локально илл в облаке

    PS. В обработку исключения, что файл не найден добавлена
    логика получения файла из облака.
    """
    try:
        path: dict[str, str] = await tools.file_service.get_file_by_uid_local(
            uid
        )
        logger.info("Файл найден")
        # if download
        return FileResponse(
            path["path"],
            filename=path["filename"] if download else None,
            media_type="application/octet-stream" if download else None,
        )
    except FileNotFoundLocal:
        logger.warning(
            "Файл не найден локально. Попытка получить копию из облака"
        )
        try:
            link = await tools.file_service.get_file_by_uid_cloud(
                uid
            )
            return RedirectResponse(
                link,
                status_code=308,
                headers={
                    "content_type": "application/octet-stream"
                } if download else None
            )
        except FileNotFound as e:
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

import asyncio
import logging


logger = logging.getLogger("Mocks")


async def upload_to_cloud_mock(*args, **kwargs):
    logger.info(f"Загрузка файла с uid={kwargs.get("key", None)}")
    await asyncio.sleep(3)
    logger.info(f"Загрузка файла с uid={kwargs.get("key", None)} завершена")


async def s3_session_mock(*args, **kwargs):
    logger.info("Создание сессии для S3")
    await asyncio.sleep(2)
    logger.info("Сессия создана")

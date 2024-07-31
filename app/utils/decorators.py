import logging
from functools import wraps


def mock(mock_func):
    """
    Декоратор для вызова мок функции

    Аргумент:
        - mock_func - мок-функция

    Логика:
        - При вызове функции, если передан аргумент mock=True,
            то вызывается мок-функция
    """
    logger = logging.getLogger("Mocker")

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if kwargs.get("mock", False):
                logger.info(f"Mocking {func.__name__}")
                try:
                    return await mock_func(*args, **kwargs)
                except Exception as e:
                    logger.error(e)
                    raise
            else:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(e)
                    raise
        return wrapper
    return decorator

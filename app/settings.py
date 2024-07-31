import os
from typing import Union

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str  # Название сервиса
    APP_VERSION: str  # Версия сервиса
    APP_DESCRIPTION: str  # Описание сервиса
    ALLOWED_ORIGINS: str  # Откуда могут поступать запросы
    DEBUG: bool  # Флаг дебаг режима
    DB_USER: str  # Логин БД
    DB_PASSWORD: str  # Пароль БД
    DB_HOST: str  # Хост БД
    DB_PORT: int  # Порт БД
    DB_NAME: str  # Название БД
    S3_KEY_ID: str | None = None  # ID ключа от S3
    S3_ACCESS_KEY: str | None = None  # Ключ доступа от S3
    S3_REGION_NAME: str | None = None  # Регион S3
    S3_BUCKET: str | None = None  # Название бакета
    S3_URL: str | None = None  # URL хранилища
    S3_PUBLIC_URL: str | None = "https://test.s3.ru/"  # URL публичного доступа

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def app_config(self) -> dict[str, Union[bool, str]]:
        """Словарь с информацией о приложении"""
        return {
            "title": self.APP_NAME,
            "version": self.APP_VERSION,
            "description": self.APP_DESCRIPTION,
            "debug": self.DEBUG,
        }

    @property
    def cors_middleware_config(self) -> dict[str, Union[bool, str, list]]:
        """Словарь с настройками CORSMiddleware"""
        return {
            "allow_origins": self.ALLOWED_ORIGINS.split(",")
            if "*" not in self.ALLOWED_ORIGINS else self.ALLOWED_ORIGINS,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
            "allow_credentials": True,
        }

    @property
    def async_dcn_string(self) -> str:
        """DSN строка для создания асинхронного движка"""
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @staticmethod
    def setup_logging() -> None:
        """Настройка логирования"""
        import yaml
        import logging.config
        with open("logging.yaml", "r") as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)

    @staticmethod
    def setup_architecture():
        """Настройка архитектуры приложения"""
        current_dir = os.getcwd()
        if not os.path.exists(f"{current_dir}/logs"):
            print("Создание папок для логов")
            os.makedirs(f"{current_dir}/logs/debug/")
            os.makedirs(f"{current_dir}/logs/info/")
            os.makedirs(f"{current_dir}/logs/error/")
            os.makedirs(f"{current_dir}/logs/warning/")
        else:
            print("Лог папки созданы")

        if not os.path.exists(f"{current_dir}/static"):
            print("Создание папки для хранения файлов")
        else:
            print("Папка для файлов создана")


settings = Settings()

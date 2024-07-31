from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from app.api.v1.files.router import router
from app.repository.models import create_table
from app.settings import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Функция инициализатор компонентов приложения"""
    await create_table()
    settings.setup_architecture()
    settings.setup_logging()
    yield


app = FastAPI(
    **settings.app_config,
    lifespan=lifespan
)
# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    **settings.cors_middleware_config
)

app.mount("/static", StaticFiles(directory="./static"), name="static")
app.include_router(router)


@app.get("/")
async def root():
    """Редирект на документацию"""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    """Проверка состояния приложения"""
    return JSONResponse({"status": "ok"}, status_code=200)

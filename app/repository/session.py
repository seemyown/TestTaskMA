from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.settings import settings

# Асинхронный движок для получения сессии
engine = create_async_engine(
    settings.async_dcn_string,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

# фабрика для создания сессии
async_session = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)


async def get_session():
    """
    Функция-генератор для получения сессии

    Возвращает:
        session(AsyncSession)
    """
    async with async_session() as session:
        yield session

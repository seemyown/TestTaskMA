import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='function')
async def client(event_loop):
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url='http://test',
    ) as client:
        yield client

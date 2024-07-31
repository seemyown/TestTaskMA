import httpx
from httpx ASGITransport
import pytest

from app.main import app


@pytest.mark.asyncio
async def test_upload_doc():
    async with httpx.AsyncClient(
        app=ASGITransport(app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/files/", files={"file": open("./tests/test_files/sample2.doc", "rb")}
        )
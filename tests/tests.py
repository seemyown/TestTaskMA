import aiofiles
import pytest

# Список загруженных файлов
UPLOADED_FILES_UID: list[str] = []


@pytest.mark.asyncio
async def test_upload_docx(client):
    """Тест отправки docx"""
    response = await client.post(
        "/files/", files={"file": open("./tests/test_files/sample2.docx", "rb")}
    )
    assert response.status_code == 201
    response = response.json()
    assert response["success"] is True
    UPLOADED_FILES_UID.append(response["fileUID"])


@pytest.mark.asyncio
async def test_upload_pdf(client):
    """Тест отправки PDF"""
    response = await client.post(
        "/files/", files={"file": open("./tests/test_files/sample3.pdf", "rb")}
    )
    assert response.status_code == 201
    response = response.json()
    assert response["success"] is True
    UPLOADED_FILES_UID.append(response["fileUID"])


@pytest.mark.asyncio
async def test_upload_mkv(client):
    """Тест отправки MKV"""
    response = await client.post(
        "/files/", files={"file": open("./tests/test_files/sample_960x540.mkv", "rb")}
    )
    assert response.status_code == 201
    response = response.json()
    assert response["success"] is True
    UPLOADED_FILES_UID.append(response["fileUID"])


@pytest.mark.asyncio
async def test_upload_png(client):
    """Тест отправки PNG"""
    response = await client.post(
        "/files/", files={"file": open("./tests/test_files/sample_1280×853.png", "rb")}
    )
    assert response.status_code == 201
    response = response.json()
    assert response["success"] is True
    UPLOADED_FILES_UID.append(response["fileUID"])


@pytest.mark.asyncio
async def test_upload_jpg(client):
    """Тест отправки JPG"""
    response = await client.post(
        "/files/", files={"file": open("./tests/test_files/sample_1920×1280.jpg", "rb")}
    )
    assert response.status_code == 201
    response = response.json()
    assert response["success"] is True
    UPLOADED_FILES_UID.append(response["fileUID"])


@pytest.mark.asyncio
async def test_upload_stream_docx(client):
    """Тест отправки потоком DOCX"""
    async with aiofiles.open("./tests/test_files/sample2.docx", mode="rb") as f:
        content = await f.read()
        response = await client.post(
            "/files/stream", content=content
        )
    assert response.status_code == 201
    response = response.json()
    assert response["success"] is True
    UPLOADED_FILES_UID.append(response["fileUID"])


@pytest.mark.asyncio
async def test_upload_stream_pdf(client):
    """Тест отправки потоком PDF"""
    async with aiofiles.open("./tests/test_files/sample3.pdf", mode="rb") as f:
        content = await f.read()
        response = await client.post(
            "/files/stream", content=content
        )
    assert response.status_code == 201
    response = response.json()
    assert response["success"] is True
    UPLOADED_FILES_UID.append(response["fileUID"])


@pytest.mark.asyncio
async def test_upload_stream_mkv(client):
    """Тест отправки потоком MKV"""
    async with aiofiles.open("./tests/test_files/sample_960x540.mkv", "rb") as f:
        content = await f.read()
        response = await client.post(
            "files/stream", content=content
        )
    assert response.status_code == 201
    response = response.json()
    assert response["success"] is True
    UPLOADED_FILES_UID.append(response["fileUID"])


@pytest.mark.asyncio
async def test_upload_stream_png(client):
    """Тест отправки потоком PNG"""
    async with aiofiles.open("./tests/test_files/sample_1280×853.png", "rb") as f:
        content = await f.read()
        response = await client.post(
            "/files/stream", content=content
        )
    assert response.status_code == 201
    response = response.json()
    assert response["success"] is True
    UPLOADED_FILES_UID.append(response["fileUID"])


@pytest.mark.asyncio
async def test_upload_stream_jpg(client):
    """Тест отправки потоком JPG"""
    async with aiofiles.open("./tests/test_files/sample_1920×1280.jpg", "rb") as f:
        content = await f.read()
        response = await client.post(
            "/files/stream", content=content
        )
    assert response.status_code == 201
    response = response.json()
    assert response["success"] is True
    UPLOADED_FILES_UID.append(response["fileUID"])


@pytest.mark.asyncio
async def test_upload_get_files(client):
    """Тест наличия всех файлов"""
    for uid in UPLOADED_FILES_UID:
        response = await client.get(
            f"/files/{uid}"
        )
        assert response.status_code == 200

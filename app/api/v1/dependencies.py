from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.repository import FileRepository
from app.repository.session import get_session
from app.service.cloud_service import CloudService
from app.service.file_service import FileService


class ServiceTools:
    def __init__(
            self, file_service: FileService,
            cloud_service: CloudService
    ):
        self.file_service = file_service
        self.cloud_service = cloud_service


async def get_tools(session: AsyncSession = Depends(get_session)):
    return ServiceTools(
        file_service=FileService(FileRepository(session)),
        cloud_service=CloudService(),
    )

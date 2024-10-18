# FastApi
from fastapi import (
    Depends, APIRouter, Response, status, Form, UploadFile, File
)

# Thirt-Party
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
import aiofiles

# Python
from typing import Annotated
from datetime import datetime
import os

# Local
from src.db.models import Doctors, Patients, PatientTests
from src.settings.base import VOLUME, logger
from .depends import get_async_session
from .schemas.response import ErrorSchema, ResponseSchema


class Registration:
    """View for registration Doctors and Patients."""

    def __init__(self) -> None:
        self.path = "/reg"
        self.router = APIRouter(
            prefix="/api/v1", tags=["Registration Users"]
        )


class ForDoctors:

    def __init__(self) -> None:
        self.path = "/tests"
        self.router = APIRouter(
            prefix="/api/v1", tags=["tests"]
        )
        self.router.add_api_route(
            path=self.path, endpoint=self.add_tests, 
            methods=["POST"], responses={
                200: {"model": ResponseSchema},
                500: {"model": ErrorSchema}
            }
        )

    async def add_tests(
        self, response: Response,
        patient_id: Annotated[int, Form(ge=0)],
        doc: UploadFile = None, 
        session: AsyncSession = Depends(get_async_session)
    ):
        try:
            now = datetime.now().strftime("%Y-%m-%d")
            doc_path = f"docs/{now}_{doc.filename}"
            file_path = os.path.join(VOLUME, doc_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            async with aiofiles.open(file_path, 'wb') as f:
                while content := await doc.read(1024):
                    await f.write(content)
        except Exception as e:
            error = f"Something went wrong: {e.__cause__}"
            logger.error(error)
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorSchema(error=error)
        query = insert(PatientTests).values(
            patient_id=patient_id, file_path=file_path
        )
        try:
            await session.execute(query)
            await session.commit()
            return ResponseSchema(response="Test added successfully!")
        except Exception as e:
            error = f"Something went wrong: {e.__cause__}"
            logger.error(error)
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorSchema(error=error)

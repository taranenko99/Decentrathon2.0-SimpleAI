# FastApi
from fastapi import (
    Depends, APIRouter, Response, status, Form, UploadFile, HTTPException
)

# Thirt-Party
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from psycopg.errors import IntegrityError, UniqueViolation
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
from .schemas.users import \
    CreateDoctor, CreatePatient, ViewAllDoctors, ViewAllPatients


class Registration:
    """View for registration Doctors and Patients."""

    def __init__(self) -> None:
        self.router = APIRouter(
            prefix="/reg", tags=["Registration Users"]
        )
        self.router.add_api_route(
            path="/doctor", endpoint=self.create_doctor, 
            methods=["POST"], responses={
                200: {"model": ResponseSchema},
                400: {"model": ErrorSchema}
            }
        )
        self.router.add_api_route(
            path="/patient", endpoint=self.create_patient, 
            methods=["POST"], responses={
                200: {"model": ResponseSchema},
                400: {"model": ErrorSchema}
            }
        )

    @staticmethod
    async def create_doctor(
        obj: CreateDoctor, response: Response,
        session: AsyncSession = Depends(get_async_session)
    ):
        stmt = insert(Doctors).values(
            telegram_id=obj.telegram_id, 
            individual_number=obj.individual_number
        )
        try:
            await session.execute(statement=stmt)
            await session.commit()
            return ResponseSchema(response="Doctor created!")
        except Exception as e:
            error = f"Нарушена уникальность: {e.__cause__}"
            logger.error(error)
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorSchema(error=error)

    @staticmethod
    async def create_patient(
        obj: CreatePatient, response: Response,
        session: AsyncSession = Depends(get_async_session)
    ):
        stmt = insert(Patients).values(
            telegram_id=obj.telegram_id,
            individual_number=obj.individual_number,
            doctor_id=obj.doctor_id
        )
        try:
            await session.execute(statement=stmt)
            await session.commit()
            return ResponseSchema(response="Patient created!")
        except Exception as e:
            error = f"Нарушена уникальность: {e.__cause__}"

            logger.error(error)
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorSchema(error=error)


class ViewUsers:

    def __init__(self) -> None:
        self.router = APIRouter(
            prefix="/view", tags=["View Users"]
        )
        self.router.add_api_route(
            path="/doctor", endpoint=self.view_doctors, 
            methods=["GET"], responses={
                200: {"model": ViewAllDoctors},
                404: {"model": None}
            }
        )
        self.router.add_api_route(
            path="/patient", endpoint=self.view_patients, 
            methods=["GET"], responses={
                200: {"model": ViewAllPatients},
                404: {"model": None}
            }
        )

    @staticmethod
    async def view_doctors(
        limit: int = 50, page_number: int = 0,
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Doctors).limit(
            limit=limit
        ).offset(offset=page_number)
        temp = await session.execute(query)
        data = temp.scalars().all()
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="there is no data"
            )
        obj = []
        for item in data:
            doctor = CreateDoctor(
                id=item.id,
                telegram_id=item.telegram_id, 
                individual_number=item.individual_number
            )
            obj.append(doctor)
        return ViewAllDoctors(response=obj)
    
    @staticmethod
    async def view_patients(
        limit: int = 50, page_number: int = 0,
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Patients).limit(
            limit=limit
        ).offset(offset=page_number)
        temp = await session.execute(query)
        data = temp.scalars().all()
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="there is no data"
            )
        obj = []
        for item in data:
            patient = CreatePatient(
                id=item.id,
                telegram_id=item.telegram_id, 
                individual_number=item.individual_number,
                doctor_id=item.doctor_id
            )
            obj.append(patient)
        return ViewAllPatients(response=obj)
    

class ForDoctors:

    def __init__(self) -> None:
        self.path = "/tests"
        self.router = APIRouter(
            prefix="/api/v1", tags=["Tests"]
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

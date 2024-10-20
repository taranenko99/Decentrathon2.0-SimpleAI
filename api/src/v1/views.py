# FastApi
from fastapi import (
    Depends, APIRouter, Response, status, Form, UploadFile, HTTPException, File
)

# Thirt-Party
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update
import aiofiles
from langchain_community.chat_message_histories import RedisChatMessageHistory

# Python
from typing import Annotated
from datetime import datetime
import os

# Local
from src.llm.generation import qa, classify_patient_answer, summarize_last_chat_history
from src.db.models import Doctors, Patients, PatientTests
from src.settings.base import VOLUME, logger, REDIS_URL
from src.llm.get_text_from_image import get_text_from_table
from .depends import get_async_session
from .schemas.response import ErrorSchema, ResponseSchema, ResponseChat
from .schemas.users import (
    CreateDoctor, CreatePatient, ViewAllDoctors, ViewAllPatients, 
    ViewTest, RequestChat, UpdatePatient, ViewDoctor
)


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
        self.router.add_api_route(
            path="/patient", endpoint=self.update_patient,
            methods=["PATCH"], responses={
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

    @staticmethod
    async def update_patient(
        obj: UpdatePatient, response: Response,
        session: AsyncSession = Depends(get_async_session)
    ):
        stmt = update(Patients).where(
            Patients.individual_number==obj.individual_number
        ).values(telegram_id=obj.telegram_id)
        try:
            await session.execute(statement=stmt)
            await session.commit()
            return ResponseSchema(response="Patient updated!")
        except Exception as e:
            error = f"Something went wrong: {e.__cause__}"
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
            path="/doctor/{telegram_id}", endpoint=self.view_doctor, 
            methods=["GET"], responses={
                200: {"model": ViewDoctor},
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
    async def view_doctor(
        telegram_id: int, 
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Doctors).where(Doctors.telegram_id==telegram_id)
        temp = await session.execute(query)
        doctor = temp.scalars().one_or_none()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="there is no data"
            )
        patients = []
        for p in doctor.patients:
            obj = CreatePatient(
                id=p.id, telegram_id=p.telegram_id, 
                individual_number=p.individual_number, 
                doctor_id=p.doctor_id
            )
            patients.append(obj)
        schema = ViewDoctor(
            id=doctor.id, telegram_id=doctor.telegram_id, 
            individual_number=doctor.individual_number, patients=patients
        )
        return schema
    
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
    

class CheckUser:
    def __init__(self) -> None:
        self.router = APIRouter(
            prefix="/check", tags=["Check User"]
        )
        self.router.add_api_route(
            path="/doctor", endpoint=self.check_doctor, 
            methods=["GET"], responses={
                200: {"model": CreateDoctor},
                404: {"model": None}
            }
        )
        self.router.add_api_route(
            path="/patient", endpoint=self.check_patient, 
            methods=["GET"], responses={
                200: {"model": CreatePatient},
                404: {"model": None}
            }
        )

    @staticmethod
    async def check_doctor(
        telegram_id: int, 
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Doctors).where(Doctors.telegram_id==telegram_id)
        temp = await session.execute(query)
        obj = temp.scalars().one_or_none()
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="there is no data"
            )
        schema = CreateDoctor(
            id=obj.id, telegram_id=obj.telegram_id, 
            individual_number=obj.individual_number
        )
        return schema
    
    @staticmethod
    async def check_patient(
        telegram_id: int,
        session: AsyncSession = Depends(get_async_session)
    ):
        query = select(Patients).where(Patients.telegram_id==telegram_id)
        temp = await session.execute(query)
        obj = temp.scalars().one_or_none()
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="there is no data"
            )
        help_schema = CreateDoctor(
            id=obj.doctor.id, telegram_id=obj.doctor.telegram_id, 
            individual_number=obj.doctor.individual_number
        )
        schema = CreatePatient(
            id=obj.id, telegram_id=obj.telegram_id, 
            individual_number=obj.individual_number,
            doctor_id=obj.doctor_id, doctor=help_schema
        )
        return schema


class ForDoctors:

    def __init__(self) -> None:
        self.path = "/tests"
        self.router = APIRouter(
            prefix="/api/v1", tags=["Tests"]
        )
        self.router.add_api_route(
            path=self.path, endpoint=self.add_tests, 
            methods=["POST"], responses={
                200: {"model": ViewTest},
                500: {"model": ErrorSchema}
            }
        )

    @staticmethod
    async def add_tests(
        response: Response,
        patient_id: Annotated[int, Form(ge=0)],
        doc: UploadFile = None, 
        session: AsyncSession = Depends(get_async_session)
    ):
        try:
            now = datetime.now().strftime("%Y-%m-%d")
            data = {}
            doc_path = os.path.join("docs", f"{now}_{doc.filename}")
            file_path = os.path.join(VOLUME, doc_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            async with aiofiles.open(file_path, 'wb') as f:
                while content := await doc.read(1024):
                    await f.write(content)
            temp_data = get_text_from_table(image_path=file_path)
            data.update({f"{now}_{doc.filename}": temp_data})

        except Exception as e:
            error = f"Something went wrong: {e.__cause__}"
            logger.error(error)
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorSchema(error=error)
        query = insert(PatientTests).values(
            patient_id=patient_id, file_path=file_path, data=data
        ).returning(PatientTests)
        try:
            result = await session.execute(query)
            temp = result.scalars().one_or_none()
            await session.commit()
            schema = ViewTest(
                id=temp.id, patient_id=temp.patient_id, data=temp.data
            )
            return schema
        except Exception as e:
            error = f"Something went wrong: {e.__cause__}"
            logger.error(error)
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorSchema(error=error)


class Chat:

    def __init__(self) -> None:
        self.path = "/chat"
        self.router = APIRouter(
            prefix="/api/v1", tags=["Chat"]
        )
        self.router.add_api_route(
            path=self.path, endpoint=self.chat, 
            methods=["POST"], responses={
                200: {"model": ResponseChat},
                400: {"model": None}
            }
        )

    @staticmethod
    async def chat(request: RequestChat):
        # chat_history_redis = RedisChatMessageHistory(
        #     session_id=request.telegram_id,
        #     url=REDIS_URL, key_prefix='memory'
        # )
        # answer = summarize_last_chat_history(chat_history=chat_history_redis.messages[-5:])
        try:
            status = classify_patient_answer(text=request.message)
            if status == "0":
                return ResponseChat(trigger=2, bot_message="У пациента все норм")
            bot_response = await qa(user_query=request.message, telegram_id=str(request.telegram_id))
            return ResponseChat(trigger=bot_response['trigger'], bot_message=bot_response['bot_message'])

        except Exception as e:
            error = f"Something went wrong: {e.__cause__}"
            logger.error(error)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e
            )

# Aiogram
from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# local
from src.v1.states import Master, Doctor
from src.v1.mixins import MessageMixin, CallbackMixin
from src.v1.utils.master import create_doctor, create_patient


router = Router(name="Doctor Router")


@router.callback_query(Master.select, F.data == "doctor")
class DocType(CallbackMixin):
    async def handle(self):
        self.progress_func()
        await self.answer_to_callback()
        await self.fsm.set_state(state=Master.doc_number)
        await self.make_response(text="Пожалуйста введите свой ИИН")


@router.message(Master.doc_number)
class CreateDoctor(MessageMixin):
    async def handle(self):
        self.progress_func()
        if len(self.event.text) != 12:
            await self.make_response(
                text="ИИН должен содержать 12 цифр!"
            )
            return
        created = await create_doctor(data={
            "individual_number": self.event.text,
            "telegram_id": self.chat_id
        })
        if not created:
            await self.make_response(
                text="Невозможно создать пользователя"
            )
            return
        await self.make_response(
            text="""Регистрация прошла успешно! 
            \nВы можете использовать команды в меню чтобы добавлять пациентов и их анализы!"""
        )


@router.message(Doctor.add_patient)
class JoinPatient(MessageMixin):
    async def handle(self):
        self.progress_func()
        if len(self.event.text) != 12:
            await self.make_response(
                text="ИИН должен содержать 12 цифр!"
            )
            return
        data = await self.fsm.get_data()
        doctor = data.get("user")
        created = await create_patient(data={
            "doctor_id": doctor.id,
            "individual_number": self.event.text
        })
        if not created:
            await self.make_response(
                text="Что-то пошло не так"
            )
            return
        await self.fsm.clear()
        await self.make_response(text="Пациент добавлен!")

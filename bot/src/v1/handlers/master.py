# Aiogram
from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# local
from src.v1.states import Master, Doctor
from src.v1.mixins import MessageMixin, CallbackMixin
from src.v1.utils.master import check_doctor, check_patient, get_patients


router = Router(name="Master Router")


@router.message(CommandStart())
class StartBot(MessageMixin):
    async def handle(self):
        self.progress_func()
        doctor = await check_doctor(telegram_id=self.chat_id)
        if doctor:
            ...
            return
        patient = await check_patient(telegram_id=self.chat_id)
        if patient:
            ...
            return
        await self.fsm.set_state(state=Master.select)
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="Врач", callback_data="doctor"
            ),
            InlineKeyboardButton(
                text="Пациент", callback_data="patient"
            )
        ]])
        await self.make_response(
            text="Пожалуйста выберите роль на клавиатуре ниже",
            markup=markup
        )


@router.message(Command("add"))
class AddPatient(MessageMixin):
    async def handle(self):
        self.progress_func()
        doctor = await check_doctor(telegram_id=self.chat_id)
        if not doctor:
            await self.make_response(text="Вы не доктор")
            return
        await self.fsm.set_state(state=Doctor.add_patient)
        await self.fsm.update_data(data={"user": doctor})
        await self.make_response(text="Введите ИИН пациента")
        

@router.message(Command("upload"))
class UploadTests(MessageMixin):
    async def handle(self):
        self.progress_func()
        doctor = await check_doctor(telegram_id=self.chat_id)
        if not doctor:
            await self.make_response(text="Вы не доктор")
            return
        await self.fsm.set_state(state=Doctor.add_tests)
        patients = await get_patients(telegram_id=self.chat_id)
        await self.fsm.update_data(data={"patients": patients})
        await self.make_response(
            text=""
        )

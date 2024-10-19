# Aiogram
from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# local
from src.v1.states import Master
from src.v1.mixins import MessageMixin, CallbackMixin
from src.v1.utils.master import update_patient


router = Router(name="Patient Router")


@router.callback_query(Master.select, F.data == "patient")
class PatType(CallbackMixin):
    async def handle(self):
        self.progress_func()
        await self.answer_to_callback()
        await self.fsm.set_state(state=Master.pat_number)
        await self.make_response(text="Пожалуйста введите свой ИИН")


@router.message(Master.pat_number)
class UpdatePatient(MessageMixin):
    async def handle(self):
        self.progress_func()
        if len(self.event.text) != 12:
            await self.make_response(
                text="ИИН должен содержать 12 цифр!"
            )
            return
        updated = await update_patient(data={
            "individual_number": self.event.text,
            "telegram_id": self.chat_id
        })
        if not updated:
            await self.make_response(
                text="Чтото пошло не так"
            )
            return
        await self.make_response(
            text="Обновление прошло успешно"
        )

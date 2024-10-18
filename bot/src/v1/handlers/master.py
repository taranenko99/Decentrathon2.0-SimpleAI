# Aiogram
from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# local
from src.v1.states import Master
from src.v1.mixins import MessageMixin, CallbackMixin
from src.v1.utils.master import check_user_in_api, create_user


router = Router(name="Master Router")


@router.message(CommandStart())
class StartBot(MessageMixin):
    async def respond(self):
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

    async def handle(self):
        self.progress_func()
        data = await self.fsm.get_data()
        user = data.get("user", None)
        if not user:
            user = await check_user_in_api(telegram_id=self.chat_id)
            if not user:
                await self.respond()


@router.callback_query(Master.select, F.data == "doctor")
class DocType(CallbackMixin):
    async def handle(self):
        self.progress_func()
        await self.answer_to_callback()
        await self.fsm.set_state(state=Master.doc_number)
        await self.fsm.update_data(data={"user": {
            "type": self.event.data
        }})
        await self.make_response(text="Пожалуйста введите свой ИИН")


@router.callback_query(Master.select, F.data == "patient")
class PatType(CallbackMixin):
    async def handle(self):
        self.progress_func()
        await self.answer_to_callback()
        await self.fsm.set_state(state=Master.pat_number)
        await self.fsm.update_data(data={"user": {
            "type": self.event.data
        }})
        await self.make_response(text="Пожалуйста введите свой ИИН")


@router.message(StateFilter(Master.doc_number, Master.pat_number))
class CreateUser(MessageMixin):
    async def handle(self):
        self.progress_func()
        if len(self.event.text) != 12:
            await self.make_response(
                text="ИИН должен содержать 12 цифр!"
            )
            return
        await self.fsm.update_data(data={"user": {
            "number": self.event.text
        }})
        data = await self.fsm.get_data()
        user = data.get("user")
        created = await create_user(data=user)
        if not created:
            await self.make_response(
                text="Невозможно создать пользователя"
            )
            return
        await self.make_response(
            text="Регистрация прошла успешно"
        )

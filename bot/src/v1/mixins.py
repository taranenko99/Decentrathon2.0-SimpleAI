# Aiogram
from aiogram.handlers import (
    MessageHandler, CallbackQueryHandler, BaseHandler
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
import aiogram.types as tp

# Python
from datetime import datetime
from typing import Any, Union

# Local
from src.settings.base import logger, bot, storage


class BaseMixin(BaseHandler):
    """Base mixin for Messages and CallbackQueries."""

    def __init__(
        self, event: Union[tp.Message, tp.CallbackQuery], **kwargs: Any
    ) -> None:
        if isinstance(event, tp.Message):
            self.chat_id = event.chat.id
        elif isinstance(event, tp.CallbackQuery):
            self.chat_id = event.message.chat.id
        self.storage = storage
        self.key = StorageKey(
            bot_id=bot.id, chat_id=self.chat_id, user_id=self.chat_id
        )
        self.fsm = FSMContext(
            storage=self.storage, key=self.key
        )
        self.event = event

    def progress_func(self):
        """It's for tracing performing handlers."""
        name = self.__class__.__name__
        logger.info("-"*50)
        logger.info(f"{name} In Progress for user {self.chat_id}")
        logger.info("-"*50)

    async def make_response(
        self, text: str, markup: Union[
            tp.ReplyKeyboardRemove, tp.ReplyKeyboardMarkup, 
            tp.InlineKeyboardMarkup, InlineKeyboardBuilder
        ] = tp.ReplyKeyboardRemove()
    ):
        await bot.send_message(
            chat_id=self.chat_id, text=text, reply_markup=markup
        )


class MessageMixin(MessageHandler, BaseMixin):
    """Mixin for Message Handlers."""

    def __init__(self, event: tp.Message, **kwargs: Any) -> None:
        super().__init__(event, **kwargs)


class CallbackMixin(CallbackQueryHandler, BaseMixin):
    """Mixin for Callback Query Handlers."""

    def __init__(self, event: tp.CallbackQuery, **kwargs: Any) -> None:
        super().__init__(event, **kwargs)

    async def answer_to_callback(self):
        try:
            await self.event.answer()
            await self.event.message.delete_reply_markup()
        except:
            pass

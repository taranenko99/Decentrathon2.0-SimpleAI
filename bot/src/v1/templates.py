# Aiogram
from aiogram.types import Message, Chat, User, MessageEntity

# Python
from datetime import datetime, timezone


def get_message_object(chat_id: int, first_name: str) -> Message:
    message = Message(
        message_id=999999,
        date=datetime.now(tz=timezone.utc),
        chat=Chat(
            id=chat_id, type="private",
        ),
        from_user=User(
            id=chat_id, is_bot=False, 
            first_name=first_name
        ),
        text="/report",
        entities=[MessageEntity(
            type="bot_command", offset=0, length=7
        )]
    )
    return message

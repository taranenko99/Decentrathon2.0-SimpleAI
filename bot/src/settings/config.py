# Aiogram
from aiogram.types.bot_command import BotCommand


start = BotCommand(
    command="start",
    description="Запуск бота"
)

MENU = [start]
DESCRIPTION = """SafePregnancyBot разработан для обращения беременных пациентов!
\n Используйте команду /start чтобы сообщить нам о вашем самочувствии.
\n При первом запуске вам необходимо зарегистрироваться."""

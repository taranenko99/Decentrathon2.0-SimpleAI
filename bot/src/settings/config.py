# Aiogram
from aiogram.types.bot_command import BotCommand


start = BotCommand(
    command="start",
    description="Запуск бота"
)
upload = BotCommand(
    command="upload",
    description="Загрузка анализов"
)
add = BotCommand(
    command="join",
    description="Добавить пациента"
)

MENU = [start, upload, add]
DESCRIPTION = """SafePregnancyBot разработан для обращения беременных пациентов!
\n Используйте команду /start чтобы сообщить нам о вашем самочувствии.
\n При первом запуске вам необходимо зарегистрироваться."""

API_HOST = "http://127.0.0.1:8000/"
REG_DOC_URL = f"{API_HOST}reg/doctor"
REG_PAT_URL = f"{API_HOST}reg/patient"
UPLOAD_TESTS = f"{API_HOST}api/v1/tests"
CHAT = f"{API_HOST}api/v1/chat"
CHECK_DOC = f"{API_HOST}check/doctor"
CHECK_PAT = f"{API_HOST}check/patient"
MY_PATIENTS = f"{API_HOST}view/doctor/" # тут надо добавить в конце телеграм id

# Third-Party
from aiohttp import ClientSession

# Local
from src.settings.base import logger, scheduler
from src.settings.config import GET_DOCTORS, MY_PATIENTS
from src.v1.handlers.patient import StartDialog
from .templates import get_message_object


async def get_scheduler():
    scheduler.start()
    await default_jobs()


async def default_jobs():
    scheduler.add_job(
        start, "cron", hour=18, minute=37, 
        replace_existing=True, name="check_date", jobstore="redis",
        id="check_date"    
    )

async def get_doctors():
    async with ClientSession() as session:
        try:
            response = await session.get(url=GET_DOCTORS)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Something went wrong: {e.__cause__}")
            return None
        data = await response.json()
        return data
    
async def get_patients(telegram_id):
    async with ClientSession() as session:
        try:
            response = await session.get(url=f"{MY_PATIENTS}{telegram_id}")
            response.raise_for_status()
        except:
            return None
        data = await response.json()
        return data

async def start():
    doctors = await get_doctors()
    docs = doctors.get("response")
    for doc in docs:
        telegram_id = doc.get("telegram_id")
        data = await get_patients(telegram_id=telegram_id)
        patients = data.get("patients")
        for p in patients:
            contact = p.get("telegram_id")
            name = p.get("individual_number")
            message = get_message_object(chat_id=contact, first_name=name)
            help_func = StartDialog(event=message)
            await help_func.handle()

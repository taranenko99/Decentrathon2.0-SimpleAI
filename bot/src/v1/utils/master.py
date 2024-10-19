# Third-Party
from aiohttp import ClientSession

# Local
from src.settings.config import (
    CHAT, REG_DOC_URL, REG_PAT_URL, 
    UPLOAD_TESTS, CHECK_DOC, CHECK_PAT, MY_PATIENTS
)


async def check_doctor(telegram_id: int):
    async with ClientSession() as session:
        try:
            response = await session.get(
                url=CHECK_DOC, params={"telegram_id": telegram_id}
            )
            response.raise_for_status()
        except:
            return None
        data = await response.json()
        return data
    
async def check_patient(telegram_id: int):
    async with ClientSession() as session:
        try:
            response = await session.get(
                url=CHECK_PAT, params={"telegram_id": telegram_id}
            )
            response.raise_for_status()
        except:
            return None
        data = await response.json()
        return data
    
async def create_doctor(data: dict):
    async with ClientSession() as session:
        try:
            response = await session.post(url=REG_DOC_URL, json=data)
            response.raise_for_status()
        except:
            return None
        data = await response.json()
        return data
    
async def create_patient(data: dict):
    async with ClientSession() as session:
        try:
            response = await session.post(url=REG_PAT_URL, json=data)
            response.raise_for_status()
        except:
            return None
        data = await response.json()
        return data
    
async def update_patient(data: dict):
    async with ClientSession() as session:
        try:
            response = await session.patch(url=REG_PAT_URL, json=data)
            response.raise_for_status()
        except:
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

async def make_chat(telegram_id: int, message: str):
    data = {"telegram_id": telegram_id, "message": message}
    async with ClientSession() as session:
        try:
            response = await session.post(url=REG_PAT_URL, json=data)
            response.raise_for_status()
        except:
            return None
        data = await response.json()
        return data

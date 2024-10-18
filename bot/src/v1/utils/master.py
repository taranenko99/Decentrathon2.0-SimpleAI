# Third-Party
from aiohttp import ClientSession


async def check_user_in_api(telegram_id: int):
    async with ClientSession() as session:
        response = await session.post(url=...)
        pass


async def create_user(data: dict):
    async with ClientSession() as session:
        response = await session.post(url=..., json=...)
        response.raise_for_status()
        if response.status == 200:
            return True
        else:
            return False
        
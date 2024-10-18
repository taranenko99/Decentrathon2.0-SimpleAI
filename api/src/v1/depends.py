# Third-Party
from sqlalchemy.ext.asyncio import AsyncSession

# Python
from typing import AsyncGenerator

# Local
from src.settings.base import session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with session() as conn:
        yield conn

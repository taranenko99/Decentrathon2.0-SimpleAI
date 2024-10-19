# Aiogram
import asyncio

# Local
from src.settings.base import bot, logger, AIOREDIS, dp, http_session
from src.settings.config import MENU, DESCRIPTION
from src.v1.routers import ROUTERS
from src.v1.tasks import get_scheduler


async def main():
    try:
        await bot.set_my_commands(commands=MENU)
        await bot.set_my_description(description=DESCRIPTION)
        dp.include_routers(*ROUTERS)
        logger.info("START BOT")
        await asyncio.gather(
            dp.start_polling(bot),
            get_scheduler()
        )
    except KeyboardInterrupt:
        pass
    finally:
        await shutdown()

async def shutdown():
    await AIOREDIS.aclose()
    await http_session.close()
    logger.info("SHUTDOWN BOT")

    
if __name__ == "__main__":
    asyncio.run(main())

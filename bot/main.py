# Aiogram
import asyncio

# Local
from src.settings.base import bot, logger, AIOREDIS, dp, http_session
from src.settings.config import MENU, DESCRIPTION


async def main():
    try:
        await bot.set_my_commands(commands=MENU)
        await bot.set_my_description(description=DESCRIPTION)
        logger.info(msg="START BOT")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        pass
    finally:
        await shutdown()

async def shutdown():
    await AIOREDIS.aclose()
    await http_session.close()
    logger.info(msg="SHUTDOWN BOT")

    
if __name__ == "__main__":
    asyncio.run(main())

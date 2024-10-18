# Third-Party
import uvicorn
import asyncio

# Local
from src.settings.base import logger


async def main():
    config = uvicorn.Config(
        app="main:app", host="0.0.0.0", 
        port=8000
    )
    server = uvicorn.Server(config=config)
    logger.info(msg="SERVER STARTED")
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Shutdown server: {e.__cause__}")

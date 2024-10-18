# Third-Party
import uvicorn
import asyncio
from llm.vector_db.utils import create_vector_db

# Local
from src.settings.base import logger


async def main():
    config = uvicorn.Config(
        app="main:app", host="0.0.0.0", 
        port=8000
    )
    server = uvicorn.Server(config=config)
    create_vector_db(r'llm/vector_db/symptoms.txt')
    logger.info(msg="SERVER STARTED")
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Shutdown server: {e.__cause__}")

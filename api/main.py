# Third-Party
import uvicorn
import asyncio
from src.llm.vector_db.utils import create_vector_db

# Local
from src.settings.base import logger, app
from src.v1.views import \
    Registration, ForDoctors, ViewUsers, Chat, CheckUser


async def main():
    app.include_router(Registration().router)
    app.include_router(ForDoctors().router)
    app.include_router(ViewUsers().router)
    app.include_router(Chat().router)
    app.include_router(CheckUser().router)
    config = uvicorn.Config(
        app=app, host="0.0.0.0", 
        port=8000
    )
    server = uvicorn.Server(config=config)
    create_vector_db(r'api/src/llm/vector_db/symptoms.txt')
    logger.info("SERVER STARTED")
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown server")
    except Exception as e:
        logger.error(f"Shutdown server: {e.__cause__}")

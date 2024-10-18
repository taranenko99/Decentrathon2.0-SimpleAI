# FastApi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Third-Party
from loguru import logger
from decouple import config
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker,
)


app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")
SQL_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(url=SQL_URL)
session = async_sessionmaker(bind=engine, expire_on_commit=False)

VOLUME = "./volume/"
logger.add(
    sink=f"{VOLUME}logs_{{time:YYYY-MM-DD}}.log.json", 
    level="INFO", enqueue=True, format="{time} {level} {message}", 
    colorize=True, retention="7 days",
    serialize=True, rotation="00:00", compression="zip"
)

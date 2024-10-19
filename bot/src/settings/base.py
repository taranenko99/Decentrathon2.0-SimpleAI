# Aiogram
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.session.aiohttp import AiohttpSession

# Third-Party
from loguru import logger
from decouple import config
from redis import asyncio as aioredis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore

# Python
import time


BOT_TOKEN = config("BOT_TOKEN")
REDIS_URL = config("REDIS_URL")
POOL = aioredis.ConnectionPool.from_url(
    url=REDIS_URL, max_connections=20
)
AIOREDIS = aioredis.Redis(connection_pool=POOL)
http_session = AiohttpSession(timeout=60.0)
storage = RedisStorage(redis=AIOREDIS)
bot: Bot = Bot(token=BOT_TOKEN, session=http_session)
dp: Dispatcher = Dispatcher(storage=storage)
scheduler = AsyncIOScheduler(jobstores={
    "redis" : RedisJobStore(host="localhost", port="6379", db=1)
})


VOLUME = "./volume/"
logger.add(
    sink=f"{VOLUME}logs_{{time:YYYY-MM-DD}}.log.json", 
    level="INFO", enqueue=True, format="{time} {level} {message}", 
    colorize=True, retention="7 days",
    serialize=True, rotation="00:00", compression="zip"
)

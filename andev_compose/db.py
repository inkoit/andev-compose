import aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from . import config

REDIS_POOL = aioredis.ConnectionPool.from_url(config.get_redis_url())

PG_ENGINE = create_async_engine(config.get_postgres_url())
SessionLocal = sessionmaker(
    PG_ENGINE, expire_on_commit=False, class_=AsyncSession
)


async def get_anagrams_db():
    return aioredis.Redis(connection_pool=REDIS_POOL)


async def get_devices_db():
    async with SessionLocal() as session:
        yield session

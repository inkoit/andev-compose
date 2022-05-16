import collections

import aioredis
import fastapi
from sqlalchemy import select, func, Text, insert
from sqlalchemy.dialects.postgresql import array
import sqlalchemy.ext.asyncio as sa_aio
import sqlalchemy.orm as sa_orm

from . import config
from . import models

app = fastapi.FastAPI()


@app.on_event("startup")
async def startup():
    app.state.redis_pool = aioredis.ConnectionPool.from_url(config.get_redis_url())

    app.state.pg_engine = sa_aio.create_async_engine(config.get_postgres_url())
    app.state.pg_session_factory = sa_orm.sessionmaker(
        app.state.pg_engine, expire_on_commit=False, class_=sa_aio.AsyncSession
    )


async def get_redis():
    return aioredis.Redis(connection_pool=app.state.redis_pool)


async def get_postgres():
    async with app.state.pg_session_factory() as session:
        yield session


@app.get("/are_anagrams")
async def anagrams(first: str, second: str, redis=fastapi.Depends(get_redis)):
    are_anagrams = collections.Counter(first) == collections.Counter(second)
    return {
        "are_anagrams": are_anagrams,
        "counter": await redis.incr("anagrams-counter", int(are_anagrams)),
    }


@app.put("/devices/random", status_code=201)
async def put_random_devices(
    devices_count: int = 10,
    attach_count: int = 5,
    postgres: sa_aio.AsyncSession = fastapi.Depends(get_postgres),
):
    random_devices = select(
        array(["emeter", "zigbee", "lora", "gsm"])[func.floor(func.random() * 4 + 1)],
        func.substr(func.md5(func.random().cast(Text)), 0, 13),
    ).select_from(func.generate_series(1, devices_count))

    devices_ids = (
        insert(models.Device)
        .from_select([models.Device.dev_type, models.Device.dev_id], random_devices)
        .returning(models.Device.id)
        .cte()
    )

    insert_endpoints = insert(models.Endpoint).from_select(
        [models.Endpoint.device_id],
        devices_ids.select().order_by(func.random()).limit(attach_count),
    )

    await postgres.execute(insert_endpoints)
    await postgres.commit()


@app.get("/devices/unattached_stats")
async def get_unattached_devices_stats(
    postgres: sa_aio.AsyncSession = fastapi.Depends(get_postgres),
):
    query = (
        select(models.Device.dev_type, func.count("*"))
        .outerjoin_from(models.Device, models.Endpoint)
        .where(models.Endpoint.id.is_(None))
        .group_by(models.Device.dev_type)
    )
    result = await postgres.execute(query)
    return result.fetchall()

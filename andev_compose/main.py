import collections

import aioredis
import aiopg
import fastapi

from . import config
from . import models

app = fastapi.FastAPI()


@app.on_event("startup")
async def startup():
    app.state.pg_pool = await aiopg.create_pool(config.get_postgres_dsn())
    app.state.redis_pool = aioredis.ConnectionPool.from_url(config.get_redis_url())


async def get_redis():
    return aioredis.Redis(connection_pool=app.state.redis_pool)


async def get_postgres():
    async with app.state.pg_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            yield cursor


@app.get("/are_anagrams")
async def anagrams(first: str, second: str, redis = fastapi.Depends(get_redis)):
    are_anagrams = collections.Counter(first) == collections.Counter(second)
    return {"are_anagrams": are_anagrams, "counter": await redis.incr("anagrams-counter", int(are_anagrams))}


@app.put("/devices/random", status_code=201)
async def put_random_devices(
    devices_count: int = 10,
    attach_count: int = 5,
    postgres: aiopg.Cursor = fastapi.Depends(get_postgres),
):
    query = f"""
    WITH ids AS (
        INSERT INTO devices (dev_type, dev_id)
        SELECT (ARRAY['emeter', 'zigbee', 'lora', 'gsm'])[floor(random() * 4 + 1)], substr(md5(random()::text), 0, 13)
        FROM generate_series(1, {devices_count}) RETURNING devices.id
    )
    INSERT INTO endpoints (device_id) SELECT id FROM ids ORDER BY random() LIMIT {attach_count};
    """
    await postgres.execute(query)


@app.get("/devices/unattached_stats")
async def get_unattached_devices_stats(postgres: aiopg.Cursor = fastapi.Depends(get_postgres)):
    query = """
    SELECT devices.dev_type, COUNT(*)
    FROM devices
    LEFT OUTER JOIN endpoints ON endpoints.device_id = devices.id
    WHERE endpoints.id IS NULL
    GROUP BY devices.dev_type;
    """
    await postgres.execute(query)
    return await postgres.fetchall()
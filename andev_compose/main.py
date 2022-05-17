import collections

import fastapi

from . import db
from . import crud

app = fastapi.FastAPI()


@app.get("/are_anagrams")
async def anagrams(first: str, second: str, anagrams_db=fastapi.Depends(db.get_anagrams_db)):
    are_anagrams = collections.Counter(first) == collections.Counter(second)
    return {
        "are_anagrams": are_anagrams,
        "counter": await anagrams_db.incr("anagrams-counter", int(are_anagrams)),
    }


@app.put("/devices/random", status_code=201)
async def put_random_devices(
    devices_count: int = 10,
    attach_count: int = 5,
    devices_db: db.AsyncSession = fastapi.Depends(db.get_devices_db),
):
    await crud.put_random_devices(devices_db, devices_count, attach_count)


@app.get("/devices/unattached_stats")
async def get_unattached_devices_stats(
    devices_db: db.AsyncSession = fastapi.Depends(db.get_devices_db),
):
    return await crud.get_unattached_devices_stats(devices_db)

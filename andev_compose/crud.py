from sqlalchemy import select, func, Text, insert
from sqlalchemy.dialects.postgresql import array

from . import db
from . import models

DEVICES = ["emeter", "zigbee", "lora", "gsm"] 
MAC_ADDR_HEX_LEN = 12


async def put_random_devices(
    devices_db: db.AsyncSession,
    devices_count: int = 10,
    attach_count: int = 5,
):
    random_devices = select(
        array(DEVICES)[func.floor(func.random() * len(DEVICES) + 1)],
        func.substr(func.md5(func.random().cast(Text)), 0, MAC_ADDR_HEX_LEN + 1),
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

    await devices_db.execute(insert_endpoints)
    await devices_db.commit()


async def get_unattached_devices_stats(devices_db: db.AsyncSession):
    query = (
        select(models.Device.dev_type, func.count("*"))
        .outerjoin_from(models.Device, models.Endpoint)
        .where(models.Endpoint.id.is_(None))
        .group_by(models.Device.dev_type)
    )
    result = await devices_db.execute(query)
    return result.fetchall()

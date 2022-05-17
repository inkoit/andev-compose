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
    """Inserts randomly generated devices and randomly attaches endpoints to some of them

    It was pretty tricky to put function-heavy double-insert statement into SQLAlchemy.
    I'm not sure if it was a good idea still, so here's original SQL query:

    WITH (
        INSERT INTO devices
        SELECT ARRAY[<devices>][FLOOR(RANDOM * <len(devices)> + 1)], substr(md5(random())::text, 0, <mac_addr_len> + 1)
        FROM generate_series(1, <devices_count>)
        RETURNING devices.id
    ) as devices_ids
    INSERT INTO endpoints (device_id) SELECT * FROM devices_ids ORDER BY random() LIMIT <attach_count>

    """

    random_device = array(DEVICES, dimensions=1)[func.floor(func.random() * len(DEVICES) + 1)]
    random_md5 = func.md5(func.random().cast(Text))
    random_mac_addr = func.substr(random_md5, 0, MAC_ADDR_HEX_LEN + 1)

    random_devices = select(random_device, random_mac_addr).select_from(
        func.generate_series(1, devices_count)
    )

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
    """Gets counts of unattached devices grouped by their types"""
    query = (
        select(models.Device.dev_type, func.count("*"))
        .outerjoin_from(models.Device, models.Endpoint)
        .where(models.Endpoint.id.is_(None))
        .group_by(models.Device.dev_type)
    )
    result = await devices_db.execute(query)
    return result.fetchall()

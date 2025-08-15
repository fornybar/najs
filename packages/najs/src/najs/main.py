import io
import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import fastavro
import nats
from loguru import logger
from nats.aio.client import Client

from najs.schema import fetch_schema
from najs.types import StreamMsg


@asynccontextmanager
async def nats_context(
    *args: Any,  # noqa: ANN401
    **kwargs: dict[str, Any],
) -> AsyncGenerator[Client, None]:
    """Context with a nats connection

    All parameters are sent directly to nats.aio.client.Client.connect.
    Reference: https://nats-io.github.io/nats.py/modules.html#nats.aio.client.Client.connect
    """
    client = await nats.connect(*args, **kwargs)
    try:
        yield client
    finally:
        logger.info("Closing NATS client")
        await client.flush()
        await client.close()


def avro_serialize(records: list[dict], schema: str) -> bytes:
    payload = io.BytesIO()
    fastavro.schemaless_writer(payload, schema, records)
    return payload.getvalue()


async def publish(
    nc: Client,
    msg: StreamMsg,
) -> nats.js.api.PubAck:
    """Publish message to Jetstream"""
    js = nc.jetstream()

    if msg.schema_name is None:
        payload = json.dumps(msg.records).encode()
    else:
        schema = await fetch_schema(js, msg.schema_name)
        payload = avro_serialize(msg.records, schema)

    return await js.publish(
        subject=msg.subject,
        payload=payload,
        stream=msg.stream,
        headers=msg.headers,
    )

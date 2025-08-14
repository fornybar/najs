import io
import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import fastavro
import nats
from loguru import logger
from nats.aio.client import Client

from natsy.schema import fetch_schema
from natsy.types import Message


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



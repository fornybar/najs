import asyncio
import logging
from collections.abc import AsyncGenerator

import nats.errors
from nats.aio.msg import Msg
from nats.js import JetStreamContext
from nats.js.api import AckPolicy

logger = logging.getLogger(name=__name__)

async def yield_messages(  # noqa: PLR0913
    sub: JetStreamContext.PullSubscription,
    batch: int,
    *,
    run_forever: bool = False,
    nats_timeout: float | None = 5,
    heartbeat: float | None = 1,
) -> AsyncGenerator[list[Msg], None]:
    # try block for cleanup.
    try:
        while True:
            try:
                msgs = await sub.fetch(
                    batch=batch,
                    timeout=nats_timeout,
                    heartbeat=heartbeat,
                )
                yield msgs

            except nats.errors.TimeoutError:
                if not run_forever:
                    break
                if heartbeat is not None:
                    await asyncio.sleep(heartbeat)
    finally:
        await sub.unsubscribe()

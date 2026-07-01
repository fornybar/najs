import asyncio
import logging
from collections.abc import AsyncGenerator

import nats.errors
from nats.aio.msg import Msg
from nats.js import JetStreamContext
from nats.js.api import AckPolicy

logger = logging.getLogger(name=__name__)


async def auto_ack(msgs: list[Msg], policy: AckPolicy) -> None:
    match policy:
        case AckPolicy.ALL if len(msgs) > 0:
            try:
                await msgs[-1].ack()
            except nats.errors.TimeoutError as e:
                logger.log(msg=e, level=logging.ERROR)
                raise
        case AckPolicy.EXPLICIT:
            try:
                async with asyncio.TaskGroup() as tg:
                    for msg in msgs:
                        tg.create_task(msg.ack())
            except* nats.errors.TimeoutError as e:
                logger.log(msg=e, level=logging.ERROR)
                raise
        case AckPolicy.NONE:
            pass


async def yield_messages(  # noqa: PLR0913
    sub: JetStreamContext.PullSubscription,
    batch: int,
    *,
    enable_auto_ack: bool = False,
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

                ack_policy = (await sub.consumer_info()).config.ack_policy
                if enable_auto_ack and ack_policy is not None:
                    await auto_ack(msgs, ack_policy)

            except nats.errors.TimeoutError:
                if not run_forever:
                    break
                if heartbeat is not None:
                    await asyncio.sleep(heartbeat)
    finally:
        await sub.unsubscribe()

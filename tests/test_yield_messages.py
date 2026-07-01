import pytest
from mock_classes import FakeMsg, FakeSubscription
from nats.errors import TimeoutError as NatsTimeoutError
from nats.js.api import AckPolicy

from najs.yield_messages import auto_ack, yield_messages


@pytest.mark.asyncio
async def test_auto_ack_explicit():
    msgs = [FakeMsg(), FakeMsg(), FakeMsg()]

    await auto_ack(msgs, AckPolicy.EXPLICIT)

    assert [msg.ack_count for msg in msgs] == [1, 1, 1]


@pytest.mark.asyncio
async def test_auto_ack_all():
    msgs = [FakeMsg(), FakeMsg(), FakeMsg()]

    await auto_ack(msgs, AckPolicy.ALL)

    assert [msg.ack_count for msg in msgs] == [0, 0, 1]


@pytest.mark.asyncio
async def test_auto_ack_none():
    msgs = [FakeMsg(), FakeMsg()]

    await auto_ack(msgs, AckPolicy.NONE)

    assert [msg.ack_count for msg in msgs] == [0, 0]


@pytest.mark.asyncio
async def test_auto_ack_multiple_errors():
    msgs = [FakeMsg(RuntimeError("first")), FakeMsg(ValueError("second"))]

    with pytest.raises(ExceptionGroup) as exc_info:
        await auto_ack(msgs, AckPolicy.EXPLICIT)

    assert {type(error) for error in exc_info.value.exceptions} == {
        RuntimeError,
        ValueError,
    }


@pytest.mark.asyncio
async def test_yield_messages_yields_results_without_auto_ack_by_default():
    msgs = [FakeMsg(), FakeMsg()]
    sub = FakeSubscription([msgs, NatsTimeoutError()], ack_policy=AckPolicy.ALL)

    yielded = [
        batch
        async for batch in yield_messages(
            sub,
            2,
            nats_timeout=1.5,
            heartbeat=0.25,
        )
    ]

    assert yielded == [msgs]
    assert sub.fetch_calls == [
        {"batch": 2, "timeout": 1.5, "heartbeat": 0.25},
        {"batch": 2, "timeout": 1.5, "heartbeat": 0.25},
    ]
    assert [msg.ack_count for msg in msgs] == [0, 0]
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_yields_empty_batches():
    msg = FakeMsg()
    sub = FakeSubscription(
        [[], [msg], NatsTimeoutError()],
        ack_policy=AckPolicy.EXPLICIT,
    )

    yielded = [batch async for batch in yield_messages(sub, 2, enable_auto_ack=True)]

    assert yielded == [[], [msg]]
    assert msg.ack_count == 1
    assert sub.fetch_calls == [
        {"batch": 2, "timeout": 5, "heartbeat": 1},
        {"batch": 2, "timeout": 5, "heartbeat": 1},
        {"batch": 2, "timeout": 5, "heartbeat": 1},
    ]
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_does_not_ack_when_closed_before_resume():
    msg = FakeMsg()
    sub = FakeSubscription([[msg]], ack_policy=AckPolicy.EXPLICIT)
    generator = yield_messages(sub, 1, enable_auto_ack=True)

    assert await anext(generator) == [msg]
    await generator.aclose()

    assert msg.ack_count == 0
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_does_not_ack_when_closed_after_consumer_raises():
    msg = FakeMsg()
    sub = FakeSubscription([[msg]], ack_policy=AckPolicy.EXPLICIT)
    generator = yield_messages(sub, 1, enable_auto_ack=True)

    try:
        with pytest.raises(RuntimeError, match="consumer failed"):
            async for _ in generator:
                raise RuntimeError("consumer failed")
    finally:
        await generator.aclose()

    assert msg.ack_count == 0
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_respects_ack_policy_none():
    msgs = [FakeMsg(), FakeMsg()]
    sub = FakeSubscription([msgs, NatsTimeoutError()], ack_policy=AckPolicy.NONE)

    yielded = [batch async for batch in yield_messages(sub, 2, enable_auto_ack=True)]

    assert yielded == [msgs]
    assert [msg.ack_count for msg in msgs] == [0, 0]
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_respects_ack_policy_all():
    msgs = [FakeMsg(), FakeMsg()]
    sub = FakeSubscription([msgs, NatsTimeoutError()], ack_policy=AckPolicy.ALL)

    yielded = [batch async for batch in yield_messages(sub, 2, enable_auto_ack=True)]

    assert yielded == [msgs]
    assert [msg.ack_count for msg in msgs] == [0, 1]
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_stops_on_timeout_without_yielding():
    sub = FakeSubscription([NatsTimeoutError()])

    yielded = [batch async for batch in yield_messages(sub, 10)]

    assert yielded == []
    assert sub.fetch_calls == [
        {"batch": 10, "timeout": 5, "heartbeat": 1},
    ]
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_passes_timeout_none_to_fetch():
    sub = FakeSubscription([NatsTimeoutError()])

    yielded = [batch async for batch in yield_messages(sub, 10, nats_timeout=None)]

    assert yielded == []
    assert sub.fetch_calls == [
        {"batch": 10, "timeout": None, "heartbeat": 1},
    ]
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_run_forever_waits_after_timeout(monkeypatch):
    sleeps = []
    msg = FakeMsg()
    sub = FakeSubscription([NatsTimeoutError(), [msg]])

    async def fake_sleep(seconds):
        sleeps.append(seconds)

    monkeypatch.setattr("najs.yield_messages.asyncio.sleep", fake_sleep)

    generator = yield_messages(
        sub,
        1,
        heartbeat=0.25,
        run_forever=True,
    )

    try:
        assert await anext(generator) == [msg]
    finally:
        await generator.aclose()

    assert sleeps == [0.25]
    assert sub.fetch_calls == [
        {"batch": 1, "timeout": 5, "heartbeat": 0.25},
        {"batch": 1, "timeout": 5, "heartbeat": 0.25},
    ]
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_run_forever_retries_timeout_without_sleeping_when_heartbeat_is_none(
    monkeypatch,
):
    sleeps = []
    msg = FakeMsg()
    sub = FakeSubscription([NatsTimeoutError(), [msg]])

    async def fake_sleep(seconds):
        sleeps.append(seconds)

    monkeypatch.setattr("najs.yield_messages.asyncio.sleep", fake_sleep)

    generator = yield_messages(
        sub,
        1,
        heartbeat=None,
        run_forever=True,
    )

    try:
        assert await anext(generator) == [msg]
    finally:
        await generator.aclose()

    assert sleeps == []
    assert sub.fetch_calls == [
        {"batch": 1, "timeout": 5, "heartbeat": None},
        {"batch": 1, "timeout": 5, "heartbeat": None},
    ]
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_propagates_fetch_errors_and_cleans_up():
    error = RuntimeError("fetch failed")
    sub = FakeSubscription([error])

    with pytest.raises(RuntimeError, match="fetch failed"):
        async for _ in yield_messages(sub, 1):
            pass

    assert sub.fetch_calls == [
        {"batch": 1, "timeout": 5, "heartbeat": 1},
    ]
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_propagates_ack_errors_and_cleans_up():
    error = RuntimeError("ack failed")
    msg = FakeMsg(ack_error=error)
    sub = FakeSubscription([[msg]], ack_policy=AckPolicy.EXPLICIT)
    generator = yield_messages(sub, 1, enable_auto_ack=True)

    assert await anext(generator) == [msg]

    with pytest.raises(ExceptionGroup) as exc_info:
        await anext(generator)

    assert len(exc_info.value.exceptions) == 1
    assert isinstance(exc_info.value.exceptions[0], RuntimeError)
    assert str(exc_info.value.exceptions[0]) == "ack failed"
    assert msg.ack_count == 0
    assert sub.fetch_calls == [
        {"batch": 1, "timeout": 5, "heartbeat": 1},
    ]
    assert sub.unsubscribe_count == 1


@pytest.mark.asyncio
async def test_yield_messages_propagates_ack_timeout_errors_and_cleans_up():
    msg = FakeMsg(ack_error=NatsTimeoutError())
    sub = FakeSubscription([[msg]], ack_policy=AckPolicy.EXPLICIT)
    generator = yield_messages(sub, 1, enable_auto_ack=True)

    assert await anext(generator) == [msg]

    with pytest.raises(ExceptionGroup) as exc_info:
        await anext(generator)

    assert len(exc_info.value.exceptions) == 1
    assert isinstance(exc_info.value.exceptions[0], NatsTimeoutError)
    assert msg.ack_count == 0
    assert sub.fetch_calls == [
        {"batch": 1, "timeout": 5, "heartbeat": 1},
    ]
    assert sub.unsubscribe_count == 1

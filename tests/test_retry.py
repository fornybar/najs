import inspect

import nats.errors
import pytest

from najs.retry import nats_retry


@pytest.mark.asyncio
async def test_nats_retry_wraps_existing_function_and_retries():
    calls = 0

    async def flaky(value: str) -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise nats.errors.TimeoutError
        return value

    wrapped = nats_retry(
        flaky,
        attempts=3,
        base_delay_seconds=0.0,
        max_delay_seconds=0.0,
    )

    assert await wrapped("ok") == "ok"
    assert calls == 3


@pytest.mark.asyncio
async def test_nats_retry_does_not_retry_non_nats_exceptions():
    calls = 0

    message = "boom"

    @nats_retry(attempts=3, base_delay_seconds=0.0, max_delay_seconds=0.0)
    async def fail() -> None:
        nonlocal calls
        calls += 1
        raise ValueError(message)

    with pytest.raises(ValueError, match=message):
        await fail()

    assert calls == 1


@pytest.mark.asyncio
async def test_nats_retry_wrapped_function_forwards_kwargs():
    async def echo(value: str, *, suffix: str) -> str:
        return value + suffix

    wrapped = nats_retry(echo)

    assert await wrapped("hello", suffix="!") == "hello!"


@pytest.mark.asyncio
async def test_nats_retry_preserves_signature_and_retries():
    calls = 0

    @nats_retry(attempts=3, base_delay_seconds=0.0, max_delay_seconds=0.0)
    async def flaky(value: int, *, scale: int = 2) -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise nats.errors.NoRespondersError
        return value * scale

    assert str(inspect.signature(flaky)) == "(value: int, *, scale: int = 2) -> int"
    assert await flaky(4, scale=3) == 12
    assert calls == 2


@pytest.mark.asyncio
async def test_nats_retry_supports_bare_decorator_usage():
    @nats_retry
    async def echo(value: str) -> str:
        return value

    assert str(inspect.signature(echo)) == "(value: str) -> str"
    assert await echo("hello") == "hello"

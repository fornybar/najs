"""Retry helpers for transient infrastructure errors."""

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import overload

import nats.errors
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

type RetryableExceptions = tuple[type[Exception], ...]
type AsyncCallable[**P, R] = Callable[P, Awaitable[R]]
type AsyncDecorator[**P, R] = Callable[[AsyncCallable[P, R]], AsyncCallable[P, R]]


NATS_RETRY_EXCEPTIONS: RetryableExceptions = (
    nats.errors.TimeoutError,
    nats.errors.NoRespondersError,
    nats.errors.ConnectionClosedError,
)


@overload
def nats_retry[**P, R](func: AsyncCallable[P, R], /) -> AsyncCallable[P, R]: ...


@overload
def nats_retry[**P, R](
    func: AsyncCallable[P, R],
    /,
    *,
    attempts: int = 6,
    base_delay_seconds: float = 0.25,
    max_delay_seconds: float = 3.0,
) -> AsyncCallable[P, R]: ...


@overload
def nats_retry[**P, R](
    *,
    attempts: int = 6,
    base_delay_seconds: float = 0.25,
    max_delay_seconds: float = 3.0,
) -> AsyncDecorator[P, R]: ...


def nats_retry[**P, R](
    func: AsyncCallable[P, R] | None = None,
    /,
    *,
    attempts: int = 6,
    base_delay_seconds: float = 0.25,
    max_delay_seconds: float = 3.0,
) -> AsyncCallable[P, R] | AsyncDecorator[P, R]:
    """Wrap or decorate an async function with transient NATS retries.

    Args:
        func: Async callable to wrap when used as `nats_retry(func)` or `@nats_retry`.
        attempts: Maximum number of attempts before re-raising the last error.
        base_delay_seconds: Base backoff delay (also used as the minimum delay).
        max_delay_seconds: Maximum backoff delay.

    Returns:
        Either a wrapped async callable or a decorator factory, depending on how
        it is invoked.

    Examples:
        Basic decorator usage:

        ```python
        from najs.retry import nats_retry

        @nats_retry
        async def stream_info(js, stream: str):
            return await js.stream_info(stream)
        ```

        Configured decorator usage:

        ```python
        @nats_retry(attempts=3, base_delay_seconds=0.1)
        async def publish(js, subject: str, payload: bytes) -> None:
            await js.publish(subject, payload)
        ```

        Wrapping a bound method:

        ```python
        get_stream_info = nats_retry(js.stream_info, attempts=3)
        info = await get_stream_info("events")
        ```
    """

    def decorator(inner: AsyncCallable[P, R]) -> AsyncCallable[P, R]:
        @wraps(inner)
        async def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            retrying = AsyncRetrying(
                retry=retry_if_exception_type(NATS_RETRY_EXCEPTIONS),
                stop=stop_after_attempt(attempts),
                wait=wait_exponential(
                    multiplier=base_delay_seconds,
                    min=base_delay_seconds,
                    max=max_delay_seconds,
                ),
                reraise=True,
            )
            return await retrying(inner, *args, **kwargs)

        return wrapped

    if func is not None:
        return decorator(func)

    return decorator

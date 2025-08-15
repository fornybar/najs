from pathlib import Path

import najs
import nats
import nkeys
import pytest
import pytest_asyncio
from najs import nats_context, publish
from najs.schema import fetch_schema
from najs.types import StreamMsg


def test_version():
    assert najs.__version__ == "0.0.1"


def test_natspy_import():
    assert isinstance(nats.__file__, str)


def test_nkeys_import():
    assert isinstance(nkeys.__file__, str)


@pytest.mark.asyncio
async def test_nats_context(single_server):
    async with nats_context() as nc:
        assert nc.is_connected


@pytest_asyncio.fixture
async def nc(single_server):
    async with nats_context() as inited_context:
        yield inited_context


@pytest_asyncio.fixture
async def sample_subject(nc):
    js = nc.jetstream()
    stream = "MYSTREAM"
    subject = "sample.subject"
    await js.add_stream(name=stream, subjects=[subject])
    return stream, subject


@pytest.mark.asyncio
async def test_publish_no_schema(nc, sample_subject):
    stream, subject = sample_subject
    ack = await publish(
        nc,
        StreamMsg(
            stream=stream,
            subject=subject,
            records=[
                {"a": 1},
                {"b": 2},
            ],
        ),
    )
    assert ack.stream == stream


@pytest.mark.asyncio
async def test_publish_with_schema(nc, sample_subject):
    stream, subject = sample_subject
    js = nc.jetstream()

    # Ensure that schema exists
    await js.create_key_value(bucket=najs.settings.SCHEMA_REGISTRY_BUCKET)
    schema_name = "sample.schema"
    await fetch_schema(
        js,
        schema_name,
        fallback_path=Path(__file__).parent / f"{schema_name}.avsc",
    )

    ack = await publish(
        nc,
        StreamMsg(
            stream=stream,
            subject=subject,
            records=[
                {"number": 1.1, "sometext": "hei"},
            ],
            headers={"one": "header"},
            schema_name=schema_name,
        ),
    )
    assert ack.stream == stream

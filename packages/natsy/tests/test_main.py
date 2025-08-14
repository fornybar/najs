import nats
import natsy
import pytest
from natsy import nats_context


def test_version():
    assert natsy.__version__ == "0.0.1"


def test_natspy_import():
    assert isinstance(nats.__file__, str)


@pytest.mark.asyncio
async def test_nats_context(single_server):
    async with nats_context() as nc:
        assert nc.is_connected

import nats
import natsy


def test_version():
    assert natsy.__version__ == "0.0.1"


def test_natspy_import():
    assert isinstance(nats.__file__, str)

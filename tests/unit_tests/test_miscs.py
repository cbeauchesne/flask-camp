from flask_camp._services._memory_cache import _MemoryCache


def test_api():
    assert hasattr(_MemoryCache(), "client")
    assert _MemoryCache().client is None

import pytest
from unittest.mock import patch, MagicMock

from helpers.redis_helper import RedisHelper


def test_redis_helper_init_with_mock(monkeypatch):
    # Patch redis.Redis to avoid real connection
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True

    with patch('helpers.redis_helper.redis.Redis', return_value=mock_redis):
        r = RedisHelper()
        assert r is not None
        # client should be set and pingable
        assert hasattr(r, '_client')
        assert r._client.ping()

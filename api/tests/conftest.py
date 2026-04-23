import pytest
import fakeredis
import sys
from pathlib import Path
from unittest.mock import MagicMock
from main import app
from fastapi.testclient import TestClient

# Add the api directory to Python path so we can import 'main'
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_redis():
    """Create a fake Redis instance for testing"""
    fake_redis = fakeredis.FakeRedis(decode_responses=True)
    
    original_hget = fake_redis.hget
    def patched_hget(key, field):
        result = original_hget(key, field)
        if result == "" or result is None:
            return None
        return result
    
    fake_redis.hget = patched_hget
    return fake_redis


@pytest.fixture
def client(mock_redis, monkeypatch):
    """Patch Redis in main.py and provide test client"""
    monkeypatch.setattr("main.r", mock_redis)
    return TestClient(app)
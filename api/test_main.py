import pytest
from unittest.mock import Mock, patch, MagicMock
import uuid
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

@pytest.fixture
def mock_redis():
    """Mock Redis for testing"""
    with patch('main.r') as mock_r:
        yield mock_r

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_success(self, mock_redis):
        """Test health endpoint returns healthy status"""
        mock_redis.ping.return_value = True
        
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
        mock_redis.ping.assert_called_once()

    def test_health_check_redis_failure(self, mock_redis):
        """Test health endpoint when Redis is unavailable"""
        mock_redis.ping.side_effect = Exception("Redis connection failed")
        
        response = client.get("/health")
        
        assert response.status_code == 503


class TestCreateJob:
    """Test job creation endpoint"""
    
    def test_create_job_success(self, mock_redis):
        """Test successful job creation"""
        mock_redis.lpush.return_value = 1
        mock_redis.hset.return_value = 1
        
        response = client.post("/jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        
        # Verify Redis calls
        mock_redis.lpush.assert_called_once()
        mock_redis.hset.assert_called_once()
        
        # Verify the job_id is a valid UUID
        job_id = data["job_id"]
        uuid.UUID(job_id)  # Should not raise

    def test_create_job_redis_failure(self, mock_redis):
        """Test job creation when Redis fails"""
        mock_redis.lpush.side_effect = Exception("Redis connection failed")
        
        response = client.post("/jobs")
        
        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()


class TestGetJob:
    """Test job status retrieval endpoint"""
    
    def test_get_job_success(self, mock_redis):
        """Test retrieving job status successfully"""
        job_id = str(uuid.uuid4())
        mock_redis.hget.return_value = "queued"
        
        response = client.get(f"/jobs/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == "queued"
        
        # Verify the correct Redis key was accessed
        mock_redis.hget.assert_called_once_with(f"job:{job_id}", "status")

    def test_get_job_not_found(self, mock_redis):
        """Test retrieving non-existent job"""
        job_id = str(uuid.uuid4())
        mock_redis.hget.return_value = None
        
        response = client.get(f"/jobs/{job_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_job_redis_failure(self, mock_redis):
        """Test retrieving job when Redis fails"""
        job_id = str(uuid.uuid4())
        mock_redis.hget.side_effect = Exception("Redis connection failed")
        
        response = client.get(f"/jobs/{job_id}")
        
        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()

    def test_get_job_completed_status(self, mock_redis):
        """Test retrieving a completed job"""
        job_id = str(uuid.uuid4())
        mock_redis.hget.return_value = "completed"
        
        response = client.get(f"/jobs/{job_id}")
        
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

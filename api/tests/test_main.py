import pytest
from fastapi.testclient import TestClient
import uuid

def test_health_check(client):
    """Test that /health endpoint returns healthy status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["redis"] == "connected"


def test_create_job(client):
    """Test that /jobs endpoint creates and returns job_id"""
    response = client.post("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    # Verify job was stored in Redis
    job_id = data["job_id"]
    get_response = client.get(f"/jobs/{job_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "queued"


def test_get_job_not_found(client):
    """Test that /jobs/{job_id} returns 404 for non-existent job"""
    response = client.get("/jobs/job-id-12345")
    assert response.status_code == 404
    assert response.json()["error"] == "not found"


def test_get_job_success(client):
    """Test that /jobs/{job_id} returns correct job status"""
    # Create a job first
    create_response = client.post("/jobs")
    job_id = create_response.json()["job_id"]
    
    # Get the job
    get_response = client.get(f"/jobs/{job_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "queued"


def test_job_id_is_uuid(client):
    """Test that created job_id is a valid UUID"""
    response = client.post("/jobs")
    job_id = response.json()["job_id"]
    try:
        uuid_obj = uuid.UUID(job_id)
        assert uuid_obj.version == 4
    except ValueError:
        pytest.fail("job_id is not a valid UUID")
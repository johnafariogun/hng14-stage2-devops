from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import uuid
import os
import logging

app = FastAPI()

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True
    )

@app.get("/health")
def health():
    """Health check endpoint for Docker"""
    if not r:
        raise HTTPException(status_code=503, detail="Redis connection failed")
    try:
        r.ping()
        return {"status": "healthy"}
    except redis.ConnectionError:
        raise HTTPException(status_code=503, detail="Redis connection failed")

@app.post("/jobs")
def create_job():
    if not r:
        logger.error("Attempted to create job but Redis client is not initialized")
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        job_id = str(uuid.uuid4())
        r.lpush("job", job_id)
        r.hset(f"job:{job_id}", "status", "queued")
        logger.info(f"Created job: {job_id}")
        return {"job_id": job_id}
    except redis.ConnectionError as e:
        logger.error(f"Redis error creating job: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if not r:
        logger.error("Attempted to get job but Redis client is not initialized")
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        status = r.hget(f"job:{job_id}", "status")
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"job_id": job_id, "status": status}
    except redis.ConnectionError as e:
        logger.error(f"Redis error retrieving job: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")

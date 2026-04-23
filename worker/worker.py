import redis
import time
import os
import signal
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Initialize Redis connection
try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True
    )
    r.ping()
    logger.info("Connected to Redis successfully")
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    sys.exit(1)

# Graceful shutdown handler
def signal_handler(signum, frame):
    logger.info("Received termination signal, shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def process_job(job_id):
    """Process a job and update its status"""
    try:
        logger.info(f"Processing job {job_id}")
        time.sleep(2)  # simulate work
        r.hset(f"job:{job_id}", "status", "completed")
        logger.info(f"Job completed: {job_id}")
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        try:
            r.hset(f"job:{job_id}", "status", "failed")
        except redis.ConnectionError:
            logger.error(f"Failed to update job status to failed for {job_id}")

# Main job processing loop
def main():
    logger.info("Worker started, listening for jobs...")
    while True:
        try:
            # Block for up to 5 seconds waiting for a job
            job = r.brpop("job", timeout=5)
            if job:
                _, job_id = job
                process_job(job_id)
        except redis.ConnectionError as e:
            logger.error(f"Redis connection lost: {e}")
            logger.info("Attempting to reconnect in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
# Multi-stage build for Worker service
FROM python:3.11-slim as builder

WORKDIR /build

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy only necessary files from builder
COPY --from=builder /root/.local /home/appuser/.local
COPY worker.py .

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    REDIS_HOST=redis \
    REDIS_PORT=6379

# Change ownership of files
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check - verify Redis connectivity
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import redis; redis.Redis(host='$REDIS_HOST', port=int('$REDIS_PORT'), decode_responses=True).ping()" || exit 1

# Run the worker
CMD ["python", "worker.py"]

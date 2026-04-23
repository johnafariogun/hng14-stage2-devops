# HNG14 Stage 2 DevOps - Job Processing System

A production-ready, multi-service job processing system with complete containerization and CI/CD pipeline.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Node.js)                   │
│                    Port: 3000                           │
│        - Job submission UI                             │
│        - Status polling dashboard                       │
│        - Health check endpoint                          │
└─────────────┬───────────────────────────────────────────┘
              │
              │ HTTP/JSON
              ▼
┌─────────────────────────────────────────────────────────┐
│                  API (Python/FastAPI)                   │
│                    Port: 8000                           │
│        - Job creation endpoint                          │
│        - Job status retrieval                           │
│        - Health check endpoint                          │
└─────────────┬───────────────────────────────────────────┘
              │
              │ Redis Queue
              ▼
┌─────────────────────────────────────────────────────────┐
│                    Redis Cache                          │
│              (Internal, not exposed)                    │
│        - Job queue storage                              │
│        - Job status tracking                            │
└─────────────┬───────────────────────────────────────────┘
              │
              │ Job consumption
              ▼
┌─────────────────────────────────────────────────────────┐
│                  Worker (Python)                        │
│        - Background job processor                       │
│        - Job status updates                             │
│        - Horizontal scaling ready                       │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

### System Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+
- (Optional) Python 3.11+ for local development
- (Optional) Node.js 18+ for local frontend development

### Supported Platforms
- Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- macOS 12+ (with Docker Desktop)
- Windows 10/11 Pro (with Docker Desktop and WSL 2)

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/johnafariogun/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration (optional for local development)
```

### 3. Build and Start Services
```bash
docker-compose up --build
```

The system will start all services in the following order:
1. Redis (health check enabled)
2. API (waits for Redis health check)
3. Worker (waits for API health check)
4. Frontend (waits for API health check)

### 4. Verify System is Running

**Check service health:**
```bash
# API health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Frontend health
curl http://localhost:3000/health
# Expected: {"status":"healthy"}

# Check running containers
docker-compose ps
```

### 5. Access the Application

Open your browser to: **http://localhost:3000**

You should see the Job Processor Dashboard. Click "Submit New Job" to:
1. Submit a job to the API
2. The API queues it in Redis
3. The worker picks it up and processes it
4. Status updates in real-time on the dashboard

## Common Tasks

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Stop the System
```bash
# Graceful shutdown
docker-compose down

# Remove volumes too (clears all data)
docker-compose down -v
```

### Rebuild Images
```bash
# Remove old images
docker-compose down

# Rebuild from scratch
docker-compose up --build

# Rebuild specific service
docker-compose up --build api
```

### Run API Tests
```bash
# Install test dependencies
pip install -r api/requirements.txt

# Run tests with coverage
cd api
pytest test_main.py -v --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Scale the Worker
```bash
# Run multiple worker instances
docker-compose up --scale worker=3
```

### Monitor Resource Usage
```bash
# View real-time container stats
docker stats

# View specific container
docker stats worker
```

## Environment Variables

All configuration is managed through environment variables. See `.env.example` for complete list.

### Key Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `REDIS_HOST` | redis | Redis server hostname |
| `REDIS_PORT` | 6379 | Redis server port |
| `API_URL` | http://api:8000 | API URL for frontend and worker |
| `PORT` | 3000 | Frontend port |

### Changing Configuration
Edit `.env` file before starting:
```bash
REDIS_HOST=redis
REDIS_PORT=6379
API_URL=http://api:8000
PORT=3000
```

Then restart services:
```bash
docker-compose down
docker-compose up
```

## Health Checks

All services include Docker health checks that verify:
- API: Can reach `/health` endpoint and connect to Redis
- Frontend: Can reach `/health` endpoint
- Worker: Can connect to Redis
- Redis: Can respond to PING command

Services automatically restart if health checks fail.

## Troubleshooting

### "Connection refused" errors

**Problem:** Services can't communicate
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Solution:**
1. Ensure all services are running: `docker-compose ps`
2. Check logs for startup errors: `docker-compose logs`
3. Verify network: `docker network inspect app-network`

### Worker not processing jobs

**Problem:** Jobs stay in "queued" status
```bash
# Check worker logs
docker-compose logs worker

# Verify Redis connection
docker-compose exec worker redis-cli -h redis ping
```

**Solution:**
1. Check worker is running: `docker-compose ps worker`
2. Verify Redis works: `docker-compose exec redis redis-cli ping`
3. Review worker logs for errors

### High memory usage

**Problem:** Containers using too much memory
```bash
# Check current usage
docker stats
```

**Solution:**
1. Check compose file memory limits in `docker-compose.yml`
2. Scale workers appropriately
3. Clear Redis data: `docker-compose down -v`

### Port conflicts

**Problem:** "Port already in use" error
```
Error starting userland proxy: Bind for 0.0.0.0:3000 failed
```

**Solution:**
Change ports in `.env`:
```bash
PORT=3001  # Change from 3000
API_PORT=8001  # Change from 8000
```

## CI/CD Pipeline

The project includes a complete GitHub Actions CI/CD pipeline. See `.github/workflows/ci-cd.yml`.

### Pipeline Stages
1. **Lint** - Code quality checks (flake8, eslint, hadolint)
2. **Test** - Unit tests with coverage (pytest)
3. **Build** - Docker image building and registry push
4. **Security Scan** - Vulnerability scanning with Trivy
5. **Integration Test** - Full stack end-to-end test
6. **Deploy** - Rolling update to production (main branch only)

### Running Pipeline Locally
```bash
# Install GitHub Actions runner
# https://github.com/actions/runner/releases


## Production Deployment

### Prerequisites for Production
- Docker registry (Docker Hub, ECR, GCR, etc.)
- Kubernetes cluster or Docker Swarm
- Load balancer for high availability
- Monitoring stack (Prometheus, Grafana, etc.)
- Log aggregation (ELK, Loki, etc.)

### Deploying to Production

1. **Build and push images:**
```bash
docker build -t myregistry/api:v1.0 ./api
docker build -t myregistry/worker:v1.0 ./worker
docker build -t myregistry/frontend:v1.0 ./frontend

docker push myregistry/api:v1.0
docker push myregistry/worker:v1.0
docker push myregistry/frontend:v1.0
```

2. **Update docker-compose for production:**
```yaml
# Use pulled images instead of building
services:
  api:
    image: myregistry/api:v1.0
  worker:
    image: myregistry/worker:v1.0
  frontend:
    image: myregistry/frontend:v1.0
```

3. **Start services:**
```bash
docker-compose -f docker-compose.yml up -d
```

4. **Verify deployment:**
```bash
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:3000/health
```

### Rolling Updates

For zero-downtime updates:
```bash
# Pull new images
docker-compose pull

# Update services one by one
docker-compose up -d --no-deps --build api
docker-compose up -d --no-deps --build worker
docker-compose up -d --no-deps --build frontend

# Verify system still works
curl http://localhost:3000
```

## Performance Tuning

### Increase Worker Concurrency
```bash
# Start multiple worker instances
docker-compose up --scale worker=5

# Monitor queue depth
docker-compose exec redis redis-cli LLEN job
```

### Optimize Redis
```bash
# Monitor Redis commands
docker-compose exec redis redis-cli MONITOR

# Get Redis stats
docker-compose exec redis redis-cli INFO stats
```

### Check Service Metrics
```bash
# Monitor container resource usage
docker stats --no-stream
```

## Security

### Features Implemented
- ✅ Non-root user execution in all containers
- ✅ Docker health checks
- ✅ Resource limits (CPU, Memory)
- ✅ Internal network isolation
- ✅ No hardcoded credentials
- ✅ Secrets via environment variables
- ✅ Regular vulnerability scanning (Trivy)
- ✅ HTTPS-ready (add reverse proxy as needed)

### Security Hardening
For production, consider:
1. Use a reverse proxy (nginx, traefik) with HTTPS
2. Implement authentication on API endpoints
3. Add rate limiting to prevent abuse
4. Use secrets management (Vault, AWS Secrets Manager)
5. Implement WAF rules
6. Regular security audits and penetration testing

## Monitoring & Logging

### View Logs
```bash
# Follow all logs
docker-compose logs -f

# Filter by service
docker-compose logs -f api
docker-compose logs -f worker
```

### Container Inspection
```bash
# Inspect running container
docker inspect api

# Check container processes
docker top api

# View resource usage
docker stats api
```

### Health Check Status
```bash
# Check health status
docker inspect --format='{{.State.Health}}' api
docker inspect --format='{{.State.Health}}' worker
docker inspect --format='{{.State.Health}}' frontend
```

## Development

### Local Development Setup

**For API (Python):**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r api/requirements.txt

# Run tests
pytest api/test_main.py -v

# Start API server
uvicorn api.main:app --reload
```

**For Frontend (Node.js):**
```bash
# Install dependencies
npm install --prefix frontend

# Start frontend
npm --prefix frontend start
```

**For Worker (Python):**
```bash
# Install dependencies
pip install -r worker/requirements.txt

# Start worker (requires Redis running)
python worker/worker.py
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "Your message"

# Push and create PR
git push origin feature/your-feature

# CI/CD pipeline runs automatically on PR
```

## Documentation Files

- [FIXES.md](FIXES.md) - Complete list of bugs found and fixed
- [.env.example](.env.example) - Environment variable template
- [docker-compose.yml](docker-compose.yml) - Full stack configuration
- [api/Dockerfile](api/Dockerfile) - API service container image
- [worker/Dockerfile](worker/Dockerfile) - Worker service container image
- [frontend/Dockerfile](frontend/Dockerfile) - Frontend service container image

## Support & Contributing

### Reporting Issues
1. Check [FIXES.md](FIXES.md) for known issues
2. Review logs: `docker-compose logs`
3. Open GitHub issue with:
   - Error message and full stack trace
   - Steps to reproduce
   - Environment (OS, Docker version, etc.)

### Contributing
1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

This project is part of the HNG14 Stage 2 DevOps assessment.

## Changelog

### Version 1.0.0 (Initial Release)
- ✅ Multi-service containerization
- ✅ Production-ready Dockerfiles
- ✅ Docker Compose orchestration
- ✅ Health checks on all services
- ✅ Complete CI/CD pipeline
- ✅ Unit tests with coverage
- ✅ Security scanning
- ✅ Integration tests
- ✅ Rolling deployment support
- ✅ Comprehensive documentation
- ✅ 27 bugs fixed from original code

# TruthLens Production Deployment Guide

## Architecture Topology
- **Web App**: Next.js 14+ (Vercel, AWS ECS, or Node container)
- **API Backend**: FastAPI / Uvicorn (Containerized CPU/GPU cluster)
- **Database**: PostgreSQL 15+ (AWS RDS, Cloud SQL, or Neon)
- **Cache**: Redis 7+ (ElastiCache, Upstash, or MemoryDB)

---

## Running with Docker Compose

1. Clone repository and verify environment variables:
   ```bash
   cp .env.example .env
   ```

2. Build and start containers:
   ```bash
   docker compose up --build -d
   ```

3. Verify health:
   ```bash
   curl http://localhost:8000/api/v1/health/ready
   ```

---

## Local Development (Without Docker)

### 1. Backend Service
```bash
python -m venv .venv
# Activate virtual environment
pip install -r requirements.txt
python -m ml.training.train
uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Service
```bash
cd apps/web
npm install
npm run dev
```
Open `http://localhost:3000`.

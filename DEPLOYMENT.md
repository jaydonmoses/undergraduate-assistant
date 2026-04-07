# Undergraduate Assistant - Deployment Guide

A full-stack application that connects undergraduate students with professors based on research interests, built with FastAPI (Python) and React (TypeScript).

## 🚀 Quick Deploy with Docker

### Prerequisites
- Docker and Docker Compose installed
- Git

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd undergraduate-assistant
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file with your settings:
```bash
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=false
UVICORN_WORKERS=1
ENABLE_SCHEDULER=true
SCRAPER_INTERVAL_HOURS=168
SCRAPER_POLL_SECONDS=60
SCRAPER_TOTAL_PAGES=56
SCRAPER_ADMIN_TOKEN=replace-with-a-secret

# Frontend Configuration
REACT_APP_API_URL=http://your-domain.com:8000
# or http://localhost:8000 for local deployment

# CORS Configuration  
ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:3000
```

### 3. Deploy

**Development:**
```bash
docker-compose up --build
```

**Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 4. Access Application
- Frontend: http://localhost:3000 (dev) or http://localhost (prod)
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 🔧 Manual Deployment

### Backend (FastAPI)

1. **Install Dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set Environment Variables:**
```bash
export BACKEND_HOST=0.0.0.0  
export BACKEND_PORT=8000
export DEBUG=false
export ALLOWED_ORIGINS=https://your-frontend-domain.com
```

3. **Run Server:**
```bash
python start_server.py
```

### Frontend (React)

1. **Install Dependencies:**
```bash
cd frontend
npm install
```

2. **Set Environment Variables:**
```bash
export REACT_APP_API_URL=https://your-backend-domain.com
```

3. **Build and Serve:**
```bash
npm run build
# Serve build folder with nginx or any static server
```

---

## ☁️ Cloud Deployment Options

### Option 1: Docker on VPS
1. Deploy to any VPS (DigitalOcean, Linode, AWS EC2)
2. Install Docker and Docker Compose
3. Run production deployment commands above
4. Setup reverse proxy with nginx/Caddy for HTTPS

### Option 2: Platform as a Service

**Backend (Heroku/Railway/Render):**
- Push backend folder
- Set environment variables in platform
- Use `start_server.py` as entry point

**Frontend (Vercel/Netlify):**
- Push frontend folder  
- Set `REACT_APP_API_URL` environment variable
- Deploy with automatic build

### Option 3: Kubernetes
Use provided Docker images with Kubernetes manifests (create separately).

---

## 🔒 Security Considerations

### Production Checklist
- [ ] Set `DEBUG=false` in production
- [ ] Use HTTPS for both frontend and backend  
- [ ] Restrict CORS origins to your domain only
- [ ] Use environment variables for all secrets
- [ ] Regular security updates for dependencies
- [ ] Setup proper database backups
- [ ] Implement rate limiting
- [ ] Add authentication if needed

### Database Security
- SQLite database is stored in `backend/data/` 
- Ensure proper file permissions in production
- Consider upgrading to PostgreSQL for large deployments

---

## 📊 Monitoring and Maintenance

### Weekly Scraper Scheduler
- Scheduler runs inside the backend service, so no second Railway service is required.
- `ENABLE_SCHEDULER=true` enables automatic refreshes.
- `SCRAPER_INTERVAL_HOURS=168` configures weekly refreshes.
- `SCRAPER_POLL_SECONDS=60` controls how often the scheduler checks if a run is due.
- `SCRAPER_TOTAL_PAGES=56` controls scrape breadth (use `1` for smoke tests).
- API status endpoint: `GET /scraper/status`
- Manual trigger endpoint: `POST /scraper/trigger` with `X-Admin-Token` header.

### Health Checks
- Backend: `GET /health`
- Frontend: Standard HTTP check on root path

### Release Smoke Test
Before publishing or after deployment, run:

```bash
cd backend
python smoke_test.py --base-url https://your-api-domain.com
```

For local verification:

```bash
cd backend
python smoke_test.py --base-url http://127.0.0.1:8000
```

### Logs
- Docker logs: `docker-compose logs -f`  
- Application logs are output to stdout/stderr

### Backups
```bash
# Backup SQLite database
docker cp undergraduate-assistant-backend:/app/data/undergraduate_assistant.db ./backup_$(date +%Y%m%d).db
```

### Updates
```bash
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🐛 Troubleshooting

### Common Issues

**CORS Errors:**
- Check `ALLOWED_ORIGINS` environment variable
- Ensure frontend URL is included in CORS origins

**Database Connection:**
- Check `backend/data/` directory has write permissions
- Verify SQLite database file is created

**Environment Variables:**
- Ensure all required env vars are set
- Check `.env` file is in project root

**Container Issues:**
- Check logs: `docker-compose logs backend` or `docker-compose logs frontend`  
- Restart services: `docker-compose restart`

### Support
- API Documentation: `/docs` endpoint
- Health Check: `/health` endpoint
- Container logs for debugging

---

## 📝 Development

### Local Development
```bash  
cp .env.development .env
docker-compose up
```

### Running Tests
```bash
# Backend tests
cd backend  
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Architecture
- **Backend:** FastAPI with SQLite database
- **Frontend:** React with TypeScript  
- **Deployment:** Docker containers with nginx
- **Database:** SQLite (easily upgradable to PostgreSQL)
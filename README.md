# Undergraduate Assistant 🎓

A full-stack application that connects undergraduate students with professors based on research interests. Built with FastAPI (Python) and React (TypeScript).

## ✨ Features

- **Smart Matching**: Connects students with professors based on research interests and skills
- **Easy-to-Use Interface**: Clean React frontend for student information input
- **Professor Database**: Comprehensive professor information with research areas
- **RESTful API**: Well-documented FastAPI backend with automatic OpenAPI documentation
- **Real-time Search**: Find professors by research areas and interests

## 🚀 Quick Start

### Option 1: Docker (Recommended)

**Prerequisites:** Docker and Docker Compose

```bash
# Clone the repository
git clone <your-repo-url>
cd undergraduate-assistant

# Start development environment
./deploy.sh dev
# or on Windows:
deploy.bat dev

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python start_server.py
```

**Frontend:**
```bash
cd frontend  
npm install
npm start
```

## 📁 Project Structure

```
undergraduate-assistant/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   │   └── app.py         # Main FastAPI application
│   ├── database/          # Database management
│   │   └── database.py    # SQLite database handler  
│   ├── scraper/           # Web scraping utilities
│   ├── services/          # Business logic services
│   ├── data/              # SQLite database storage
│   ├── requirements.txt   # Python dependencies
│   ├── start_server.py    # Server startup script
│   └── Dockerfile         # Backend container config
│
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API communication  
│   │   └── types/         # TypeScript interfaces
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   ├── Dockerfile         # Frontend container config
│   └── nginx.conf         # Production web server config
│
├── docker-compose.yml      # Development deployment
├── docker-compose.prod.yml # Production deployment  
├── .env.example           # Environment template
├── .env.development       # Development config
├── deploy.sh              # Deployment script (Linux/Mac)
├── deploy.bat             # Deployment script (Windows)
└── DEPLOYMENT.md          # Detailed deployment guide
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/` | API information and available endpoints |
| GET    | `/health` | Health check for monitoring |
| GET    | `/research-areas` | Get all available research areas |
| POST   | `/user_info` | Create or update user information |
| GET    | `/user_info/{user_id}` | Get user information by ID |  
| POST   | `/prof_info` | Get professor recommendations |
| GET    | `/professors` | Get all professors |
| GET    | `/professors/search` | Search professors by research area |

## 🌐 Deployment

### Development
```bash
./deploy.sh dev
```

### Production
```bash
./deploy.sh prod
```

### Cloud Platforms

**Backend Deployment:**
- Heroku, Railway, Render: Deploy backend folder directly
- AWS, GCP, Azure: Use Docker containers
- Set environment variables for configuration

**Frontend Deployment:**  
- Vercel, Netlify: Deploy frontend folder
- Set `REACT_APP_API_URL` to your backend URL
- Automatic builds from Git repositories

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🔒 Environment Configuration

Create `.env` file from template:
```bash
cp .env.example .env
```

Key configuration options:
```bash
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=false

# Frontend  
REACT_APP_API_URL=http://localhost:8000

# Security
ALLOWED_ORIGINS=https://your-domain.com
```

## 🛠️ Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt

# Run with auto-reload
python start_server.py
```

### Frontend Development
```bash
cd frontend
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

### Database
- Uses SQLite for simplicity and portability
- Database file: `backend/data/undergraduate_assistant.db`
- Automatic database initialization on first run
- Easy to backup and migrate

## 📊 Monitoring

### Health Checks
- Backend: `GET /health`
- Returns database connectivity status
- Used by load balancers and monitoring systems

### Logs  
```bash
# Docker logs
docker-compose logs -f

# Specific service logs
./deploy.sh logs backend
./deploy.sh logs frontend
```

### Database Backup
```bash
./deploy.sh backup
```

## 🐛 Troubleshooting

### Common Issues

**CORS Errors:**
- Verify `ALLOWED_ORIGINS` includes your frontend URL
- Check environment variable configuration

**Database Issues:**
- Ensure `backend/data/` directory has write permissions
- Check SQLite database file creation

**Container Issues:**
- Check Docker logs: `docker-compose logs [service]`
- Verify environment variables are set correctly
- Restart services: `./deploy.sh stop && ./deploy.sh dev`

### Getting Help
- Check API documentation at `/docs`
- Use health check endpoint at `/health` 
- Review container logs for error details

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest
```

### Frontend Tests
```bash
cd frontend  
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Links

- [Deployment Guide](DEPLOYMENT.md) - Comprehensive deployment documentation
- API Documentation - Available at `/docs` when server is running
- Health Check - Available at `/health` for monitoring
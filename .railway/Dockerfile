# Multi-stage build for complete application
# Build React frontend
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/src ./src
COPY frontend/public ./public  
COPY frontend/tsconfig.json ./

# Build with API URL pointing to backend on same host
ENV REACT_APP_API_URL=http://localhost:8000
RUN npm run build

# Python backend with frontend served statically
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend ./backend

# Copy built frontend to be served by backend
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Create data directory for database
RUN mkdir -p backend/data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "backend/start_server.py"]

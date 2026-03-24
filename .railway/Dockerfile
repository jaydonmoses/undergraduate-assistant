# Multi-stage build for Railway deployment
# Stage 1: Build React frontend
FROM node:18-alpine as frontend-build

WORKDIR /app

# Copy entire frontend directory
COPY frontend ./frontend

WORKDIR /app/frontend

# Install dependencies
RUN npm ci

# Build React app
ENV REACT_APP_API_URL=http://localhost:8000
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend ./backend

# Copy built frontend from first stage
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Create data directory for database
RUN mkdir -p backend/data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "backend/start_server.py"]

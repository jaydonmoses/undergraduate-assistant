# Multi-stage build for complete application
# Stage 1: Build React frontend
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/tsconfig.json ./

# Build frontend - API URL will be determined at runtime by the frontend
ENV REACT_APP_API_URL=http://localhost:8000
RUN npm run build

# Stage 2: Final image with Python backend and built frontend
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

# Copy startup script
COPY backend/start_server.py .

# Create data directory for database
RUN mkdir -p backend/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set working directory
WORKDIR /app

# Run backend server
CMD ["python", "backend/start_server.py"]

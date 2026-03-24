#!/bin/bash

# Undergraduate Assistant Deployment Script
# This script helps deploy the application in different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Environment setup
setup_env() {
    if [ ! -f ".env" ]; then
        log_info "Creating .env file from template..."
        
        if [ "$1" = "production" ]; then
            cp .env.example .env
        else
            cp .env.development .env
        fi
        
        log_warn "Please edit the .env file with your configuration before continuing."
        read -p "Press Enter to continue after editing .env file..."
    else
        log_info ".env file already exists."
    fi
}

# Development deployment
deploy_dev() {
    log_info "Starting development deployment..."
    setup_env "development"
    
    log_info "Building and starting containers..."
    docker-compose up --build
}

# Production deployment
deploy_prod() {
    log_info "Starting production deployment..."
    setup_env "production"
    
    log_info "Building and starting containers in production mode..."
    docker-compose -f docker-compose.prod.yml up -d --build
    
    log_info "Deployment complete!"
    log_info "Frontend: http://localhost"
    log_info "Backend API: http://localhost:8000"
    log_info "API Documentation: http://localhost:8000/docs"
    log_info "Health Check: http://localhost:8000/health"
}

# Stop all services
stop_services() {
    log_info "Stopping all services..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    log_info "All services stopped."
}

# Clean up Docker artifacts
cleanup() {
    log_warn "This will remove all stopped containers, unused networks, and dangling images."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up Docker resources..."
        docker system prune -f
        log_info "Cleanup complete."
    else
        log_info "Cleanup cancelled."
    fi
}

# Backup database
backup_db() {
    log_info "Creating database backup..."
    timestamp=$(date +"%Y%m%d_%H%M%S")
    
    if docker ps --format '{{.Names}}' | grep -q "undergraduate-assistant-backend"; then
        docker cp undergraduate-assistant-backend:/app/data/undergraduate_assistant.db "./backup_${timestamp}.db"
        log_info "Database backup created: backup_${timestamp}.db"
    else
        log_error "Backend container is not running. Cannot create backup."
        exit 1
    fi
}

# Show logs
show_logs() {
    if [ "$1" = "backend" ]; then
        docker-compose logs -f backend
    elif [ "$1" = "frontend" ]; then
        docker-compose logs -f frontend  
    else
        docker-compose logs -f
    fi
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Check backend
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✅ Backend is healthy"
    else
        log_error "❌ Backend is not responding"
    fi
    
    # Check frontend
    if curl -f http://localhost > /dev/null 2>&1; then
        log_info "✅ Frontend is accessible"
    else
        log_error "❌ Frontend is not responding"
    fi
}

# Main script
main() {
    check_docker
    
    case "$1" in
        "dev")
            deploy_dev
            ;;
        "prod")
            deploy_prod
            ;;
        "stop")
            stop_services
            ;;
        "cleanup")
            cleanup
            ;;
        "backup")
            backup_db
            ;;
        "logs")
            show_logs "$2"
            ;;
        "health")
            health_check
            ;;
        *)
            echo "Usage: $0 {dev|prod|stop|cleanup|backup|logs|health}"
            echo ""
            echo "Commands:"
            echo "  dev      - Start development environment"
            echo "  prod     - Start production environment"
            echo "  stop     - Stop all services"
            echo "  cleanup  - Clean up Docker resources"
            echo "  backup   - Backup database"
            echo "  logs     - Show logs (optional: backend|frontend)"
            echo "  health   - Check service health"
            exit 1
            ;;
    esac
}

main "$@"
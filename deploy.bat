@echo off
REM Undergraduate Assistant Deployment Script for Windows
REM This script helps deploy the application in different environments

setlocal EnableDelayedExpansion

REM Check if Docker is installed
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

where docker-compose >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Environment setup
:setup_env
if not exist ".env" (
    echo [INFO] Creating .env file from template...
    
    if "%1"=="production" (
        copy .env.example .env
    ) else (
        copy .env.development .env
    )
    
    echo [WARN] Please edit the .env file with your configuration before continuing.
    pause
) else (
    echo [INFO] .env file already exists.
)
goto :eof

REM Development deployment
:deploy_dev
echo [INFO] Starting development deployment...
call :setup_env development

echo [INFO] Building and starting containers...
docker-compose up --build
goto :eof

REM Production deployment  
:deploy_prod
echo [INFO] Starting production deployment...
call :setup_env production

echo [INFO] Building and starting containers in production mode...
docker-compose -f docker-compose.prod.yml up -d --build

echo [INFO] Deployment complete!
echo [INFO] Frontend: http://localhost
echo [INFO] Backend API: http://localhost:8000
echo [INFO] API Documentation: http://localhost:8000/docs
echo [INFO] Health Check: http://localhost:8000/health
goto :eof

REM Stop all services
:stop_services
echo [INFO] Stopping all services...
docker-compose down
docker-compose -f docker-compose.prod.yml down
echo [INFO] All services stopped.
goto :eof

REM Clean up Docker artifacts
:cleanup
echo [WARN] This will remove all stopped containers, unused networks, and dangling images.
set /p choice="Are you sure? (y/N): "
if /i "!choice!"=="y" (
    echo [INFO] Cleaning up Docker resources...
    docker system prune -f
    echo [INFO] Cleanup complete.
) else (
    echo [INFO] Cleanup cancelled.
)
goto :eof

REM Backup database
:backup_db
echo [INFO] Creating database backup...

for /f "tokens=*" %%i in ('docker ps --format "{{.Names}}"') do (
    echo %%i | findstr /c:"undergraduate-assistant-backend" >nul
    if !errorlevel! equ 0 (
        set backend_running=1
    )
)

if defined backend_running (
    for /f "tokens=2 delims= " %%i in ('date /t') do set date_part=%%i
    for /f "tokens=1 delims= " %%i in ('time /t') do set time_part=%%i
    set timestamp=!date_part:/=!!time_part::=!
    set timestamp=!timestamp: =!
    
    docker cp undergraduate-assistant-backend:/app/data/undergraduate_assistant.db "backup_!timestamp!.db"
    echo [INFO] Database backup created: backup_!timestamp!.db
) else (
    echo [ERROR] Backend container is not running. Cannot create backup.
    exit /b 1
)
goto :eof

REM Show logs
:show_logs
if "%2"=="backend" (
    docker-compose logs -f backend
) else if "%2"=="frontend" (
    docker-compose logs -f frontend
) else (
    docker-compose logs -f
)
goto :eof

REM Health check
:health_check
echo [INFO] Performing health check...

curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] ✅ Backend is healthy
) else (
    echo [ERROR] ❌ Backend is not responding
)

curl -f http://localhost >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] ✅ Frontend is accessible
) else (
    echo [ERROR] ❌ Frontend is not responding
)
goto :eof

REM Main script logic
if "%1"=="dev" (
    call :deploy_dev
) else if "%1"=="prod" (
    call :deploy_prod
) else if "%1"=="stop" (
    call :stop_services
) else if "%1"=="cleanup" (
    call :cleanup
) else if "%1"=="backup" (
    call :backup_db
) else if "%1"=="logs" (
    call :show_logs %1 %2
) else if "%1"=="health" (
    call :health_check
) else (
    echo Usage: %0 {dev^|prod^|stop^|cleanup^|backup^|logs^|health}
    echo.
    echo Commands:
    echo   dev      - Start development environment
    echo   prod     - Start production environment
    echo   stop     - Stop all services
    echo   cleanup  - Clean up Docker resources
    echo   backup   - Backup database
    echo   logs     - Show logs ^(optional: backend^|frontend^)
    echo   health   - Check service health
)
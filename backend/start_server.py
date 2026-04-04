"""
Production-ready startup script for the FastAPI server
"""
import sys
import os
from decouple import config

if __name__ == "__main__":
    # Resolve the backend/api layout for both direct execution and Docker images.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.isdir(os.path.join(current_dir, "api")):
        backend_dir = current_dir
    elif os.path.isdir(os.path.join(current_dir, "backend", "api")):
        backend_dir = os.path.join(current_dir, "backend")
    else:
        backend_dir = current_dir

    api_dir = os.path.join(backend_dir, "api")

    if not os.path.isdir(api_dir):
        raise FileNotFoundError(f"Unable to locate API directory at {api_dir}")
    
    sys.path.insert(0, backend_dir)
    sys.path.insert(0, api_dir)
    
    # Configuration from environment variables
    host = config("BACKEND_HOST", default="0.0.0.0")
    port = config("BACKEND_PORT", default=8000, cast=int)
    debug = config("DEBUG", default=False, cast=bool)
    workers = config("UVICORN_WORKERS", default=1, cast=int)
    
    print("🚀 Starting Undergraduate Assistant API...")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    print(f"🔄 Interactive API: http://{host}:{port}/redoc")
    print(f"🏥 Health Check: http://{host}:{port}/health")
    
    import uvicorn
    
    # Change working directory to api so uvicorn can import app:app reliably.
    os.chdir(api_dir)
    
    # Start the server with production-ready settings
    uvicorn.run(
        "app:app", 
        host=host, 
        port=port, 
        reload=debug,
        workers=1 if debug else workers,
        log_level="info"
    )
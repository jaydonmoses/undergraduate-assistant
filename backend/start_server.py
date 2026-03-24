"""
Production-ready startup script for the FastAPI server
"""
import sys
import os
from decouple import config

if __name__ == "__main__":
    # Add the backend directory and api directory to Python path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    api_dir = os.path.join(backend_dir, "api")
    
    sys.path.insert(0, backend_dir)
    sys.path.insert(0, api_dir)
    
    # Configuration from environment variables
    host = config("BACKEND_HOST", default="127.0.0.1")
    port = config("BACKEND_PORT", default=8000, cast=int)
    debug = config("DEBUG", default=True, cast=bool)
    
    print("🚀 Starting Undergraduate Assistant API...")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    print(f"🔄 Interactive API: http://{host}:{port}/redoc")
    print(f"🏥 Health Check: http://{host}:{port}/health")
    
    import uvicorn
    
    # Change working directory to api
    os.chdir(api_dir)
    
    # Start the server with production-ready settings
    uvicorn.run(
        "app:app", 
        host=host, 
        port=port, 
        reload=debug,
        workers=1 if debug else 4,
        log_level="info"
    )
"""
Simple startup script for the FastAPI server
"""
import sys
import os

if __name__ == "__main__":
    # Add the backend directory and api directory to Python path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    api_dir = os.path.join(backend_dir, "api")
    
    sys.path.insert(0, backend_dir)
    sys.path.insert(0, api_dir)
    
    print("🚀 Starting Undergraduate Assistant API...")
    print("📖 API Documentation: http://127.0.0.1:8000/docs")
    print("🔄 Interactive API: http://127.0.0.1:8000/redoc")
    
    import uvicorn
    
    # Change working directory to api
    os.chdir(api_dir)
    
    # Start the server
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
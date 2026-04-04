from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import sys
import os
from decouple import config

# Add the parent directory to the path to import our database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import UndergraduateAssistantDatabase
from services.scheduler import start_scheduler, stop_scheduler, get_scheduler_status, run_weekly_scrape


@asynccontextmanager
async def lifespan(_: FastAPI):
    start_scheduler()
    try:
        yield
    finally:
        stop_scheduler()

app = FastAPI(
    title="Undergraduate Assistant API",
    description="API for connecting undergraduate students with professors based on research interests",
    version="1.0.0",
    lifespan=lifespan,
)

# Get CORS origins from environment variable.
raw_allowed_origins = config(
    "ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000,http://0.0.0.0:3000",
)
allowed_origins = [origin.strip() for origin in raw_allowed_origins.split(",") if origin.strip()]
allow_origin_regex = config("ALLOWED_ORIGIN_REGEX", default="")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex if allow_origin_regex else None,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize database
db = UndergraduateAssistantDatabase()

# Pydantic models for request/response
class UserInfo(BaseModel):
    name: str
    major: str
    research_interests: List[str]
    skills: List[str]

class UserResponse(BaseModel):
    user_id: int
    name: str
    major: str
    research_interests: List[str]
    skills: List[str]

class ProfessorInfo(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    position: Optional[str] = None
    research_interests: List[str] = []
    location: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    personal_website: Optional[str] = None
    google_scholar: Optional[str] = None

# TODO: Replace logic with agentic flow
'''
DESCRIPTION:
    Agentic flow should match user research interests, skills, and major with professors
    in similar research fields of labs. Mapping should be broad and interdisciplinary when possible.
Input:
    user_info: UserInfo (not including id) [
        Skills
        Research Interests
        Major
        Notes (Add text box and implement in the DB later)
    ]   

    professors: List[ProfessorInfo] (all professors from DB) [
        EVERYTHING in ProfessorInfo
    ]

Output:
    recommendations: List[ProfessorInfo] (filtered and ranked professors by relevancy)
    Short blurb from model on why each professor is a good match (optional, based on less "direct" matches)

Workflow:
    TODO: Summarize workflow here

Work:
    1. Create logic flow in dify
    2. Dockerize dify agent and containerize
    3. Hook into Docker here

'''
class ProfessorRecommendationRequest(BaseModel):
    user_info: UserInfo

class ProfessorRecommendationResponse(BaseModel):
    recommendations: List[ProfessorInfo]
    match_count: int

@app.get("/")
async def root():
    """Serve React app or API info"""
    # Check if frontend build exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    app_root = os.path.dirname(backend_dir)
    frontend_build_path = os.path.join(app_root, "frontend", "build")
    index_file = os.path.join(frontend_build_path, "index.html")
    
    print(f"DEBUG: Looking for frontend at: {frontend_build_path}")
    print(f"DEBUG: Index file path: {index_file}")
    print(f"DEBUG: Index file exists: {os.path.exists(index_file)}")
    
    if os.path.exists(index_file):
        print("DEBUG: Serving React frontend")
        return FileResponse(index_file)
    
    # Fall back to API info
    print("DEBUG: Serving API info (frontend not found)")
    return {
        "message": "Welcome to the Undergraduate Assistant API",
        "endpoints": {
            "GET /user_info/{user_id}": "Get user information",
            "POST /user_info": "Create or update user information", 
            "POST /prof_info": "Get professor recommendations based on user interests",
            "GET /professors": "Get all professors",
            "GET /professors/search": "Search professors by research area",
            "GET /research-areas": "Get all available research areas",
            "GET /health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    try:
        # Test database connection
        db.get_database_stats()
        return {
            "status": "healthy",
            "message": "API is running and database is accessible",
            "version": "1.0.0",
            "scraper": {
                "status": db.get_metadata("scraper_status"),
                "last_success_at": db.get_metadata("scraper_last_success_at"),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/scraper/status")
async def scraper_status():
    """Get scheduler and scraper execution status."""
    return get_scheduler_status()


@app.post("/scraper/trigger")
async def trigger_scraper(
    background_tasks: BackgroundTasks,
    x_admin_token: Optional[str] = Header(default=None),
):
    """Trigger an on-demand scrape with admin token protection."""
    expected_token = config("SCRAPER_ADMIN_TOKEN", default="")

    if not expected_token:
        raise HTTPException(
            status_code=503,
            detail="Manual trigger is disabled. Set SCRAPER_ADMIN_TOKEN to enable.",
        )

    if x_admin_token != expected_token:
        raise HTTPException(status_code=403, detail="Forbidden")

    if db.get_metadata("scraper_status") == "running":
        return {"status": "ignored", "message": "Scraper is already running"}

    background_tasks.add_task(run_weekly_scrape)
    return {"status": "accepted", "message": "Scraper run has been queued"}

@app.get("/research-areas")
async def get_research_areas():
    """Get all available research areas for dropdown/autocomplete"""
    try:
        # Import here to avoid circular imports
        from scraper.webscrapper import get_research_info
        
        base_url = "https://www.khoury.northeastern.edu/people/"
        research_areas = get_research_info(base_url)
        
        return {
            "research_areas": sorted(research_areas),  # Sort alphabetically
            "count": len(research_areas)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching research areas: {str(e)}")

@app.get("/user_info/{user_id}", response_model=UserResponse)
async def get_user_info(user_id: int):
    """Get user information by ID"""
    try:
        user = db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            user_id=user['id'],
            name=user['name'],
            major=user['major'],
            research_interests=user['research_interests'],
            skills=user['skills']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/user_info", response_model=UserResponse)
async def create_or_update_user_info(user_info: UserInfo):
    """Create or update user information"""
    try:
        # Check if user already exists
        existing_users = db.search_users(name=user_info.name)
        
        if existing_users:
            # Update existing user
            user_id = existing_users[0]['id']
            user_data = {
                'name': user_info.name,
                'major': user_info.major,
                'research_interests': user_info.research_interests,
                'skills': user_info.skills
            }
            db.update_user(user_id=user_id, user_data=user_data)
        else:
            # Create new user
            user_id = db.insert_user(
                name=user_info.name,
                major=user_info.major,
                research_interests=user_info.research_interests,
                skills=user_info.skills
            )
        
        return UserResponse(
            user_id=user_id,
            name=user_info.name,
            major=user_info.major,
            research_interests=user_info.research_interests,
            skills=user_info.skills
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/prof_info", response_model=ProfessorRecommendationResponse)
async def get_professor_recommendations(request: ProfessorRecommendationRequest):
    """Save user info to database and return all professors (not filtered)"""
    try:
        # First, save the user information to the database
        user_info = request.user_info
        
        # Check if user already exists
        existing_users = db.search_users(name=user_info.name)
        
        if existing_users:
            # Update existing user
            user_id = existing_users[0]['id']
            user_data = {
                'name': user_info.name,
                'major': user_info.major,
                'research_interests': user_info.research_interests,
                'skills': user_info.skills
            }
            db.update_user(user_id=user_id, user_data=user_data)
        else:
            # Create new user
            user_data = {
                'name': user_info.name,
                'major': user_info.major,
                'research_interests': user_info.research_interests,
                'skills': user_info.skills
            }
            user_id = db.insert_user(user_data)
        
        # Get ALL professors (not filtered by research interests)
        professors = db.get_all_professors()
        
        # Convert to ProfessorInfo objects
        recommendations = []
        for prof in professors:
            recommendations.append(ProfessorInfo(
                name=prof.get('name', ''),
                title=prof.get('title', ''),
                position=prof.get('position', ''),
                research_interests=prof.get('research_interests', []),
                location=prof.get('location', ''),
                email=prof.get('email', ''),
                phone=prof.get('phone', ''),
                personal_website=prof.get('personal_website', ''),
                google_scholar=prof.get('google_scholar', '')
            ))
        
        return ProfessorRecommendationResponse(
            recommendations=recommendations,
            match_count=len(recommendations)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@app.get("/professors", response_model=List[ProfessorInfo])
async def get_all_professors(limit: Optional[int] = 50, offset: Optional[int] = 0):
    """Get all professors with pagination"""
    try:
        professors = db.get_all_professors()
        
        # Apply pagination manually since the DB method doesn't support it yet
        paginated_professors = professors[offset:offset + limit] if limit else professors[offset:]
        
        return [
            ProfessorInfo(
                name=prof['name'],
                title=prof['title'],
                position=prof['position'],
                research_interests=prof['research_interests'],
                location=prof['location'],
                email=prof['email'],
                phone=prof['phone'],
                personal_website=prof['personal_website'],
                google_scholar=prof['google_scholar']
            )
            for prof in paginated_professors
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/professors/search", response_model=List[ProfessorInfo])
async def search_professors(
    research_area: Optional[str] = None,
    location: Optional[str] = None,
    name: Optional[str] = None
):
    """Search professors by various criteria"""
    try:
        professors = db.search_professors(
            name=name,
            research_area=research_area,
            location=location
        )
        
        return [
            ProfessorInfo(
                name=prof['name'],
                title=prof['title'],
                position=prof['position'],
                research_interests=prof['research_interests'],
                location=prof['location'],
                email=prof['email'],
                phone=prof['phone'],
                personal_website=prof['personal_website'],
                google_scholar=prof['google_scholar']
            )
            for prof in professors
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching professors: {str(e)}")


# Mount static files (React build)
current_file_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_file_dir)
app_root = os.path.dirname(backend_dir)
frontend_build_path = os.path.join(app_root, "frontend", "build")

print(f"Framework initialization: Looking for frontend at {frontend_build_path}")

if os.path.exists(frontend_build_path):
    # Mount the static directory for CSS, JS, etc.
    static_path = os.path.join(frontend_build_path, "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
        print("Debug: Static files mounted successfully")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React app for client-side routing"""
        # Don't intercept API routes or Swagger docs
        if any(full_path.startswith(prefix) for prefix in ["api", "docs", "redoc", "openapi", "static"]):
            raise HTTPException(status_code=404, detail="Not found")
        
        index_file = os.path.join(frontend_build_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        
        raise HTTPException(status_code=404, detail="Not found")
else:
    print(f"WARNING: Frontend build not found at {frontend_build_path}")
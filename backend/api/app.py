from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Add the parent directory to the path to import our database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import UndergraduateAssistantDatabase

app = FastAPI(
    title="Undergraduate Assistant API",
    description="API for connecting undergraduate students with professors based on research interests",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
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
    return {
        "message": "Welcome to the Undergraduate Assistant API",
        "endpoints": {
            "GET /user_info/{user_id}": "Get user information",
            "POST /user_info": "Create or update user information", 
            "POST /prof_info": "Get professor recommendations based on user interests",
            "GET /professors": "Get all professors",
            "GET /professors/search": "Search professors by research area",
            "GET /research-areas": "Get all available research areas"
        }
    }

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
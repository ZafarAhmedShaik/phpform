from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import hashlib
import csv
import io
from fastapi.responses import StreamingResponse


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Admin credentials (in production, use proper auth system)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # In production, hash this!

# Helper function to hash passwords
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Helper function to prepare data for MongoDB
def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

# Models
class ClientSubmission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=20)
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClientSubmissionCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone_number: str = Field(..., min_length=12, max_length=15, regex=r'^\+1-\d{3}-\d{3}-\d{4}$')

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    message: str

# Simple token verification (in production, use JWT)
async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    expected_token = hash_password(f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}")
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return credentials.credentials

# Routes
@api_router.get("/")
async def root():
    return {"message": "Client Form Management System API"}

# Client submission routes
@api_router.post("/clients", response_model=ClientSubmission)
async def submit_client_data(client_data: ClientSubmissionCreate):
    """Submit new client data"""
    try:
        # Check if email already exists
        existing_client = await db.clients.find_one({"email": client_data.email})
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already registered"
            )
        
        # Create client submission
        submission = ClientSubmission(**client_data.dict())
        submission_dict = prepare_for_mongo(submission.dict())
        
        # Insert into database
        await db.clients.insert_one(submission_dict)
        
        return submission
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit client data"
        )

# Admin authentication
@api_router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(login_data: AdminLogin):
    """Admin login endpoint"""
    if login_data.username != ADMIN_USERNAME or login_data.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Generate simple token (in production, use JWT)
    token = hash_password(f"{login_data.username}:{login_data.password}")
    
    return AdminLoginResponse(
        access_token=token,
        message="Login successful"
    )

# Admin routes (protected)
@api_router.get("/admin/clients", response_model=List[ClientSubmission])
async def get_all_clients(token: str = Depends(verify_admin_token)):
    """Get all client submissions (admin only)"""
    try:
        clients = await db.clients.find().sort("submitted_at", -1).to_list(1000)
        return [ClientSubmission(**client) for client in clients]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client data"
        )

@api_router.get("/admin/clients/export")
async def export_clients_csv(token: str = Depends(verify_admin_token)):
    """Export all client data as CSV (admin only)"""
    try:
        clients = await db.clients.find().sort("submitted_at", -1).to_list(1000)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Full Name', 'Email', 'Phone Number', 'Submitted At'])
        
        # Write data
        for client in clients:
            writer.writerow([
                client.get('id', ''),
                client.get('full_name', ''),
                client.get('email', ''),
                client.get('phone_number', ''),
                client.get('submitted_at', '')
            ])
        
        output.seek(0)
        
        # Return as streaming response
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=client_submissions.csv"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export client data"
        )

@api_router.get("/admin/stats")
async def get_admin_stats(token: str = Depends(verify_admin_token)):
    """Get admin dashboard statistics"""
    try:
        total_clients = await db.clients.count_documents({})
        
        # Get recent submissions (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc).replace(day=1)  # Simple monthly count
        recent_count = await db.clients.count_documents({
            "submitted_at": {"$gte": thirty_days_ago.isoformat()}
        })
        
        return {
            "total_clients": total_clients,
            "recent_submissions": recent_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

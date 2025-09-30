# Shared utilities for Vercel serverless functions
from motor.motor_asyncio import AsyncIOMotorClient
import os
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional
import re

# MongoDB connection (connection reuse for serverless)
_client = None
_db = None

def get_database():
    global _client, _db
    if _client is None:
        mongo_url = os.environ.get('MONGO_URL')
        if not mongo_url:
            raise ValueError("MONGO_URL environment variable not set")
        _client = AsyncIOMotorClient(mongo_url)
        _db = _client[os.environ.get('DB_NAME', 'client_form_db')]
    return _db

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def prepare_for_mongo(data):
    """Helper function to prepare data for MongoDB"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, dict):
                prepare_for_mongo(value)
    return data

def validate_email(email: str) -> bool:
    """Enhanced email validation"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number in +1-XXX-XXX-XXXX format"""
    phone_pattern = r'^\+1-\d{3}-\d{3}-\d{4}$'
    return bool(re.match(phone_pattern, phone))

def format_phone(phone: str) -> str:
    """Format phone number to +1-XXX-XXX-XXXX"""
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Handle different input formats
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]  # Remove leading 1
    elif len(digits) == 10:
        pass  # Perfect length
    else:
        return phone  # Return original if can't format
    
    # Format to +1-XXX-XXX-XXXX
    return f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"

async def verify_token(token: str) -> bool:
    """Verify admin token"""
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    expected_token = hash_password(f"{admin_username}:{admin_password}")
    return token == expected_token

def cors_response(data, status_code=200):
    """Helper to create CORS-enabled response"""
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Content-Type": "application/json"
        },
        "body": json.dumps(data) if isinstance(data, (dict, list)) else data
    }
# Admin login endpoint
from utils import hash_password, cors_response
import json
import os

async def handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return cors_response({}, 200)
    
    if event.get('httpMethod') != 'POST':
        return cors_response({"error": "Method not allowed"}, 405)
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        username = body.get('username', '').strip()
        password = body.get('password', '').strip()
        
        if not username or not password:
            return cors_response({"error": "Username and password are required"}, 400)
        
        # Get admin credentials from environment
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        # Verify credentials
        if username != admin_username or password != admin_password:
            return cors_response({"error": "Invalid credentials"}, 401)
        
        # Generate token (in production, use JWT)
        token = hash_password(f"{admin_username}:{admin_password}")
        
        return cors_response({
            "message": "Login successful",
            "access_token": token
        }, 200)
        
    except Exception as e:
        return cors_response({"error": f"Internal server error: {str(e)}"}, 500)
# Client form submission endpoint
from utils import get_database, validate_email, validate_phone, format_phone, prepare_for_mongo, cors_response
import json
import uuid
from datetime import datetime, timezone

async def handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return cors_response({}, 200)
    
    if event.get('httpMethod') != 'POST':
        return cors_response({"error": "Method not allowed"}, 405)
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        full_name = body.get('full_name', '').strip()
        email = body.get('email', '').strip().lower()
        phone_number = body.get('phone_number', '').strip()
        
        # Validation
        if len(full_name) < 2:
            return cors_response({"error": "Full name must be at least 2 characters long"}, 400)
        
        if not validate_email(email):
            return cors_response({"error": "Please enter a valid email address"}, 400)
        
        # Format phone number
        formatted_phone = format_phone(phone_number)
        if not validate_phone(formatted_phone):
            return cors_response({"error": "Phone number must be in format: +1-XXX-XXX-XXXX"}, 400)
        
        # Connect to database
        db = get_database()
        clients_collection = db.clients
        
        # Check for duplicate email
        existing_client = await clients_collection.find_one({"email": email})
        if existing_client:
            return cors_response({"error": "A client with this email already exists"}, 409)
        
        # Create client record
        client_data = {
            "id": str(uuid.uuid4()),
            "full_name": full_name,
            "email": email,
            "phone_number": formatted_phone,
            "submitted_at": datetime.now(timezone.utc)
        }
        
        # Prepare for MongoDB and insert
        prepared_data = prepare_for_mongo(client_data.copy())
        result = await clients_collection.insert_one(prepared_data)
        
        return cors_response({
            "message": "Client information submitted successfully",
            "client_id": client_data["id"]
        }, 201)
        
    except Exception as e:
        return cors_response({"error": f"Internal server error: {str(e)}"}, 500)
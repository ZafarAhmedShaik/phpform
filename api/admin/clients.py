# Admin clients retrieval endpoint
from utils import get_database, verify_token, cors_response
import json

async def handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return cors_response({}, 200)
    
    if event.get('httpMethod') != 'GET':
        return cors_response({"error": "Method not allowed"}, 405)
    
    try:
        # Check authorization
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization') or headers.get('authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return cors_response({"error": "Missing or invalid authorization header"}, 403)
        
        token = auth_header.split(' ')[1]
        if not await verify_token(token):
            return cors_response({"error": "Invalid or expired token"}, 403)
        
        # Connect to database
        db = get_database()
        clients_collection = db.clients
        
        # Retrieve all clients
        clients_cursor = clients_collection.find({})
        clients = await clients_cursor.to_list(length=None)
        
        # Convert ObjectId to string and format response
        formatted_clients = []
        for client in clients:
            if '_id' in client:
                del client['_id']  # Remove MongoDB ObjectId
            
            # Ensure consistent format
            formatted_client = {
                "id": client.get("id"),
                "full_name": client.get("full_name"),
                "email": client.get("email"),
                "phone_number": client.get("phone_number"),
                "submitted_at": client.get("submitted_at")
            }
            formatted_clients.append(formatted_client)
        
        return cors_response(formatted_clients, 200)
        
    except Exception as e:
        return cors_response({"error": f"Internal server error: {str(e)}"}, 500)
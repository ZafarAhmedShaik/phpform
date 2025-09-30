# Admin stats endpoint
from utils import get_database, verify_token, cors_response
from datetime import datetime, timezone, timedelta

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
        
        # Get total clients count
        total_clients = await clients_collection.count_documents({})
        
        # Get recent submissions (last 7 days)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_filter = {"submitted_at": {"$gte": seven_days_ago.isoformat()}}
        recent_submissions = await clients_collection.count_documents(recent_filter)
        
        stats = {
            "total_clients": int(total_clients),
            "recent_submissions": int(recent_submissions)
        }
        
        return cors_response(stats, 200)
        
    except Exception as e:
        return cors_response({"error": f"Internal server error: {str(e)}"}, 500)
# Admin CSV export endpoint  
from utils import get_database, verify_token, cors_response
import csv
import io

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
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Full Name', 'Email', 'Phone Number', 'Submitted At'])
        
        # Write data rows
        for client in clients:
            writer.writerow([
                client.get('id', ''),
                client.get('full_name', ''),
                client.get('email', ''),
                client.get('phone_number', ''),
                client.get('submitted_at', '')
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # Return CSV response
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Content-Type": "text/csv",
                "Content-Disposition": "attachment; filename=client_submissions.csv"
            },
            "body": csv_content
        }
        
    except Exception as e:
        return cors_response({"error": f"Internal server error: {str(e)}"}, 500)
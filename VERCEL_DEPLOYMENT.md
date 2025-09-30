# Vercel Deployment Guide

## Overview
Your FastAPI backend has been converted to Vercel serverless functions. Here's how to deploy:

## Project Structure (Updated)
```
/app/
├── api/                     # Vercel serverless functions
│   ├── utils.py            # Shared utilities
│   ├── clients.py          # POST /api/clients
│   └── admin/
│       ├── login.py        # POST /api/admin/login
│       ├── clients.py      # GET /api/admin/clients
│       ├── export.py       # GET /api/admin/clients/export
│       └── stats.py        # GET /api/admin/stats
├── frontend/               # React app
├── vercel.json            # Vercel configuration
├── requirements.txt       # Python dependencies
└── package.json          # Node.js configuration
```

## Deployment Steps

### 1. Environment Variables in Vercel Dashboard
After deploying, add these environment variables in Vercel dashboard:

```
MONGO_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/
DB_NAME=client_form_db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
CORS_ORIGINS=https://your-app.vercel.app
```

### 2. Database Setup
- Use MongoDB Atlas (free tier available)
- Create a new cluster
- Get connection string and add to MONGO_URL

### 3. Deploy to Vercel
```bash
# Option 1: Using Vercel CLI
npm i -g vercel
vercel --prod

# Option 2: Connect GitHub repo in Vercel dashboard
# - Import your GitHub repository
# - Vercel will auto-detect the configuration
# - Uses Node.js 22.x LTS (latest)
```

### 4. Update Frontend URL
After deployment, update `.env.production`:
```
REACT_APP_BACKEND_URL=https://your-actual-app-name.vercel.app
```

## API Endpoints (After Deployment)
- `POST https://your-app.vercel.app/api/clients`
- `POST https://your-app.vercel.app/api/admin/login` 
- `GET https://your-app.vercel.app/api/admin/clients`
- `GET https://your-app.vercel.app/api/admin/clients/export`
- `GET https://your-app.vercel.app/api/admin/stats`

## Key Changes Made
1. **Converted FastAPI to serverless functions** - Each endpoint is now a separate Python file
2. **Added CORS handling** - All functions include proper CORS headers
3. **Optimized MongoDB connections** - Connection reuse for serverless environment
4. **Environment variable security** - Moved hardcoded credentials to env vars
5. **Proper Vercel configuration** - Created vercel.json with correct routing

## Testing After Deployment
1. Visit your Vercel app URL
2. Test client form submission
3. Test admin login (username: admin, password: from env var)
4. Test admin dashboard functionality
5. Test CSV export

## Troubleshooting
- Check Vercel function logs for errors
- Ensure all environment variables are set
- Verify MongoDB Atlas connection string
- Check CORS_ORIGINS includes your Vercel domain
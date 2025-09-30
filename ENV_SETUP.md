# Environment Variables Setup Guide

## 🔒 **Security First - Using .env Files**

This project uses `.env` files to keep sensitive information (like database URLs and admin passwords) private and secure.

## 📁 **File Structure**

```
/app/
├── backend/.env              # Backend environment variables (DO NOT COMMIT)
├── backend/.env.example      # Template for backend variables (safe to commit)
├── frontend/.env             # Frontend environment variables (DO NOT COMMIT)
├── frontend/.env.example     # Template for frontend variables (safe to commit)
└── .gitignore               # Ensures .env files are never committed
```

## 🚀 **Local Development Setup**

### Step 1: Copy Example Files
```bash
# Copy backend template
cp backend/.env.example backend/.env

# Copy frontend template  
cp frontend/.env.example frontend/.env
```

### Step 2: Configure Backend (.env)
Edit `backend/.env` with your actual values:

```env
# Database Configuration
MONGO_URL=mongodb://localhost:27017
# For MongoDB Atlas: mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
DB_NAME=client_form_db

# Admin Credentials (CHANGE THESE!)
ADMIN_USERNAME=your_chosen_username
ADMIN_PASSWORD=your_secure_password_123!

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Step 3: Configure Frontend (.env)
Edit `frontend/.env`:

```env
# Points to your local backend
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🌐 **Production Deployment**

### For Vercel Deployment:

1. **Never commit .env files** - they're in .gitignore for security
2. **Set environment variables in Vercel dashboard:**
   - Go to your Vercel project settings
   - Add these environment variables:

```env
MONGO_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
DB_NAME=client_form_db
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password
CORS_ORIGINS=https://your-app.vercel.app
```

3. **Frontend automatically uses production URL** when deployed

## ✅ **Security Checklist**

- ✅ `.env` files are in `.gitignore`
- ✅ Only `.env.example` files are committed to GitHub
- ✅ Real passwords and URLs are never in source code
- ✅ Production uses different credentials than development
- ✅ CORS_ORIGINS restricts which domains can access your API

## 🔧 **Current Configuration**

### Local Development:
- **Backend**: `http://localhost:8001`
- **Frontend**: `http://localhost:3000`  
- **Database**: Local MongoDB on `mongodb://localhost:27017`
- **Admin Login**: Uses credentials from `backend/.env`

### Production (After Deployment):
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: Serverless functions on same domain
- **Database**: MongoDB Atlas (cloud)
- **Admin Login**: Uses Vercel environment variables

## 🚨 **Important Notes**

1. **Never commit .env files** - They contain secrets!
2. **Change default passwords** - Don't use `admin123` in production
3. **Use MongoDB Atlas** - For production database
4. **Update CORS_ORIGINS** - Add your actual Vercel domain

## 🆘 **Troubleshooting**

**App not connecting to backend?**
- Check `REACT_APP_BACKEND_URL` in `frontend/.env`
- Ensure backend is running on the correct port

**Database connection errors?**
- Verify `MONGO_URL` in `backend/.env`
- For Atlas: check username, password, and cluster URL

**Admin login not working?**
- Check `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `backend/.env`
- Make sure you're using the same credentials you set
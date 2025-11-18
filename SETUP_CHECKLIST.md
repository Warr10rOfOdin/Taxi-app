# Voss Taxi Setup & Verification Checklist

Complete guide to set up and verify your Voss Taxi web application with authentication.

---

## <¯ Quick Setup Guide

Choose your setup:
- **[Local Development](#local-development-setup)** - Run on your computer
- **[Production Deployment](#production-deployment-vercel)** - Deploy to Vercel

---

## Local Development Setup

### Prerequisites

Before you start, ensure you have:
- [ ] Python 3.9 or higher installed
- [ ] Node.js 18 or higher installed
- [ ] Git installed
- [ ] Code editor (VS Code recommended)

### Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd Taxi-app
```

### Step 2: Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd web-app/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - **Mac/Linux:** `source venv/bin/activate`
   - **Windows:** `venv\Scripts\activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify .env file exists:**
   ```bash
   ls -la .env
   ```
   Should contain:
   ```
   DATABASE_URL=sqlite:///./taxi_app.db
   SECRET_KEY=dev-secret-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

6. **Start backend server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Verify backend is running:**
   - Open browser: http://localhost:8000
   - Should see: `{"status":"ok","message":"Voss Taxi Web App API"}`
   - API docs: http://localhost:8000/docs

### Step 3: Frontend Setup

1. **Open new terminal, navigate to frontend:**
   ```bash
   cd web-app/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Verify frontend is running:**
   - Terminal will show: `Local: http://localhost:5173`
   - Open that URL in browser
   - Should see the login page

### Step 4: Create First User

1. **Open app:** http://localhost:5173
2. **Click "Opprett ny konto"** (Create new account)
3. **Fill in registration form:**
   - Full name: Test User
   - Email: test@example.com
   - Username: testuser
   - Password: test1234
4. **Click "Registrer"** (Register)
5. **Verify:**
   - Should be automatically logged in
   - Should see the home page
   - Sidebar should show your name and email
   - Can navigate to different pages

### Step 5: Test Core Features

- [ ] **Settings page loads** - Add company info
- [ ] **Add a driver** - In Settings ’ Drivers
- [ ] **Add bank account** - In Settings ’ Bank Accounts
- [ ] **Logout works** - Click "Logg ut" in sidebar
- [ ] **Login works** - Login with your credentials
- [ ] **Protected routes work** - Try accessing http://localhost:5173/ without logging in (should redirect to login)

---

## Production Deployment (Vercel)

### Prerequisites

- [ ] Vercel account (free tier available)
- [ ] Supabase account (free tier available)
- [ ] Domain name (optional but recommended)

### Part A: Database Setup (Supabase)

#### 1. Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click **"New Project"**
3. Fill in:
   - **Name:** voss-taxi-db
   - **Database Password:** (Generate strong password - save it!)
   - **Region:** Choose closest to your users
4. Click **"Create new project"**
5. Wait 2-3 minutes for project to initialize

#### 2. Initialize Database Tables

1. In Supabase Dashboard, click **"SQL Editor"** in sidebar
2. Click **"New query"**
3. Copy contents from `web-app/backend/init_database.sql`
4. Paste into SQL Editor
5. Click **"Run"** (or Ctrl+Enter / Cmd+Enter)
6. Verify success:
   - Should see "Database initialized successfully!"
   - Click **"Table Editor"** ’ should see 8 tables (users, companies, drivers, etc.)

#### 3. Get Database Connection String

1. In Supabase Dashboard, click **"Project Settings"** ’ **"Database"**
2. Scroll to **"Connection string"**
3. Select **"URI"** tab
4. Click **"Connection pooling"** toggle
5. Copy the connection string (starts with `postgresql://`)
6. **Replace [YOUR-PASSWORD]** with your actual database password
7. **Verify it uses port 6543** (not 5432)
8. Save this for later

### Part B: Backend Deployment

#### 1. Deploy Backend to Vercel

1. Go to https://vercel.com/new
2. Import your Git repository
3. **Project settings:**
   - **Framework Preset:** Other
   - **Root Directory:** `web-app/backend`
   - **Build Command:** Leave empty
   - **Output Directory:** Leave empty
4. Click **"Deploy"**
5. Wait for deployment to complete

#### 2. Configure Environment Variables

1. In Vercel project, click **"Settings"** ’ **"Environment Variables"**
2. Add these variables (one by one):

**Required variables:**

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `DATABASE_URL` | `postgresql://...` | Your Supabase connection string from Part A |
| `SECRET_KEY` | Generate new | Run: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ALGORITHM` | `HS256` | Leave as is |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiry in minutes |
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Add production URL later |
| `UPLOAD_DIR` | `/tmp/uploads` | Temporary file storage |
| `PDF_DIR` | `/tmp/pdfs` | PDF output directory |

3. **For each variable:**
   - Click **"Add New"**
   - Enter **Name** and **Value**
   - Check **Production**, **Preview**, and **Development**
   - Click **"Save"**

#### 3. Redeploy Backend

1. Go to **"Deployments"** tab
2. Click **"..."** on latest deployment ’ **"Redeploy"**
3. Wait for deployment to complete
4. **Test backend:**
   - Click on deployment URL (e.g., `https://your-project.vercel.app`)
   - Should see: `{"status":"ok","message":"Voss Taxi Web App API"}`

#### 4. Configure Custom Domain (Optional)

1. In Vercel project, click **"Settings"** ’ **"Domains"**
2. Add domain: `api.voss-taxi.app` (or your domain)
3. Follow DNS configuration instructions
4. Wait for SSL certificate to be issued

### Part C: Frontend Deployment

#### 1. Deploy Frontend to Vercel

1. Go to https://vercel.com/new
2. Import your Git repository again (same repo, different project)
3. **Project settings:**
   - **Framework Preset:** Vite
   - **Root Directory:** `web-app/frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Click **"Deploy"**
5. Wait for deployment to complete

#### 2. Configure Environment Variables

1. In frontend Vercel project, click **"Settings"** ’ **"Environment Variables"**
2. Add this variable:

| Variable Name | Value |
|--------------|-------|
| `VITE_API_URL` | Your backend URL (e.g., `https://your-backend.vercel.app` or `https://api.voss-taxi.app`) |

3. Check **Production**, **Preview**, and **Development**
4. Click **"Save"**

#### 3. Redeploy Frontend

1. Go to **"Deployments"** tab
2. Click **"..."** on latest deployment ’ **"Redeploy"**
3. Wait for deployment to complete

#### 4. Configure Custom Domain (Optional)

1. In frontend Vercel project, click **"Settings"** ’ **"Domains"**
2. Add domains:
   - `voss-taxi.app`
   - `www.voss-taxi.app`
3. Follow DNS configuration instructions

### Part D: Update Backend CORS Settings

After frontend is deployed:

1. Go to **backend** Vercel project
2. **Settings** ’ **Environment Variables**
3. Find `ALLOWED_ORIGINS`
4. Click **Edit**
5. Update value to include your frontend URLs:
   ```
   https://voss-taxi.app,https://www.voss-taxi.app,https://your-frontend.vercel.app,http://localhost:3000,http://localhost:5173
   ```
6. Save and **redeploy backend**

### Part E: First User Registration

1. Visit your frontend URL
2. Should see login page
3. Click **"Opprett ny konto"** (Create new account)
4. Register your first admin user
5. Login and start using the app!

---

##  Verification Checklist

### Local Development

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can access http://localhost:8000 (backend)
- [ ] Can access http://localhost:5173 (frontend)
- [ ] Can register new user
- [ ] Can login with credentials
- [ ] User info shows in sidebar
- [ ] Can logout
- [ ] Protected routes work (redirect to login when not authenticated)
- [ ] Can access Settings page
- [ ] Can add company info
- [ ] Can add drivers
- [ ] Can add bank accounts

### Production Deployment

- [ ] Backend deployed to Vercel
- [ ] Frontend deployed to Vercel
- [ ] Backend health check returns OK
- [ ] Frontend loads without errors
- [ ] Can register new user
- [ ] Can login
- [ ] User info shows in sidebar
- [ ] Can logout
- [ ] All pages load correctly
- [ ] No CORS errors in browser console
- [ ] Can add company settings
- [ ] Can add drivers and bank accounts
- [ ] Custom domains configured (if applicable)
- [ ] SSL certificates issued (automatic with Vercel)

---

## = Troubleshooting

### Backend Issues

**Error: "Module not found"**
- Solution: Make sure you activated virtual environment and ran `pip install -r requirements.txt`

**Error: Database connection failed**
- Solution: Check DATABASE_URL format in .env file
- For local: `sqlite:///./taxi_app.db`
- For production: `postgresql://...` with port 6543

**Error: "Address already in use"**
- Solution: Port 8000 is already taken. Kill the process or use different port:
  ```bash
  uvicorn main:app --reload --port 8001
  ```

### Frontend Issues

**Error: "Cannot connect to API"**
- Solution: Make sure backend is running
- Check VITE_API_URL in .env.local (create if doesn't exist)
- For local: `VITE_API_URL=http://localhost:8000`

**Error: "Network Error" or CORS**
- Solution: Check backend ALLOWED_ORIGINS includes your frontend URL
- Make sure both frontend and backend are running

**Page shows blank/white screen**
- Solution: Check browser console (F12) for errors
- Clear browser cache and localStorage
- Try incognito/private window

### Authentication Issues

**Can't register: "Username already registered"**
- Solution: Choose different username or login with existing account

**Can't login: "Incorrect username or password"**
- Solution: Check username and password (case-sensitive)
- Make sure user was successfully registered

**Automatically logged out**
- Solution: Token expired (30 minutes). This is normal. Login again.

**Stuck on login page after successful login**
- Solution: Clear browser localStorage
- Check browser console for errors
- Verify backend is accessible

### Production Deployment Issues

**Backend returns 500 error**
- Check Vercel function logs: Deployments ’ Click deployment ’ "View Function Logs"
- Verify all environment variables are set
- Make sure database tables were created in Supabase

**Frontend can't connect to backend**
- Verify VITE_API_URL is set correctly
- Check backend ALLOWED_ORIGINS includes frontend URL
- Verify backend is deployed and accessible
- Check for CORS errors in browser console

**"Database connection failed" in production**
- Verify DATABASE_URL uses connection pooling (port 6543)
- Check Supabase database is running
- Verify password in connection string is correct

---

## =Þ Getting Help

If you encounter issues not covered here:

1. **Check browser console** (F12 ’ Console tab) for error messages
2. **Check backend logs:**
   - Local: Terminal where uvicorn is running
   - Production: Vercel ’ Deployments ’ Function Logs
3. **Verify environment variables** are set correctly
4. **Check archived guides** in `docs-archive/` for additional troubleshooting

---

## <‰ Next Steps

Once everything is working:

1. **Add company information** - Settings ’ Company
2. **Add drivers** - Settings ’ Drivers
3. **Add bank accounts** - Settings ’ Bank Accounts
4. **Create shift reports** - Upload Excel/DAT files
5. **Generate salary reports** - Select driver and upload files
6. **Export PDFs** - Generate professional reports

**Your Voss Taxi application is ready to use!** =•

# 🚀 Quick Deployment Checklist

## ✅ Code Fixes Applied

The following fixes have been pushed to fix the backend crashes:

- ✅ Fixed Mangum handler import order
- ✅ Added defensive error handling for database initialization
- ✅ Changed SQLite fallback to use /tmp (Vercel-compatible)
- ✅ App won't crash even if env vars are missing

## 🔧 What You Need To Do Now

### Step 1: Redeploy Backend (Pull Latest Code)

Your Vercel backend needs to pull the latest code:

1. Go to **Vercel Dashboard** → Your backend project (api.voss-taxi.app)
2. Go to **Deployments** tab
3. Click **"..."** (three dots) on the latest deployment
4. Click **"Redeploy"**
5. Wait for deployment to complete

### Step 2: Set Environment Variables

**CRITICAL:** Set these 7 environment variables in Vercel:

1. Go to **Settings** → **Environment Variables**
2. Add each variable for **All Environments** (Production, Preview, Development):

```bash
ALLOWED_ORIGINS=https://voss-taxi.app,https://www.voss-taxi.app,https://voss-taxi-web.vercel.app

DATABASE_URL=postgresql://postgres.eqclrxoeunhwlslazaas:[YOUR-NEW-PASSWORD]@aws-1-eu-north-1.pooler.supabase.com:6543/postgres?sslmode=require

SECRET_KEY=[GENERATE-NEW-RANDOM-KEY]

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

UPLOAD_DIR=/tmp/uploads

PDF_DIR=/tmp/pdfs
```

**IMPORTANT:**
- Replace `[YOUR-NEW-PASSWORD]` with your **new** Supabase password (after resetting it - see SECURITY_INCIDENT_REMEDIATION.md)
- Generate `SECRET_KEY` with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### Step 3: Redeploy Again (After Setting Env Vars)

After adding environment variables:

1. Go to **Deployments** tab
2. Click **"Redeploy"** again to use the new environment variables

### Step 4: Verify Backend is Working

1. Visit: **https://api.voss-taxi.app**
2. Should see: `{"status":"ok","message":"Voss Taxi Web App API"}`
3. If you see this, the backend is working! ✅

### Step 5: Test Registration

1. Go to: **https://voss-taxi-web.vercel.app**
2. Click **"Register"**
3. Create an account
4. If successful, you're done! 🎉

## 🔍 Troubleshooting

### Still getting 500 error?

**Check Vercel Logs:**
1. Go to **Deployments** → Click on latest deployment
2. Click **"View Function Logs"**
3. Look for error messages

**Common Issues:**
- Environment variables not set → Set them in Vercel Settings
- Wrong DATABASE_URL → Verify it's the pooler URL from Supabase
- Missing SECRET_KEY → Generate and set a new one

### CORS errors?

- Verify `ALLOWED_ORIGINS` includes all three domains
- No typos in the URLs
- No trailing slashes

### Database connection errors?

- Use the **pooler** URL (port 6543), not direct (port 5432)
- Verify password is correct
- Check Supabase project is active

## 📊 What Changed

**Before:**
- Mangum import at bottom of file → Import order issues
- Database init could crash function → No error handling
- SQLite default path not writable in Vercel → Function crash

**After:**
- Mangum imported at top with other imports ✅
- Database init wrapped in try/except ✅
- SQLite uses /tmp (writable in Vercel) ✅
- Fallback to in-memory DB if connection fails ✅

## Need Help?

See detailed guides:
- **VERCEL_ENV_SETUP.md** - Environment variables guide
- **SECURITY_INCIDENT_REMEDIATION.md** - Security fixes required

The backend should work after redeploying with environment variables! 🚀

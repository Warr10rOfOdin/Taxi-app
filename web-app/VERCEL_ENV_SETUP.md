# Vercel Environment Variables Setup

## CRITICAL: Fix CORS and Database Issues

Your backend is crashing because of missing environment variables. Follow these steps **exactly**:

## Backend Environment Variables (api.voss-taxi.app)

1. Go to Vercel Dashboard → Your backend project → Settings → Environment Variables
2. Add these **EXACT** variables:

### Required Variables:

```
ALLOWED_ORIGINS=https://voss-taxi.app,https://www.voss-taxi.app,https://voss-taxi-web.vercel.app
```

```
DATABASE_URL=postgresql://postgres.xpqxrvzfwokbzvjdvduc:Toni19881209@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

```
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
```

```
ALGORITHM=HS256
```

```
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

```
UPLOAD_DIR=/tmp/uploads
```

```
PDF_DIR=/tmp/pdfs
```

## How to Add Environment Variables:

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Select your backend project** (the one deployed at api.voss-taxi.app)
3. **Click Settings** tab
4. **Click Environment Variables** in the left sidebar
5. **For each variable above**:
   - Click "Add New"
   - Enter the **Name** (e.g., `ALLOWED_ORIGINS`)
   - Enter the **Value** (e.g., the full URL list)
   - Select **All** environments (Production, Preview, Development)
   - Click **Save**
6. **After adding all variables**, go to the **Deployments** tab
7. **Redeploy** by clicking the three dots (•••) on the latest deployment → "Redeploy"

## Important Notes:

### ALLOWED_ORIGINS
- **MUST** include all frontend domains:
  - `https://voss-taxi.app` - your custom domain
  - `https://www.voss-taxi.app` - www subdomain
  - `https://voss-taxi-web.vercel.app` - Vercel deployment URL
- **NO trailing slashes**
- **Comma-separated** (no spaces)

### DATABASE_URL
- Uses Supabase **pooler** for serverless: `pooler.supabase.com:6543`
- **NOT** the direct connection string
- Make sure it starts with `postgresql://` (not `postgres://` - some tools need the full name)

### SECRET_KEY
- **CHANGE THIS** to a random string
- Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Must be at least 32 characters
- **Keep it secret!**

### Upload Directories
- Use `/tmp` for Vercel serverless (writable)
- NOT `uploads` or `pdfs` (those won't work in serverless)

## Frontend Environment Variables (voss-taxi-web.vercel.app)

1. Go to Vercel Dashboard → Your frontend project → Settings → Environment Variables
2. Add this variable:

```
VITE_API_URL=https://api.voss-taxi.app
```

## Verify Setup:

After adding variables and redeploying:

1. Visit https://api.voss-taxi.app → Should show: `{"status":"ok","message":"Voss Taxi Web App API"}`
2. Try registration at https://voss-taxi-web.vercel.app
3. Check browser console - CORS errors should be gone
4. Check Vercel deployment logs for any errors

## Troubleshooting:

### Still getting CORS errors?
- Verify `ALLOWED_ORIGINS` includes `https://voss-taxi-web.vercel.app`
- No typos in the URLs
- No trailing slashes
- Redeploy after adding the variable

### Backend still crashing?
- Check `DATABASE_URL` is correct
- Verify it uses the pooler: `pooler.supabase.com:6543`
- Check Vercel logs: Deployments → Click deployment → "View Function Logs"

### Database connection errors?
- Make sure using **pooler** URL (port 6543), not direct connection (port 5432)
- Verify Supabase project is active
- Check password is correct in the connection string

### Registration fails with 500 error?
- Check all environment variables are set
- Make sure `SECRET_KEY` is set
- Verify database tables are created (check Supabase dashboard)

## After Setup:

Once environment variables are set and backend is redeployed successfully:

1. **Test the API**: https://api.voss-taxi.app
2. **Register a user**: Go to your app and create an account
3. **Verify authentication**: Login and access protected routes

Your app should now work! 🎉

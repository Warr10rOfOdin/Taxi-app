# Production Environment Variables

## Quick Copy-Paste for Vercel

### Backend Environment Variables

Copy these to: Vercel Dashboard > voss-taxi-backend > Settings > Environment Variables

```
DATABASE_URL
[Get from Vercel Storage > Supabase > Connection String]
Example: postgresql://postgres.abcdefg:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

```
SECRET_KEY
df3e4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f
```
(⚠️ Generate a new one for production using: `openssl rand -hex 32`)

```
ALGORITHM
HS256
```

```
ACCESS_TOKEN_EXPIRE_MINUTES
30
```

```
ALLOWED_ORIGINS
https://voss-taxi.app,https://www.voss-taxi.app
```

```
UPLOAD_DIR
/tmp/uploads
```

```
PDF_DIR
/tmp/pdfs
```

---

### Frontend Environment Variables

Copy these to: Vercel Dashboard > voss-taxi-web > Settings > Environment Variables

```
VITE_API_URL
https://api.voss-taxi.app
```

---

## How to Add Environment Variables in Vercel

1. Go to your project in Vercel Dashboard
2. Click "Settings" tab
3. Click "Environment Variables" in left sidebar
4. For each variable:
   - Enter the variable name (e.g., `DATABASE_URL`)
   - Enter the value
   - Select all environments: Production, Preview, Development
   - Click "Save"
5. After adding all variables, redeploy your project

## Important Notes

### DATABASE_URL
- Get this from: Vercel > Storage > Your Supabase Database > Connect
- **Use the Pooler connection string** (port 6543, not 5432)
- Format: `postgresql://postgres.[project-ref]:[password]@[host]:6543/postgres`
- Must include the password!

### SECRET_KEY
- **Never use the example key in production!**
- Generate a new one: `openssl rand -hex 32`
- Keep it secret, never commit to Git
- Change it periodically for security

### ALLOWED_ORIGINS
- Must match your exact frontend domain(s)
- Include both with and without www if you're using both
- No trailing slashes
- Comma-separated for multiple origins

### VITE_API_URL
- Must match your backend custom domain
- No trailing slash
- Should be https://api.voss-taxi.app

## Verification

After setting all variables, verify they're correct:

### Backend Variables Check
1. Go to backend project > Settings > Environment Variables
2. You should see 7 variables:
   - ✅ DATABASE_URL
   - ✅ SECRET_KEY
   - ✅ ALGORITHM
   - ✅ ACCESS_TOKEN_EXPIRE_MINUTES
   - ✅ ALLOWED_ORIGINS
   - ✅ UPLOAD_DIR
   - ✅ PDF_DIR

### Frontend Variables Check
1. Go to frontend project > Settings > Environment Variables
2. You should see 1 variable:
   - ✅ VITE_API_URL

## After Adding Variables

1. **Redeploy both projects:**
   - Go to Deployments tab
   - Find the latest deployment
   - Click the three dots (...)
   - Click "Redeploy"
   - Do this for BOTH backend and frontend

2. **Test the deployment:**
   - Visit https://voss-taxi.app
   - Open browser console (F12)
   - Check for any errors
   - Try accessing Settings page

## Security Checklist

- [ ] DATABASE_URL contains the correct Supabase connection string
- [ ] SECRET_KEY is unique and randomly generated (not the example!)
- [ ] ALLOWED_ORIGINS matches your frontend domain exactly
- [ ] Environment variables are set in Production environment
- [ ] No sensitive data is committed to Git
- [ ] All variables are marked for all environments (if needed for previews)

---

Need help? Check the main deployment guide: `DEPLOYMENT_GUIDE_voss-taxi-app.md`

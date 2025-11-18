# Vercel Quick Start Guide

Deploy Voss Taxi Web App to Vercel in 5 minutes!

## Prerequisites

- GitHub account
- Vercel account ([sign up free](https://vercel.com/signup))
- PostgreSQL database (get free at [Supabase](https://supabase.com) or [Vercel Postgres](https://vercel.com/storage/postgres))

## Step-by-Step Deployment

### 1. Prepare Database (2 minutes)

**Using Supabase (Recommended for Free Tier):**

1. Go to [supabase.com](https://supabase.com) and sign up
2. Create a new project
3. Go to Settings > Database
4. Copy the "Connection string" (use Transaction mode)
5. Save this for later: `postgresql://postgres:[password]@[host]:5432/postgres`

**Using Vercel Postgres:**

1. Go to Vercel Dashboard
2. Storage > Create Database > Postgres
3. Copy the connection string

### 2. Deploy Backend (3 minutes)

1. **Go to Vercel:** [vercel.com/new](https://vercel.com/new)

2. **Import Repository:**
   - Select your GitHub repository
   - Click "Import"

3. **Configure Backend:**
   - Project Name: `voss-taxi-backend`
   - Framework: Other
   - Root Directory: `web-app/backend`
   - Build Command: (leave empty)
   - Click "Deploy"

4. **Wait for deployment** (this will fail initially - that's OK!)

5. **Add Environment Variables:**
   - Go to your project settings
   - Click "Environment Variables"
   - Add these variables:

   ```
   DATABASE_URL = [your-postgres-connection-string]
   SECRET_KEY = [generate-random-string]
   ALGORITHM = HS256
   ALLOWED_ORIGINS = *
   UPLOAD_DIR = /tmp/uploads
   PDF_DIR = /tmp/pdfs
   ```

   **Generate SECRET_KEY:** Use [randomkeygen.com](https://randomkeygen.com) or run:
   ```bash
   openssl rand -hex 32
   ```

6. **Redeploy:**
   - Go to Deployments tab
   - Click on the failed deployment
   - Click "Redeploy"

7. **Copy your backend URL:** `https://voss-taxi-backend.vercel.app`

### 3. Deploy Frontend (2 minutes)

1. **Import Again:** Go to [vercel.com/new](https://vercel.com/new)

2. **Configure Frontend:**
   - Project Name: `voss-taxi-web`
   - Framework: Vite
   - Root Directory: `web-app/frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Add Environment Variable:**
   ```
   VITE_API_URL = [your-backend-url-from-step-2]
   ```

4. **Deploy!**

5. **Visit your app:** `https://voss-taxi-web.vercel.app`

### 4. Update CORS (1 minute)

1. Go back to your backend project
2. Settings > Environment Variables
3. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS = https://voss-taxi-web.vercel.app
   ```
   (Use your actual frontend URL)
4. Redeploy backend

### 5. Initialize Database

Connect to your database and run:

```sql
-- Tables will be created automatically on first API call
-- Or manually initialize using your favorite PostgreSQL client
```

## Done! 🎉

Your app is live at: `https://voss-taxi-web.vercel.app`

### First Steps

1. Go to Settings
2. Add company information
3. Add drivers
4. Start creating reports!

## Troubleshooting

**Problem:** Frontend can't connect to backend
- Check `VITE_API_URL` matches your backend URL
- Check `ALLOWED_ORIGINS` includes your frontend URL
- Redeploy both frontend and backend

**Problem:** Database errors
- Verify `DATABASE_URL` is correct
- Check database is running and accessible
- Ensure connection string uses `postgresql://` (not `postgres://`)

**Problem:** Build fails
- Check all environment variables are set
- Look at deployment logs for specific errors
- Ensure root directory is correct

## Custom Domain (Optional)

1. Go to your project settings
2. Domains tab
3. Add your domain
4. Update DNS records as shown
5. Update `ALLOWED_ORIGINS` to include your custom domain

## Support

For detailed documentation, see [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)

---

**Environment Variables Checklist:**

Backend:
- [ ] DATABASE_URL
- [ ] SECRET_KEY
- [ ] ALGORITHM
- [ ] ALLOWED_ORIGINS
- [ ] UPLOAD_DIR
- [ ] PDF_DIR

Frontend:
- [ ] VITE_API_URL

All set? Your app should be working! 🚀

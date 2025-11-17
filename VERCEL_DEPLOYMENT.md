# Vercel Deployment Guide for Voss Taxi Web App

This guide will help you deploy the Voss Taxi web application to Vercel.

## Overview

The application is split into two parts:
1. **Frontend** (React + Vite) - Deployed to Vercel
2. **Backend** (FastAPI) - Deployed to Vercel as serverless functions

## Prerequisites

- [Vercel Account](https://vercel.com/signup)
- [Vercel CLI](https://vercel.com/download) (optional, for local testing)
- GitHub account (for continuous deployment)
- PostgreSQL database (recommended: [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres) or [Supabase](https://supabase.com/))

## Option 1: Deploy via Vercel Dashboard (Recommended)

### Step 1: Set Up Database

1. **Create a PostgreSQL database:**
   - **Option A - Vercel Postgres:**
     - Go to your Vercel dashboard
     - Create a new Postgres database
     - Copy the `DATABASE_URL` connection string

   - **Option B - Supabase:**
     - Create account at [supabase.com](https://supabase.com)
     - Create new project
     - Go to Settings > Database
     - Copy the connection string (use "Transaction" mode)
     - Format: `postgresql://user:password@host:port/database`

   - **Option C - Railway/Render:**
     - Create PostgreSQL instance
     - Copy connection string

### Step 2: Deploy Backend

1. **Fork/Push repository to GitHub** (if not already done)

2. **Import to Vercel:**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Select your repository
   - Configure project:
     - **Project Name:** `voss-taxi-backend`
     - **Framework Preset:** Other
     - **Root Directory:** `web-app/backend`
     - **Build Command:** Leave empty or `echo "No build needed"`
     - **Output Directory:** Leave empty

3. **Add Environment Variables:**
   Go to Settings > Environment Variables and add:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   SECRET_KEY=your-secret-key-here-generate-a-strong-one
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
   UPLOAD_DIR=/tmp/uploads
   PDF_DIR=/tmp/pdfs
   ```

4. **Deploy:**
   - Click "Deploy"
   - Wait for deployment to complete
   - Note your backend URL (e.g., `https://voss-taxi-backend.vercel.app`)

### Step 3: Deploy Frontend

1. **Import to Vercel:**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Select your repository
   - Configure project:
     - **Project Name:** `voss-taxi-web`
     - **Framework Preset:** Vite
     - **Root Directory:** `web-app/frontend`
     - **Build Command:** `npm run build`
     - **Output Directory:** `dist`

2. **Add Environment Variables:**
   Go to Settings > Environment Variables and add:
   ```
   VITE_API_URL=https://your-backend-url.vercel.app
   ```
   Replace `your-backend-url` with your actual backend URL from Step 2.

3. **Deploy:**
   - Click "Deploy"
   - Wait for deployment to complete
   - Visit your live site!

### Step 4: Update CORS

1. Go back to your backend deployment
2. Update the `ALLOWED_ORIGINS` environment variable:
   ```
   ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
   ```
3. Redeploy the backend (Settings > Deployments > ... > Redeploy)

## Option 2: Deploy via Vercel CLI

### Install Vercel CLI

```bash
npm install -g vercel
```

### Login

```bash
vercel login
```

### Deploy Backend

```bash
cd web-app/backend

# First deployment
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: voss-taxi-backend
# - Directory: ./
# - Override settings? No

# Add environment variables
vercel env add DATABASE_URL
vercel env add SECRET_KEY
vercel env add ALLOWED_ORIGINS

# Deploy to production
vercel --prod
```

### Deploy Frontend

```bash
cd web-app/frontend

# First deployment
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: voss-taxi-web
# - Directory: ./
# - Override settings? No

# Add environment variables
vercel env add VITE_API_URL

# Deploy to production
vercel --prod
```

## Database Setup

After deployment, initialize the database:

### Option A: Via Python Script

Create a file `init_db.py`:

```python
import psycopg2
from database import Base, engine

# This will create all tables
Base.metadata.create_all(bind=engine)
print("Database initialized!")
```

Run locally with your production DATABASE_URL:
```bash
DATABASE_URL="your-production-url" python init_db.py
```

### Option B: Manual SQL

Connect to your PostgreSQL database and run the SQL to create tables. The schema is defined in `models.py`.

## Environment Variables Summary

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT secret key | Generate with `openssl rand -hex 32` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` |
| `ALLOWED_ORIGINS` | Frontend URLs for CORS | `https://yourapp.vercel.app` |
| `UPLOAD_DIR` | Upload directory | `/tmp/uploads` |
| `PDF_DIR` | PDF directory | `/tmp/pdfs` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://your-backend.vercel.app` |

## Post-Deployment

### 1. Test the Application

- Visit your frontend URL
- Go to Settings and add:
  - Company information
  - Drivers
  - Bank accounts
- Test uploading files and generating reports

### 2. Set Up Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Navigate to Domains
3. Add your custom domain
4. Update DNS records as instructed
5. Update `ALLOWED_ORIGINS` in backend to include your custom domain

### 3. Monitor Logs

- Vercel Dashboard > Your Project > Logs
- Watch for errors and performance issues

## Continuous Deployment

Vercel automatically deploys when you push to your repository:

- **Push to main branch:** Deploys to production
- **Push to other branches:** Creates preview deployments

## Troubleshooting

### CORS Errors

**Problem:** Frontend can't connect to backend

**Solution:**
- Verify `ALLOWED_ORIGINS` in backend includes your frontend URL
- Check that `VITE_API_URL` in frontend matches your backend URL
- Redeploy backend after changing CORS settings

### Database Connection Errors

**Problem:** Backend can't connect to database

**Solution:**
- Verify `DATABASE_URL` is correctly formatted
- Check database is accessible from Vercel servers
- Ensure database allows connections from Vercel IPs
- For Vercel Postgres, enable "External" connection mode

### File Upload Fails

**Problem:** File uploads don't work

**Solution:**
- Vercel serverless functions have a 4.5MB body size limit
- For larger files, consider using:
  - Direct client-to-S3 upload
  - Vercel Edge Functions (50MB limit)
  - External file storage service

### PDF Generation Fails

**Problem:** PDFs don't generate

**Solution:**
- Check `/tmp` directory has write permissions (it should in Vercel)
- Verify fpdf library is installed
- Check logs for specific errors

## Performance Optimization

### 1. Database Connection Pooling

For production, use connection pooling:

```python
# database.py
from sqlalchemy.pool import NullPool

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool  # Recommended for serverless
)
```

### 2. Caching

Consider adding caching for:
- Company information
- Driver lists
- Templates

Use Vercel KV or Redis for caching.

### 3. Cold Starts

Vercel functions may have cold starts. To minimize:
- Keep dependencies minimal
- Use smaller regions
- Consider upgrading to Pro plan for faster cold starts

## Cost Considerations

### Vercel Free Tier Limits

- 100 GB bandwidth/month
- 100 hours serverless function execution/month
- 6000 minutes build time/month

For production use, consider:
- **Hobby plan** ($20/month): Unlimited bandwidth
- **Pro plan** ($20/month per user): Team features, better performance

### Database Costs

- **Vercel Postgres:** Starts at $0/month (hobby tier)
- **Supabase:** Free tier available, then $25/month
- **Railway:** $5/month minimum

## Security Best Practices

1. **Never commit secrets:** Use environment variables
2. **Rotate SECRET_KEY** regularly
3. **Use HTTPS only:** Vercel provides this automatically
4. **Implement rate limiting:** Protect your API
5. **Regular updates:** Keep dependencies updated
6. **Backup database:** Regular backups of PostgreSQL

## Scaling

As your app grows:

1. **Database:** Upgrade to larger PostgreSQL instance
2. **File Storage:** Move to S3/Cloudinary for files
3. **Caching:** Add Redis for frequently accessed data
4. **CDN:** Vercel includes CDN, but consider separate static assets CDN
5. **Monitoring:** Add Sentry or similar for error tracking

## Support

For issues:
1. Check Vercel logs
2. Review this documentation
3. Check Vercel documentation: [vercel.com/docs](https://vercel.com/docs)
4. Contact system administrator

## Next Steps

After successful deployment:

1. ✅ Set up monitoring and alerts
2. ✅ Configure automatic backups
3. ✅ Add custom domain
4. ✅ Set up SSL certificate (automatic with Vercel)
5. ✅ Configure CI/CD pipeline
6. ✅ Add integration tests
7. ✅ Set up staging environment

---

**Deployment Checklist:**

- [ ] PostgreSQL database created
- [ ] Backend deployed to Vercel
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured
- [ ] CORS properly set up
- [ ] Database initialized
- [ ] Application tested
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up
- [ ] Backups configured

Your Voss Taxi Web App is now live! 🎉

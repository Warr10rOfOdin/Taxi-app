# Voss Taxi App - Custom Domain Deployment Guide

## Your Setup

- **Domain:** voss-taxi.app
- **Database:** Supabase (connected in Vercel)
- **Hosting:** Vercel

## Recommended Architecture

```
Frontend: https://voss-taxi.app (or https://www.voss-taxi.app)
Backend:  https://api.voss-taxi.app
```

## Step-by-Step Deployment

### 1. Deploy Backend First

#### A. Deploy to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your repository: `Warr10rOfOdin/Taxi-app`
3. Configure:
   - **Project Name:** `voss-taxi-backend`
   - **Framework:** Other
   - **Root Directory:** `web-app/backend`
   - **Build Command:** (leave empty)

#### B. Set Environment Variables

In Vercel Dashboard > Your Backend Project > Settings > Environment Variables, add:

```
DATABASE_URL
```
Get this from Vercel Storage > Your Supabase > Connect > Connection String
(Should look like: postgresql://postgres.[project]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres)

```
SECRET_KEY
```
Generate a secure key:
```bash
# Run this in your terminal:
openssl rand -hex 32
```
Or use this: `df3e4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f`

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

#### C. Deploy Backend

Click "Deploy" and wait for it to complete.

Your backend will be at: `https://voss-taxi-backend.vercel.app`

#### D. Add Custom Domain to Backend

1. Go to backend project > Settings > Domains
2. Add domain: `api.voss-taxi.app`
3. Add DNS records as shown:
   - Type: CNAME
   - Name: api
   - Value: cname.vercel-dns.com
4. Wait for DNS to propagate (can take up to 48 hours, usually minutes)

### 2. Deploy Frontend

#### A. Deploy to Vercel

1. Go to [vercel.com/new](https://vercel.com/new) again
2. Import same repository: `Warr10rOfOdin/Taxi-app`
3. Configure:
   - **Project Name:** `voss-taxi-web`
   - **Framework:** Vite
   - **Root Directory:** `web-app/frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

#### B. Set Environment Variables

In Vercel Dashboard > Your Frontend Project > Settings > Environment Variables, add:

```
VITE_API_URL
https://api.voss-taxi.app
```

#### C. Deploy Frontend

Click "Deploy" and wait for completion.

Your frontend will be at: `https://voss-taxi-web.vercel.app`

#### D. Add Custom Domain to Frontend

1. Go to frontend project > Settings > Domains
2. Add your main domain: `voss-taxi.app`
3. Add www subdomain: `www.voss-taxi.app` (optional)
4. Add DNS records as shown:
   - For root domain (voss-taxi.app):
     - Type: A
     - Name: @
     - Value: 76.76.21.21
   - For www subdomain:
     - Type: CNAME
     - Name: www
     - Value: cname.vercel-dns.com

### 3. Update Backend CORS

Once your frontend domain is active:

1. Go to backend project > Settings > Environment Variables
2. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://voss-taxi.app,https://www.voss-taxi.app
   ```
3. Redeploy backend (Deployments > Latest > ... > Redeploy)

### 4. Test Your Deployment

1. Visit `https://voss-taxi.app`
2. Should see the Voss Taxi homepage
3. Go to Settings tab
4. Add company information
5. Add a test driver
6. Try uploading a file in Shift Report

### 5. Initialize Database (First Time Only)

Your database tables will be created automatically on first API call. But you can also manually initialize:

#### Option A: Via Supabase Dashboard

1. Go to your Supabase project
2. Click "SQL Editor"
3. The tables will be created automatically when you first use the app
4. Or run migrations manually if needed

#### Option B: Via API Call

Simply make any API call and tables will be created automatically.

## DNS Configuration Summary

Add these records to your domain registrar (where you bought voss-taxi.app):

| Type  | Name | Value                    | Purpose        |
|-------|------|--------------------------|----------------|
| A     | @    | 76.76.21.21             | Main domain    |
| CNAME | www  | cname.vercel-dns.com    | WWW subdomain  |
| CNAME | api  | cname.vercel-dns.com    | API subdomain  |

## Environment Variables Summary

### Backend (`api.voss-taxi.app`)

```env
DATABASE_URL=postgresql://postgres.[project]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
SECRET_KEY=df3e4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=https://voss-taxi.app,https://www.voss-taxi.app
UPLOAD_DIR=/tmp/uploads
PDF_DIR=/tmp/pdfs
```

### Frontend (`voss-taxi.app`)

```env
VITE_API_URL=https://api.voss-taxi.app
```

## Deployment Checklist

- [ ] Backend deployed to Vercel
- [ ] Backend environment variables configured
- [ ] Custom domain `api.voss-taxi.app` added to backend
- [ ] Frontend deployed to Vercel
- [ ] Frontend environment variable configured
- [ ] Custom domain `voss-taxi.app` added to frontend
- [ ] DNS records configured at domain registrar
- [ ] DNS propagated (check with `dig voss-taxi.app`)
- [ ] Backend CORS updated with frontend domain
- [ ] Both deployments redeployed with final config
- [ ] Application tested and working

## Troubleshooting

### "Can't connect to API"

**Check:**
1. Is `api.voss-taxi.app` resolving? Run: `dig api.voss-taxi.app`
2. Is `VITE_API_URL` set correctly in frontend env vars?
3. Is `ALLOWED_ORIGINS` set correctly in backend env vars?
4. Did you redeploy both after setting domains?

**Fix:**
```bash
# Check DNS
dig api.voss-taxi.app
dig voss-taxi.app

# Should return Vercel IPs
```

### CORS Errors

**Fix:**
1. Backend env vars > `ALLOWED_ORIGINS` = `https://voss-taxi.app,https://www.voss-taxi.app`
2. Redeploy backend
3. Clear browser cache

### Database Connection Issues

**Check:**
1. Vercel > Storage > Your Supabase > Connection String
2. Copy the **Pooler** connection string (port 6543, not 5432)
3. Update `DATABASE_URL` in backend env vars
4. Redeploy backend

### SSL Certificate Issues

**Wait:** SSL certificates are issued automatically by Vercel, can take up to 48 hours

**Force refresh:**
1. Vercel project > Settings > Domains
2. Remove and re-add the domain

## Next Steps After Deployment

1. **Set up monitoring:**
   - Vercel Analytics (free)
   - Sentry for error tracking (optional)

2. **Configure backups:**
   - Supabase automatic backups (included)
   - Consider weekly database exports

3. **Add users:**
   - Share the URL with your team
   - Add company info, drivers, bank accounts
   - Start creating reports!

4. **Enable automatic deployments:**
   - Already enabled! Push to GitHub = auto deploy
   - Main branch → production
   - Other branches → preview deployments

## URLs After Setup

- **Main App:** https://voss-taxi.app
- **API:** https://api.voss-taxi.app
- **API Docs:** https://api.voss-taxi.app/docs
- **Vercel Dashboard Backend:** https://vercel.com/your-username/voss-taxi-backend
- **Vercel Dashboard Frontend:** https://vercel.com/your-username/voss-taxi-web
- **Supabase Dashboard:** https://supabase.com/dashboard/project/[your-project]

## Support

If you encounter issues:

1. Check Vercel deployment logs
2. Check browser console (F12)
3. Check Network tab for failed requests
4. Review environment variables
5. Ensure DNS has propagated

---

**Ready to deploy?** Start with Step 1 above! 🚀

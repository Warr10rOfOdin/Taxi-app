# 🔥 QUICK FIX - Set Environment Variables NOW

Your backend is deployed but **missing environment variables**. This is causing the CORS and 404 errors.

## ⚡ 5-Minute Fix

### Step 1: Open Vercel Backend Project

1. Go to: https://vercel.com/dashboard
2. Find your **backend project** (should be named something like "taxi-app-backend" or deployed to `api.voss-taxi.app`)
3. Click on it

### Step 2: Go to Environment Variables

1. Click the **"Settings"** tab at the top
2. In the left sidebar, click **"Environment Variables"**

### Step 3: Add Each Variable

**You need to add 7 variables. For EACH variable:**

1. Click **"Add New"** button
2. Enter the **Name** (example: `ALLOWED_ORIGINS`)
3. Enter the **Value** (example: the URL list)
4. Select **"Production"**, **"Preview"**, and **"Development"** (check all three boxes)
5. Click **"Save"**
6. Repeat for all 7 variables below

---

## 📋 COPY & PASTE THESE EXACT VALUES:

### Variable 1: ALLOWED_ORIGINS
```
Name: ALLOWED_ORIGINS
Value: https://voss-taxi.app,https://www.voss-taxi.app,https://voss-taxi-web.vercel.app
```

### Variable 2: DATABASE_URL
```
Name: DATABASE_URL
Value: postgresql://postgres.eqclrxoeunhwlslazaas:iSwOn2PeuP7IjAqn@aws-1-eu-north-1.pooler.supabase.com:6543/postgres?sslmode=require
```

⚠️ **IMPORTANT:** You should reset your Supabase password first (see SECURITY_INCIDENT_REMEDIATION.md), then use the NEW password in this URL.

### Variable 3: SECRET_KEY
```
Name: SECRET_KEY
Value: [GENERATE YOUR OWN - See below]
```

**To generate SECRET_KEY, open a terminal and run:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as the value. It should look like: `xB3k9L2mP5nQ8rT1vW4yZ7aC6dF0gH3jK6mN9pR2sU5wY8b`

### Variable 4: ALGORITHM
```
Name: ALGORITHM
Value: HS256
```

### Variable 5: ACCESS_TOKEN_EXPIRE_MINUTES
```
Name: ACCESS_TOKEN_EXPIRE_MINUTES
Value: 30
```

### Variable 6: UPLOAD_DIR
```
Name: UPLOAD_DIR
Value: /tmp/uploads
```

### Variable 7: PDF_DIR
```
Name: PDF_DIR
Value: /tmp/pdfs
```

---

## Step 4: Redeploy

**After adding ALL 7 variables:**

1. Click the **"Deployments"** tab at the top
2. Find the most recent deployment (should be at the top)
3. Click the **"..."** (three dots) button on the right side
4. Click **"Redeploy"**
5. Click **"Redeploy"** again to confirm
6. Wait for deployment to finish (usually 30-60 seconds)

---

## Step 5: Test Backend

1. Open a new browser tab
2. Go to: **https://api.voss-taxi.app**
3. You should see: `{"status":"ok","message":"Voss Taxi Web App API"}`

✅ If you see this, the backend is working!

---

## Step 6: Test Registration

1. Go to: **https://www.voss-taxi.app**
2. Click **"Register"**
3. Fill in the form:
   - Username: test
   - Email: test@example.com
   - Full name: Test User
   - Password: test1234
4. Click **"Register"**

✅ If registration succeeds and you're logged in, everything is working!

---

## ❌ Still Not Working?

### If you still see CORS errors:

**Check Environment Variables:**
1. Vercel → Settings → Environment Variables
2. Verify `ALLOWED_ORIGINS` is set exactly as shown above
3. Make sure it's enabled for **Production** environment
4. Redeploy again

**Check Deployment Logs:**
1. Vercel → Deployments → Click on latest deployment
2. Click **"View Function Logs"**
3. Look for any error messages
4. Share the error with me

### If backend shows 403 or 500 errors:

1. Check that you redeployed AFTER adding environment variables
2. Verify `DATABASE_URL` is correct (check for typos)
3. Make sure `SECRET_KEY` is set (not empty)

---

## 🎯 Quick Checklist

Before asking for help, verify:

- [ ] All 7 environment variables are set in Vercel
- [ ] Each variable is enabled for Production, Preview, AND Development
- [ ] Backend was redeployed AFTER setting variables
- [ ] https://api.voss-taxi.app shows `{"status":"ok"}`
- [ ] Browser console shows no CORS errors

---

## 📞 What to Share If Still Broken

If it's still not working after following all steps:

1. Screenshot of your Environment Variables page (Settings → Environment Variables)
2. Error from browser console (F12 → Console tab)
3. URL of your Vercel deployment logs

The most common issue is **forgetting to redeploy after adding environment variables**. Make sure you do that!

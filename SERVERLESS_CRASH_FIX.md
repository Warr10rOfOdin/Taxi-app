# 🔧 Fix Serverless Function Crash - COMPLETE GUIDE

## Problem

Your backend is crashing with `500: INTERNAL_SERVER_ERROR` and `FUNCTION_INVOCATION_FAILED`.

**Root Cause:** The database tables don't exist in Supabase yet. When the serverless function starts, it tries to create tables but fails/times out, causing the function to crash.

## ✅ Solution: Initialize Database Tables First

You need to create the database tables in Supabase **before** the app tries to use them.

---

## 🚀 Step-by-Step Fix

### Step 1: Go to Supabase SQL Editor

1. Open Supabase Dashboard: https://supabase.com/dashboard
2. Select your project: `eqclrxoeunhwlslazaas`
3. Click **"SQL Editor"** in the left sidebar (or **"Database"** → **"SQL Editor"**)

### Step 2: Run the Database Initialization Script

1. In the SQL Editor, click **"New query"**
2. Copy the entire contents of `web-app/backend/init_database.sql`
3. Paste it into the SQL Editor
4. Click **"Run"** (or press Ctrl+Enter / Cmd+Enter)

You should see output like:
```
Database initialized successfully!
```

And a list of tables:
- bank_accounts
- companies
- drivers
- salary_reports
- shift_edits
- shift_reports
- templates
- users

### Step 3: Verify Tables Were Created

In Supabase:

1. Click **"Table Editor"** in the left sidebar
2. You should see all 8 tables listed
3. Click on **"users"** table to verify it exists

### Step 4: Redeploy Backend

Now that tables exist:

1. Go to Vercel Dashboard → Backend Project
2. Click **Deployments** tab
3. Click **"..."** → **"Redeploy"**
4. Wait for deployment to complete

### Step 5: Test Backend

1. Visit: **https://api.voss-taxi.app**
2. Should see: `{"status":"ok","message":"Voss Taxi Web App API"}`
3. ✅ If you see this, the backend is working!

### Step 6: Test Registration

1. Go to: **https://www.voss-taxi.app**
2. Click **"Register"**
3. Create a test account:
   - Username: testuser
   - Email: test@example.com
   - Full name: Test User
   - Password: test1234
4. Click **"Register"**
5. ✅ If successful, you're logged in!

---

## 📋 Alternative Method: SQL Script (If Above Doesn't Work)

If you can't access Supabase SQL Editor, here's the full SQL script to run:

```sql
-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    username VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Create Companies table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    org_number VARCHAR,
    address VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Bank Accounts table
CREATE TABLE IF NOT EXISTS bank_accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR NOT NULL,
    account_name VARCHAR,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Drivers table
CREATE TABLE IF NOT EXISTS drivers (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    driver_id VARCHAR(4) NOT NULL,
    commission_percentage FLOAT DEFAULT 45.0,
    bank_account_id INTEGER REFERENCES bank_accounts(id),
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Templates table
CREATE TABLE IF NOT EXISTS templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    template_type VARCHAR NOT NULL,
    columns JSONB NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Shift Reports table
CREATE TABLE IF NOT EXISTS shift_reports (
    id SERIAL PRIMARY KEY,
    driver_id INTEGER REFERENCES drivers(id),
    file_name VARCHAR NOT NULL,
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data JSONB NOT NULL,
    summary JSONB,
    pdf_path VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Shift Edits table
CREATE TABLE IF NOT EXISTS shift_edits (
    id SERIAL PRIMARY KEY,
    shift_report_id INTEGER REFERENCES shift_reports(id) ON DELETE CASCADE,
    row_index INTEGER NOT NULL,
    column_name VARCHAR NOT NULL,
    old_value VARCHAR,
    new_value VARCHAR NOT NULL,
    note TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Salary Reports table
CREATE TABLE IF NOT EXISTS salary_reports (
    id SERIAL PRIMARY KEY,
    driver_id INTEGER REFERENCES drivers(id) NOT NULL,
    report_period VARCHAR,
    file_names JSONB,
    gross_salary FLOAT,
    commission_percentage FLOAT,
    net_salary FLOAT,
    cash_amount FLOAT,
    tips FLOAT,
    data JSONB NOT NULL,
    pdf_path VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT 'Tables created successfully!' as status;
```

---

## 🔍 Why This Happens

**Serverless Functions:**
- Have limited execution time (10-30 seconds)
- Cold starts need to be fast
- Creating 8 database tables on cold start = too slow
- Function times out → crashes with 500 error

**Solution:**
- Create tables once in Supabase
- App just uses existing tables
- Cold starts are fast → no crashes!

---

## ❌ Troubleshooting

### Still getting 500 error after creating tables?

**Check Vercel Logs:**
1. Vercel → Deployments → Click latest deployment
2. Click **"View Function Logs"**
3. Look for error messages
4. Share the error if you need help

**Common Issues:**

1. **DATABASE_URL wrong:**
   - Must start with `postgresql://` (not `postgres://`)
   - Must use pooler port `:6543` (not `:5432`)
   - Check for typos in password

2. **Tables not created:**
   - Verify in Supabase Table Editor
   - Try running SQL script again

3. **Environment variables not set:**
   - Check Settings → Environment Variables in Vercel
   - Make sure all 7 variables are set
   - Redeploy after setting variables

### How to check if tables exist:

**In Supabase:**
1. Dashboard → Your project
2. Click "Table Editor"
3. Should see 8 tables listed

**Or run this SQL:**
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

---

## 📊 Summary

**What you're doing:**
1. ✅ Create database tables in Supabase (one time)
2. ✅ Redeploy backend in Vercel
3. ✅ Backend uses existing tables (fast!)
4. ✅ No more crashes!

**Key Files:**
- `init_database.sql` - Complete SQL script
- `create_tables.py` - Python script (for local testing)
- This guide - Step-by-step instructions

Once the tables exist, your app will work perfectly! 🎉

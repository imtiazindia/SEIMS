# Supabase IPv4 Connection Fix

## The Problem

Your Supabase database only provides IPv6 connectivity, but your network/Python environment cannot resolve or connect via IPv6. Supabase recommends using the **Session Pooler** for IPv4 networks.

## Solution: Get Session Pooler Connection String

The Session Pooler connection string from Supabase dashboard is different from the direct connection string. Follow these steps:

### Step 1: Get Session Pooler Connection String

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **Database**
3. Scroll down to **Connection string** section
4. Look for **"Session mode"** or **"Connection Pooler"** tab
5. Select **"Session mode"** (not Transaction mode)
6. Copy the connection string - it should look like:
   ```
   postgresql://postgres.cyhjecbsjlpplvlrnqya:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
   OR
   ```
   postgresql://postgres.cyhjecbsjlpplvlrnqya:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
   ```

**Important:** The Session Pooler uses a **different hostname** (usually `*.pooler.supabase.com` or `aws-0-*.pooler.supabase.com`) that has IPv4 support!

### Step 2: Update .env File

Replace the connection string in your `.env` file with the Session Pooler connection string:

```env
DATABASE_URL=postgresql://postgres.cyhjecbsjlpplvlrnqya:09DEC2025@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
SECRET_KEY=Dj6PM0CW90SUetGjgL2vdAqQH9Asq0UjoSdEsqLZdUQ=
```

**Note:** 
- Replace `aws-0-us-east-1.pooler.supabase.com` with your actual pooler hostname
- The username format might be `postgres.cyhjecbsjlpplvlrnqya` instead of just `postgres`
- Port can be `6543` (Session mode) or `5432` (Transaction mode)

### Step 3: Test Connection

```bash
python test_database_connection.py
```

## Alternative: If Pooler Hostname Not Available

If you can't find the pooler connection string:

1. **Check Supabase Dashboard** - Look for "Connection Pooling" or "Pooler" settings
2. **Contact Supabase Support** - They can provide the IPv4-compatible connection string
3. **Purchase IPv4 Add-on** - Supabase offers IPv4 add-on for projects that need it

## Connection String Format

Session Pooler connection strings typically use:
- **Hostname:** `*.pooler.supabase.com` or `aws-0-*.pooler.supabase.com`
- **Port:** `6543` (Session mode) or `5432` (Transaction mode)
- **Username:** `postgres.PROJECT_REF` (includes project reference)
- **Database:** `postgres`
- **SSL:** Always required (`?sslmode=require`)

## Why This Works

The Session Pooler hostname resolves to IPv4 addresses, which your network and Python can connect to, while the direct connection (`db.xxxxx.supabase.co`) only resolves to IPv6.


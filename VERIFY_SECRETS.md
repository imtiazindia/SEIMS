# Verify Your Streamlit Secrets Configuration

## The Problem
If you're still seeing "connection to localhost" errors, it means your secrets aren't being read correctly.

## Quick Check

Run this diagnostic script:
```bash
python check_config.py
```

This will show you:
- What's in your `.env` file (if running locally)
- What Streamlit secrets are available
- What DATABASE_URL is actually being used

## For Streamlit Cloud

### Step 1: Verify Secrets Format

Go to your Streamlit Cloud app → Settings → Secrets

Your secrets file should look **exactly** like this (NO quotes around values):

```toml
[secrets]
DATABASE_URL = postgresql://postgres:09DEC2025@db.cyhjecbsjlpplvlrnqya.supabase.co:5432/postgres
SECRET_KEY = Dj6PM0CW90SUetGjgL2vdAqQH9Asq0UjoSdEsqLZdUQ=
```

**Common Mistakes:**
- ❌ `DATABASE_URL = "postgresql://..."` (quotes - WRONG!)
- ✅ `DATABASE_URL = postgresql://...` (no quotes - CORRECT!)

### Step 2: Check for Extra Spaces

Make sure there are no extra spaces:
- ❌ `DATABASE_URL =  postgresql://...` (extra space after =)
- ✅ `DATABASE_URL = postgresql://...` (single space)

### Step 3: Verify Connection String

Your connection string should be:
```
postgresql://postgres:09DEC2025@db.cyhjecbsjlpplvlrnqya.supabase.co:5432/postgres
```

Breakdown:
- Protocol: `postgresql://`
- Username: `postgres`
- Password: `09DEC2025`
- Host: `db.cyhjecbsjlpplvlrnqya.supabase.co`
- Port: `5432`
- Database: `postgres`

### Step 4: Restart Your App

After updating secrets:
1. Go to your app in Streamlit Cloud
2. Click the "⋮" menu (three dots)
3. Click "Reboot app"
4. Wait for it to restart

### Step 5: Check the Error Message

The new error message will show you:
- What DATABASE_URL is actually being used
- Where it's trying to connect

If it shows `localhost`, your secrets aren't being read.

## For Local Development

If you're testing locally, create a `.env` file:

```
DATABASE_URL=postgresql://postgres:09DEC2025@db.cyhjecbsjlpplvlrnqya.supabase.co:5432/postgres
SECRET_KEY=Dj6PM0CW90SUetGjgL2vdAqQH9Asq0UjoSdEsqLZdUQ=
```

**Note:** No quotes in `.env` file either!

## Testing

1. Run the diagnostic: `python check_config.py`
2. Check what DATABASE_URL it shows
3. If it shows localhost, your secrets/env vars aren't being read

## Still Not Working?

1. **Double-check the secrets format** - No quotes!
2. **Check for typos** - Copy-paste the connection string exactly
3. **Restart the app** - Changes require a restart
4. **Check Streamlit Cloud logs** - Look for error messages
5. **Verify Supabase** - Make sure your database is running and accessible


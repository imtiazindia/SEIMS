# Update Streamlit Cloud Secrets for Database Connection

## The Problem
Your Streamlit Cloud app is trying to connect to `localhost` instead of your Supabase database. This means the secrets aren't configured correctly in Streamlit Cloud.

## Solution: Update Streamlit Cloud Secrets

### Step 1: Go to Streamlit Cloud Dashboard

1. Go to [share.streamlit.io](https://share.streamlit.io) and log in
2. Click on your SEIMS app
3. Click on the **Settings** (⚙️) icon in the top right
4. Click on **Secrets** in the left sidebar

### Step 2: Update or Add Secrets

In the secrets editor, add or update the following:

```toml
[secrets]
DATABASE_URL = postgresql://postgres.cyhjecbsjlpplvlrnqya:09DEC2025@aws-1-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require
SECRET_KEY = Dj6PM0CW90SUetGjgL2vdAqQH9Asq0UjoSdEsqLZdUQ=
```

**CRITICAL FORMATTING RULES:**
- ✅ **NO quotes** around the values
- ✅ **Single space** after the `=` sign
- ✅ **One line** per secret (no line breaks)
- ✅ **Exact connection string** as shown above

### Step 3: Save and Restart

1. Click **Save** at the bottom
2. Go back to your app
3. Click the **⋮** (three dots) menu in the top right
4. Click **Reboot app**
5. Wait for the app to restart (30-60 seconds)

### Step 4: Verify Connection

After restarting, the app should now connect to your Supabase database instead of localhost.

## Connection String Details

Your Session Pooler connection string:
```
postgresql://postgres.cyhjecbsjlpplvlrnqya:09DEC2025@aws-1-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require
```

Breakdown:
- **Protocol:** `postgresql://`
- **Username:** `postgres.cyhjecbsjlpplvlrnqya` (includes project reference)
- **Password:** `09DEC2025`
- **Host:** `aws-1-ap-south-1.pooler.supabase.com` (Session Pooler with IPv4 support)
- **Port:** `5432` (Session mode)
- **Database:** `postgres`
- **SSL:** `?sslmode=require` (required for Supabase)

## Common Mistakes to Avoid

❌ **WRONG:**
```toml
DATABASE_URL = "postgresql://..."  # Quotes - WRONG!
```

✅ **CORRECT:**
```toml
DATABASE_URL = postgresql://...  # No quotes - CORRECT!
```

❌ **WRONG:**
```toml
DATABASE_URL=postgresql://...  # No space after = - might work but inconsistent
```

✅ **CORRECT:**
```toml
DATABASE_URL = postgresql://...  # Space after = - CORRECT!
```

## Troubleshooting

### Still seeing "localhost" error?

1. **Check secrets format** - Make sure no quotes and correct spacing
2. **Reboot the app** - Changes require a restart
3. **Check Streamlit Cloud logs** - Look for error messages
4. **Verify connection string** - Copy-paste exactly from this guide

### Connection timeout?

1. **Check Supabase project status** - Make sure it's not paused
2. **Verify pooler is enabled** - Check Supabase dashboard
3. **Try port 6543** - Some regions use different ports

## Testing Locally

Your local `.env` file is already configured correctly. Test locally with:
```bash
python test_database_connection.py
```

If local test passes but Streamlit Cloud fails, the issue is with Streamlit Cloud secrets configuration.


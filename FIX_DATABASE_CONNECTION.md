# Fix Database Connection Error

## The Problem
Your app is trying to connect to `localhost` instead of your Supabase database.

## The Solution

### For Streamlit Cloud:

The issue is that Streamlit Cloud reads secrets differently. We need to update the settings to read from Streamlit's secrets.

### Step 1: Update settings.py to read from Streamlit secrets

The current `settings.py` reads from environment variables, but Streamlit Cloud uses `st.secrets`.

### Step 2: Verify Secrets in Streamlit Cloud

1. Go to your Streamlit Cloud app
2. Click Settings (⚙️) → Secrets
3. Make sure you have:

```toml
[secrets]
DATABASE_URL = "postgresql://postgres:90DEC2025@db.xxxxx.supabase.co:5432/postgres"
SECRET_KEY = "Dj6PM0CW90SUetGjgL2vdAqQH9Asq0UjoSdEsqLZdUQ="
```

**Important:** 
- Replace `db.xxxxx.supabase.co` with your actual Supabase host
- Make sure there are NO quotes around the values in the secrets file
- The format should be exactly as shown above

### Step 3: Update the code to read from Streamlit secrets

I'll update the settings.py file to properly read from Streamlit Cloud secrets.


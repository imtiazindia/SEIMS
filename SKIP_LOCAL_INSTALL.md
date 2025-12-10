# Skip Local Installation - Deploy Directly to Streamlit Cloud

## ✅ Good News!

You don't need to install `psycopg2-binary` locally! Streamlit Cloud will handle it automatically.

## 🚀 Quick Deployment Steps

### Step 1: Set Up Database in Supabase

1. **Go to Supabase SQL Editor:**
   - Open your Supabase project
   - Click "SQL Editor" in the left sidebar
   - Click "New query"

2. **Run the setup script:**
   - Copy the contents of `database_setup.sql`
   - Paste into SQL Editor
   - Click "Run" (or press Ctrl+Enter)
   - Wait for "Success" message

3. **Create admin user:**
   - Run `python create_admin.py` locally (with `DATABASE_URL` set) and follow prompts
   - Or create via Supabase SQL Editor using your own bcrypt hash (fields mirror `create_admin.py`)

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit: https://share.streamlit.io
   - Sign in with GitHub

2. **Deploy your app:**
   - Click "New app"
   - Repository: `imtiazindia/SEIMS`
   - Branch: `main`
   - Main file: `app.py`
   - Click "Deploy"

3. **Wait for deployment:**
   - Streamlit Cloud will automatically:
     - Install all dependencies (including psycopg2-binary)
     - Set up the environment
     - Deploy your app

### Step 3: Verify Secrets Are Set

1. In Streamlit Cloud, go to your app
2. Click Settings (⚙️) → Secrets
3. Verify you have:
   ```toml
   [secrets]
   DATABASE_URL = "postgresql://postgres:90DEC2025@db.xxxxx.supabase.co:5432/postgres"
   SECRET_KEY = "Dj6PM0CW90SUetGjgL2vdAqQH9Asq0UjoSdEsqLZdUQ="
   ```

### Step 4: Test Your App

1. Go to your Streamlit Cloud app URL
2. You should see the login page
3. Log in with:
   - Email: `admin@seims.edu`
   - Password: (the one you used to generate the hash)

## 📝 What About Local Development?

If you want to develop locally later:

### Option 1: Use Docker
- Run PostgreSQL in Docker
- Install dependencies in container

### Option 2: Install PostgreSQL Locally
- Download from: https://www.postgresql.org/download/windows/
- This provides `pg_config` needed for psycopg2-binary

### Option 3: Use WSL (Windows Subsystem for Linux)
- Install WSL2
- Install Python and dependencies in Linux environment

### Option 4: Just Use Streamlit Cloud
- Develop directly on Streamlit Cloud
- Use GitHub for version control
- Test changes by pushing to GitHub

## 🎯 Recommended Workflow

1. **For now:** Deploy to Streamlit Cloud and test there
2. **For development:** Make changes locally, push to GitHub
3. **Streamlit Cloud auto-deploys** when you push changes

## ✅ Checklist

- [ ] Database tables created in Supabase (run database_setup.sql)
- [ ] Admin user created (run `python create_admin.py`)
- [ ] App deployed to Streamlit Cloud
- [ ] Secrets configured in Streamlit Cloud
- [ ] App loads successfully
- [ ] Can log in with admin credentials

## 🐛 Troubleshooting

### App won't start
- Check Streamlit Cloud logs
- Verify secrets are correct
- Check database connection

### Can't log in
- Verify admin user exists in database
- Check password hash is correct
- Try creating admin user again

### Database connection errors
- Verify DATABASE_URL in secrets
- Check Supabase database is running
- Test connection in Supabase dashboard

## 🎉 You're All Set!

Once deployed, you can:
- Access your app from anywhere
- Make changes and push to GitHub
- Streamlit Cloud auto-updates
- No local installation needed!


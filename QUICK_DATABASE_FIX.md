# Quick Database Connection Fix

## The Problem
Your app is trying to connect to `localhost:5432` but PostgreSQL is not running locally.

## Quick Solution (Choose One)

### Option 1: Use Supabase (Recommended - 2 minutes)

1. **Go to [supabase.com](https://supabase.com)** and sign up (free)

2. **Create a new project:**
   - Click "New Project"
   - Name: SEIMS
   - Set a database password (save it!)
   - Choose region
   - Wait 2-3 minutes for setup

3. **Get your connection string:**
   - Go to Settings → Database
   - Scroll to "Connection string"
   - Click "URI" tab
   - Copy the connection string
   - Replace `[YOUR-PASSWORD]` with your actual password

4. **Update your `.env` file:**
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
   SECRET_KEY=your-random-secret-key-here
   ```

5. **Run the database setup:**
   - Go to Supabase → SQL Editor
   - Copy contents of `database_setup.sql`
   - Paste and run it

### Option 2: Use Railway (2 minutes)

1. **Go to [railway.app](https://railway.app)** and sign up with GitHub

2. **Create PostgreSQL:**
   - Click "New Project"
   - Click "Provision PostgreSQL"
   - Wait 1 minute

3. **Get connection string:**
   - Click on PostgreSQL service
   - Go to Variables tab
   - Copy `DATABASE_URL`

4. **Update your `.env` file** with the connection string

### Option 3: Install Local PostgreSQL (10-15 minutes)

**Windows:**
1. Download from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Install and remember the password
3. Start PostgreSQL service (Win+R → `services.msc` → find PostgreSQL → Start)
4. Create database:
   ```sql
   psql -U postgres
   CREATE DATABASE seims_db;
   \q
   ```
5. Update `.env`:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/seims_db
   ```

## After Setup

1. **Test the connection:**
   ```bash
   python test_database_connection.py
   ```

2. **If successful, run your app:**
   ```bash
   streamlit run app.py
   ```

## Need Help?

- See `DATABASE_SETUP.md` for detailed instructions
- See `TROUBLESHOOTING_CONNECTION.md` for common issues


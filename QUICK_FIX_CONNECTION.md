# Quick Fix: Database Connection Error

## The Problem
You're seeing: `connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused`

This means PostgreSQL is not running or not accessible.

---

## Fastest Solution: Use a Cloud Database (5 minutes)

### Step 1: Get a Free Supabase Database

1. Go to [supabase.com](https://supabase.com) and sign up (free)
2. Click "New Project"
3. Create a project (takes 2-3 minutes)
4. Go to **Settings** → **Database**
5. Copy the connection string (URI format)
6. Replace `[YOUR-PASSWORD]` with your actual password

### Step 2: Create .env File

Create a file named `.env` in your project root (`d:\SEIMS\SEIMS\.env`):

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

Replace:
- `YOUR_PASSWORD` with your Supabase password
- `db.xxxxx.supabase.co` with your actual Supabase host

### Step 3: Test Connection

Run:
```bash
python test_database_connection.py
```

You should see: `✅ Database connection test PASSED!`

---

## Alternative: Start Local PostgreSQL

If you have PostgreSQL installed locally:

### Windows:
1. Press `Win + R`
2. Type `services.msc` and press Enter
3. Find `postgresql-x64-XX` service
4. Right-click → **Start**
5. Set Startup Type to **Automatic**

### Then create `.env` file:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/seims_db
```

---

## Need More Help?

- See `TROUBLESHOOTING_CONNECTION.md` for detailed solutions
- See `DATABASE_SETUP.md` for complete setup guide
- Run `python test_database_connection.py` to diagnose issues


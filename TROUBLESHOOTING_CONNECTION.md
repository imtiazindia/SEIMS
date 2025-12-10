# Troubleshooting Database Connection Errors

## Error: "Connection refused" or "Cannot connect to server"

This error means your application cannot connect to PostgreSQL. Here's how to fix it:

---

## Quick Diagnosis

Use one of these quick checks:

- Launch the app (`streamlit run app.py`); the top banner shows configuration/connection status and any errors.
- Or run a lightweight diagnostic:
  ```bash
  python - <<'PY'
  import json
  from src.utils.diagnostics import run_diagnostics
  print(json.dumps(run_diagnostics(), indent=2))
  PY
  ```
  This reports whether config and database connectivity are OK and includes error details.

---

## Solution 1: Using a Cloud Database (Recommended)

The easiest solution is to use a cloud PostgreSQL database. You don't need to install or run anything locally.

### Option A: Supabase (Free Tier)

1. **Create account**: Go to [supabase.com](https://supabase.com) and sign up
2. **Create project**: Click "New Project" and follow the setup
3. **Get connection string**:
   - Go to Settings → Database
   - Copy the connection string (URI format)
   - Replace `[YOUR-PASSWORD]` with your actual password
4. **Configure locally**: Create a `.env` file in your project root:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
   ```

### Option B: Railway (Free Tier)

1. **Create account**: Go to [railway.app](https://railway.app) and sign up
2. **Create PostgreSQL**: Click "New Project" → "Provision PostgreSQL"
3. **Get connection string**: Go to Variables tab, copy `DATABASE_URL`
4. **Configure locally**: Add to `.env` file

See `DATABASE_SETUP.md` for detailed instructions.

---

## Solution 2: Using Local PostgreSQL

If you want to use PostgreSQL on your computer:

### Step 1: Install PostgreSQL

**Windows:**
1. Download from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Run the installer
3. Remember the password you set for the `postgres` user

**Mac:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Step 2: Start PostgreSQL Service

**Windows:**
1. Press `Win + R`, type `services.msc`, press Enter
2. Find `postgresql-x64-XX` (version number may vary)
3. Right-click → Start (if not running)
4. Set Startup Type to "Automatic" (so it starts on boot)

**Mac/Linux:**
```bash
# Check if running
pg_isready

# Start if not running
brew services start postgresql  # Mac
# OR
sudo systemctl start postgresql  # Linux
```

### Step 3: Create Database

Open a terminal/command prompt and run:

```bash
# Connect to PostgreSQL
psql -U postgres

# In PostgreSQL prompt, run:
CREATE DATABASE seims_db;

# Exit
\q
```

### Step 4: Configure Connection

Create a `.env` file in your project root:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/seims_db
```

Replace `YOUR_PASSWORD` with the password you set during installation.

---

## Solution 3: Verify Your Configuration

### Check if .env file exists

Make sure you have a `.env` file in the project root with:

```
DATABASE_URL=your_connection_string_here
```

### Verify Connection String Format

The connection string should be in this format:

```
postgresql://username:password@host:port/database
```

Examples:
- Local: `postgresql://postgres:mypassword@localhost:5432/seims_db`
- Supabase: `postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres`
- Railway: `postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway`

### Common Issues

1. **Password with special characters**: URL-encode special characters
   - `@` becomes `%40`
   - `#` becomes `%23`
   - `%` becomes `%25`
   - etc.

2. **Wrong port**: Default PostgreSQL port is `5432`

3. **Wrong host**: 
   - Local: `localhost` or `127.0.0.1`
   - Cloud: Use the exact host from your provider

---

## Testing Your Connection

### Method 1: Quick diagnostic

```bash
python - <<'PY'
import json
from src.utils.diagnostics import run_diagnostics
print(json.dumps(run_diagnostics(), indent=2))
PY
```

### Method 2: Test manually

```python
from src.database.connection import get_db_session

try:
    with get_db_session() as session:
        result = session.execute("SELECT 1")
        print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

---

## Still Having Issues?

1. **Check firewall**: Make sure port 5432 is not blocked
2. **Check PostgreSQL logs**: Look for error messages
3. **Verify credentials**: Double-check username and password
4. **Try cloud database**: Use Supabase or Railway instead of local setup
5. **Check network**: For cloud databases, ensure you have internet connection

---

## For Streamlit Cloud Deployment

If deploying to Streamlit Cloud:

1. Go to your app settings
2. Click "Secrets"
3. Add:

```toml
[secrets]
DATABASE_URL = "postgresql://postgres:password@host:port/database"
SECRET_KEY = "your-secret-key-here"
```

**Important**: No quotes around values in the secrets file!

---

## Need More Help?

- See `DATABASE_SETUP.md` for detailed setup instructions
- Check PostgreSQL documentation: [postgresql.org/docs](https://www.postgresql.org/docs/)
- Supabase docs: [supabase.com/docs](https://supabase.com/docs)
- Railway docs: [docs.railway.app](https://docs.railway.app)



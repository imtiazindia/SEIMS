# Database Setup Guide for SEIMS

## Option 1: Supabase (Recommended - Free Tier)

### Step 1: Create Supabase Account
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project" or "Sign up"
3. Sign up with GitHub, Google, or email
4. Verify your email if required

### Step 2: Create a New Project
1. After logging in, click "New Project"
2. Fill in the details:
   - **Name**: SEIMS (or your preferred name)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to you
   - **Pricing Plan**: Free tier is sufficient to start
3. Click "Create new project"
4. Wait 2-3 minutes for the project to be created

### Step 3: Get Your Connection String
1. Go to your project dashboard
2. Click on **Settings** (gear icon) in the left sidebar
3. Click on **Database** under Project Settings
4. Scroll down to **Connection string**
5. Select **URI** tab
6. Copy the connection string - it will look like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
7. **Important**: Replace `[YOUR-PASSWORD]` with the password you created in Step 2

### Step 4: Use in Streamlit Cloud
1. Go to your Streamlit Cloud app settings
2. Add this to Secrets:
   ```toml
   [secrets]
   DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres"
   SECRET_KEY = "your-secret-key-here"
   ```

---

## Option 2: Railway (Free Tier Available)

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Verify your account

### Step 2: Create PostgreSQL Database
1. Click "New Project"
2. Click "Provision PostgreSQL"
3. Railway will create a PostgreSQL database automatically
4. Wait for it to provision (takes ~1 minute)

### Step 3: Get Connection String
1. Click on your PostgreSQL service
2. Go to the **Variables** tab
3. Find `DATABASE_URL` or `POSTGRES_URL`
4. Copy the connection string
5. It will look like:
   ```
   postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway
   ```

### Step 4: Use in Streamlit Cloud
Add to Streamlit Cloud secrets as shown above.

---

## Option 3: AWS RDS (Paid but Reliable)

### Step 1: Create AWS Account
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Sign up for AWS account (requires credit card, but free tier available)
3. Navigate to RDS service

### Step 2: Create PostgreSQL Database
1. Click "Create database"
2. Choose "PostgreSQL"
3. Select "Free tier" template
4. Configure:
   - DB instance identifier: `seims-db`
   - Master username: `postgres` (or your choice)
   - Master password: Create strong password
5. Click "Create database"
6. Wait 5-10 minutes for creation

### Step 3: Get Connection String
1. Click on your database instance
2. Find "Endpoint" - this is your host
3. Connection string format:
   ```
   postgresql://postgres:YOUR_PASSWORD@your-endpoint.region.rds.amazonaws.com:5432/postgres
   ```

---

## Option 4: Local PostgreSQL (For Development Only)

### Step 1: Install PostgreSQL
**Windows:**
1. Download from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Run installer
3. Remember the password you set for `postgres` user

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

### Step 2: Create Database
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE seims_db;

-- Create user (optional)
CREATE USER seims_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE seims_db TO seims_user;
```

### Step 3: Connection String
```
postgresql://postgres:your_password@localhost:5432/seims_db
```

**Note:** Local database won't work with Streamlit Cloud. Use for local development only.

---

## Quick Setup Checklist

- [ ] Choose a database provider (Supabase recommended)
- [ ] Create account and project
- [ ] Get connection string
- [ ] Replace password in connection string
- [ ] Add to Streamlit Cloud secrets
- [ ] Test connection

---

## Testing Your Connection

After setting up, you can test the connection locally:

1. Create a `.env` file in your project:
   ```
   DATABASE_URL=your_connection_string_here
   ```

2. Test connection:
   ```python
   from src.database.connection import get_db_session
   
   try:
       with get_db_session() as session:
           session.execute("SELECT 1")
       print("✅ Database connection successful!")
   except Exception as e:
       print(f"❌ Connection failed: {e}")
   ```

---

## Security Notes

1. **Never commit** your actual connection string to Git
2. Always use environment variables or secrets
3. Use strong passwords (16+ characters, mixed case, numbers, symbols)
4. For production, consider:
   - Connection pooling
   - SSL/TLS encryption
   - IP whitelisting (if supported)
   - Regular backups

---

## Troubleshooting

### Connection Refused
- Check if database is running
- Verify host and port are correct
- Check firewall settings

### Authentication Failed
- Verify username and password
- Check if user has proper permissions
- Ensure password doesn't contain special characters that need URL encoding

### Database Not Found
- Verify database name is correct
- Check if database exists
- Ensure you're connecting to the right database

### SSL Required
Some providers require SSL. Add `?sslmode=require` to connection string:
```
postgresql://user:pass@host:port/db?sslmode=require
```


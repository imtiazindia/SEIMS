# Next Steps After Setting Up Secrets

## ✅ What You've Completed
- [x] Secrets configured in Streamlit Cloud
- [x] DATABASE_URL set
- [x] SECRET_KEY set

## 🔄 Next Steps

### Step 1: Verify Streamlit Cloud Deployment
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Check your app status
3. If there are errors, check the logs:
   - Click on your app
   - Click "⋮" (three dots) → "View app logs"
   - Look for any error messages

### Step 2: Set Up Database Tables
You need to run database migrations to create the tables. Options:

#### Option A: Using Streamlit Cloud Shell (If Available)
1. In Streamlit Cloud, go to your app
2. Look for "Shell" or "Terminal" option
3. Run:
   ```bash
   alembic upgrade head
   ```

#### Option B: Run Migrations Locally (Recommended)
1. Install dependencies locally:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your database URL:
   ```
   DATABASE_URL=postgresql://postgres:90DEC2025@db.xxxxx.supabase.co:5432/postgres
   SECRET_KEY=Dj6PM0CW90SUetGjgL2vdAqQH9Asq0UjoSdEsqLZdUQ=
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

#### Option C: Use Database Management Tool
- Use pgAdmin, DBeaver, or Supabase SQL Editor
- Run the SQL from migration files manually

### Step 3: Create First Admin User
After tables are created, you need to create the first admin user.

#### Option A: Using Python Script
Create a file `create_admin.py`:

```python
from src.database.connection import get_db_session
from src.database.models import User
from src.auth.authenticator import get_password_hash

# Admin user details
admin_email = "admin@seims.edu"
admin_password = "ChangeThisPassword123!"  # Change this!
admin_name = "System Administrator"

with get_db_session() as session:
    # Check if admin already exists
    existing = session.query(User).filter(User.email == admin_email).first()
    if existing:
        print("Admin user already exists!")
    else:
        admin = User(
            email=admin_email,
            password_hash=get_password_hash(admin_password),
            name=admin_name,
            role="admin",
            is_active=True
        )
        session.add(admin)
        session.commit()
        print(f"✅ Admin user created!")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("⚠️  Please change the password after first login!")
```

Run it:
```bash
python create_admin.py
```

#### Option B: Direct SQL (Using Supabase SQL Editor)
1. Go to Supabase → Your Project → SQL Editor
2. Run this SQL (replace password hash):

```sql
-- First, generate password hash using Python:
-- python -c "from passlib.context import CryptContext; ctx = CryptContext(schemes=['bcrypt']); print(ctx.hash('YourPassword123!'))"

INSERT INTO users (email, password_hash, name, role, is_active, created_at)
VALUES (
    'admin@seims.edu',
    '$2b$12$...',  -- Replace with bcrypt hash of your password
    'System Administrator',
    'admin',
    true,
    NOW()
);
```

### Step 4: Test Your Application
1. Go to your Streamlit Cloud app URL
2. You should see the login page
3. Try logging in with your admin credentials
4. If login works, you'll see the dashboard

### Step 5: Verify Everything Works
- [ ] App loads without errors
- [ ] Login page appears
- [ ] Can log in with admin credentials
- [ ] Dashboard displays
- [ ] Can navigate between pages
- [ ] No database connection errors

## 🐛 Troubleshooting

### Error: "No module named 'src'"
**Solution:** Make sure your app structure is correct. The `src` folder should be in the root directory.

### Error: "Could not connect to database"
**Solution:**
- Verify DATABASE_URL in secrets is correct
- Check if password needs URL encoding (special characters)
- Ensure Supabase database is running
- Check firewall/network settings

### Error: "Table 'users' does not exist"
**Solution:** Run database migrations first (Step 2)

### Error: "Invalid email or password"
**Solution:** 
- Verify admin user was created
- Check password hash is correct
- Try creating admin user again

### App shows "Please log in" but login doesn't work
**Solution:**
- Check database connection
- Verify user exists in database
- Check authentication code for errors

## 📝 Quick Checklist

- [ ] Secrets saved in Streamlit Cloud
- [ ] Database migrations run
- [ ] Admin user created
- [ ] App loads successfully
- [ ] Can log in
- [ ] Pages are accessible

## 🎉 Once Everything Works

You can now:
1. Create more users through Admin Panel (once implemented)
2. Start adding students
3. Create IEPs
4. Log sessions
5. Generate reports

## 📚 Need Help?

- Check Streamlit Cloud logs for errors
- Review database connection in Supabase
- Verify all files are pushed to GitHub
- Check that secrets are correctly formatted


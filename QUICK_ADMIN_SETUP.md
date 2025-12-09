# Quick Admin User Setup for Supabase

## Step 1: Generate Password Hash

1. Go to: **https://bcrypt-generator.com/**
2. Enter your desired password (e.g., `Admin123!`)
3. Click **"Generate Hash"**
4. **Copy the hash** (it will look like: `$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqBWVHxkd0`)

## Step 2: Run SQL in Supabase

1. Go to your **Supabase project**
2. Click **"SQL Editor"** in the left sidebar
3. Click **"New query"**
4. Copy and paste this SQL (replace the hash with yours):

```sql
INSERT INTO users (email, password_hash, name, role, is_active, created_at)
VALUES (
    'admin@seims.edu',
    'PASTE_YOUR_BCRYPT_HASH_HERE',  -- Replace this with the hash from Step 1
    'System Administrator',
    'admin',
    true,
    CURRENT_TIMESTAMP
)
ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    is_active = true;
```

5. **Replace** `PASTE_YOUR_BCRYPT_HASH_HERE` with your actual hash from Step 1
6. Click **"Run"** (or press Ctrl+Enter)

## Step 3: Verify

After running, you should see a result showing the admin user was created.

## Step 4: Test Login

1. Go to your Streamlit Cloud app
2. Log in with:
   - **Email:** `admin@seims.edu`
   - **Password:** (the password you used in Step 1)

---

## Example (Don't use this exact hash - generate your own!)

If your password is `Admin123!`, your hash might look like:
```
$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqBWVHxkd0
```

So your SQL would be:
```sql
INSERT INTO users (email, password_hash, name, role, is_active, created_at)
VALUES (
    'admin@seims.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqBWVHxkd0',
    'System Administrator',
    'admin',
    true,
    CURRENT_TIMESTAMP
)
ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    is_active = true;
```

---

## Troubleshooting

### Error: "syntax error"
- Make sure all quotes are correct (single quotes `'` not double quotes `"`)
- Make sure the hash is in single quotes
- Check there are no extra spaces or characters

### Error: "relation users does not exist"
- Run `database_setup.sql` first to create the tables

### User already exists
- The SQL uses `ON CONFLICT` so it will update if the user exists
- Or you can delete the existing user first:
  ```sql
  DELETE FROM users WHERE email = 'admin@seims.edu';
  ```


-- Create Admin User for SEIMS
-- Run this AFTER running database_setup.sql
-- IMPORTANT: Replace the password hash with your own!

-- First, you need to generate a password hash
-- Use Python: python -c "from passlib.context import CryptContext; ctx = CryptContext(schemes=['bcrypt']); print(ctx.hash('YourPassword123!'))"
-- Or use online bcrypt generator: https://bcrypt-generator.com/

-- Example admin user creation
-- Replace 'YOUR_BCRYPT_HASH' with the actual hash of your password
INSERT INTO users (email, password_hash, name, role, is_active, created_at)
VALUES (
    'admin@seims.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqBWVHxkd0',  -- Replace with your bcrypt hash
    'System Administrator',
    'admin',
    true,
    CURRENT_TIMESTAMP
)
ON CONFLICT (email) DO NOTHING;

-- Verify the user was created
SELECT user_id, email, name, role, is_active, created_at 
FROM users 
WHERE email = 'admin@seims.edu';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Admin user created!';
    RAISE NOTICE '📧 Email: admin@seims.edu';
    RAISE NOTICE '⚠️  Make sure to replace the password hash with your own!';
END $$;


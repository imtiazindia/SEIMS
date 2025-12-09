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
    'imtiyaz@rckr.com',
    '$2a$12$IPQtGGaWxJ01qHzSA4eLreBHMESAK2OC1cTw2ZRyAX8/QUkDWSPmq',  -- Replace with your bcrypt hash
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


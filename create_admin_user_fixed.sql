-- Create Admin User for SEIMS
-- Run this AFTER running database_setup.sql
-- IMPORTANT: Replace the password hash with your own!

-- Step 1: Generate a password hash
-- Go to: https://bcrypt-generator.com/
-- Enter your password (e.g., "Admin123!")
-- Click "Generate Hash"
-- Copy the hash (starts with $2b$12$...)

-- Step 2: Replace the hash below with your generated hash
-- Then run this SQL in Supabase SQL Editor

INSERT INTO users (email, password_hash, name, role, is_active, created_at)
VALUES (
    'imtiyaz@rckr.com',
    '$2b$12$fPUU46cHSpV/pNQRFTQ3GOFSodfEyhmVZtzE8RLV8OkA./GmPPFMq',  -- REPLACE THIS with your bcrypt hash from bcrypt-generator.com
    'System Administrator',
    'admin',
    true,
    CURRENT_TIMESTAMP
)
ON CONFLICT (email) DO UPDATE 
SET password_hash = EXCLUDED.password_hash,
    is_active = true;

-- Verify the user was created
SELECT user_id, email, name, role, is_active, created_at 
FROM users 
WHERE email = 'admin@seims.edu';


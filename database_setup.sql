-- SEIMS Database Setup Script
-- Run this in Supabase SQL Editor to create all tables

-- Enable UUID extension (if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,
    admission_number VARCHAR(50) UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    preferred_name VARCHAR(100),
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    nationality VARCHAR(100),
    grade VARCHAR(20),
    section VARCHAR(20),
    enrollment_date DATE NOT NULL,
    expected_graduation_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    -- Registration workflow & extended profile fields
    registration_status VARCHAR(50) DEFAULT 'draft',
    registration_step INTEGER DEFAULT 0,
    contact_info JSONB,
    academic_info JSONB,
    medical_info JSONB,
    learning_profile JSONB,
    review_status VARCHAR(50),
    review_notes TEXT,
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_students_admission ON students(admission_number);
CREATE INDEX IF NOT EXISTS idx_students_status ON students(status);
CREATE INDEX IF NOT EXISTS idx_students_registration_status ON students(registration_status);

-- Ensure new registration columns exist (for upgrades on existing databases)
ALTER TABLE students
    ADD COLUMN IF NOT EXISTS registration_status VARCHAR(50) DEFAULT 'draft',
    ADD COLUMN IF NOT EXISTS registration_step INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS contact_info JSONB,
    ADD COLUMN IF NOT EXISTS academic_info JSONB,
    ADD COLUMN IF NOT EXISTS medical_info JSONB,
    ADD COLUMN IF NOT EXISTS learning_profile JSONB,
    ADD COLUMN IF NOT EXISTS review_status VARCHAR(50),
    ADD COLUMN IF NOT EXISTS review_notes TEXT;

-- Sample student registrations for review/testing
INSERT INTO users (email, password_hash, name, role, is_active)
VALUES
    ('admin@seims.edu', '$2b$12$exampleexampleexampleexampleexampleexa', 'System Administrator', 'admin', true)
ON CONFLICT (email) DO NOTHING;

-- Draft registration (Step 2 of 6)
INSERT INTO students (
    admission_number, first_name, last_name, preferred_name,
    date_of_birth, gender, nationality,
    grade, section, enrollment_date, expected_graduation_date,
    status, registration_status, registration_step,
    contact_info, academic_info, created_by
)
VALUES (
    'S-2024-0001', 'Sarah', 'Mehta', 'Sarah',
    '2014-05-12', 'Female', 'Indian',
    '4', 'A', CURRENT_DATE, NULL,
    'pending', 'draft', 2,
    '{
        "primary_guardian": {
            "relationship": "Mother",
            "full_name": "Aisha Mehta",
            "phone": "+91-9876543210",
            "email": "aisha.mehta@example.com"
        },
        "address": {
            "line1": "12 Green Park Road",
            "city": "Bangalore",
            "state": "KA",
            "postal_code": "560001"
        },
        "emergency_contacts": [
            {"name": "Rohan Mehta", "phone": "+91-9876500001", "relationship": "Father"},
            {"name": "Neha Rao", "phone": "+91-9876500002", "relationship": "Aunt"}
        ]
    }'::jsonb,
    NULL,
    (SELECT user_id FROM users WHERE email = 'admin@seims.edu' LIMIT 1)
)
ON CONFLICT (admission_number) DO NOTHING;

-- Pending review registration (Step 6 of 6)
INSERT INTO students (
    admission_number, first_name, last_name,
    date_of_birth, gender, nationality,
    grade, section, enrollment_date,
    status, registration_status, registration_step,
    contact_info, academic_info, medical_info, learning_profile,
    review_status, created_by
)
VALUES (
    'S-2024-0002', 'Omar', 'Khan',
    '2013-09-03', 'Male', 'Indian',
    '5', 'B', CURRENT_DATE,
    'pending', 'pending_review', 6,
    '{
        "primary_guardian": {
            "relationship": "Father",
            "full_name": "Imran Khan",
            "phone": "+91-9876511111",
            "email": "imran.khan@example.com"
        }
    }'::jsonb,
    '{
        "current_enrollment": {
            "class_teacher": "Ms. Rao"
        }
    }'::jsonb,
    '{
        "conditions": [
            {
                "name": "ADHD",
                "severity": "Moderate"
            }
        ]
    }'::jsonb,
    '{
        "primary_diagnosis": "ADHD",
        "impact_level": "Moderate",
        "affected_areas": ["Attention", "Organization"]
    }'::jsonb,
    'pending',
    (SELECT user_id FROM users WHERE email = 'admin@seims.edu' LIMIT 1)
)
ON CONFLICT (admission_number) DO NOTHING;

-- Approved registration / active student
INSERT INTO students (
    admission_number, first_name, last_name,
    date_of_birth, gender, nationality,
    grade, section, enrollment_date,
    status, registration_status, registration_step,
    contact_info, academic_info, review_status, created_by
)
VALUES (
    'S-2024-0003', 'Lila', 'Singh',
    '2012-02-20', 'Female', 'Indian',
    '6', 'C', CURRENT_DATE - INTERVAL '1 year',
    'active', 'approved', 6,
    '{
        "primary_guardian": {
            "relationship": "Guardian",
            "full_name": "Rita Singh",
            "phone": "+91-9876522222"
        }
    }'::jsonb,
    '{
        "current_enrollment": {
            "class_teacher": "Mr. Sharma"
        }
    }'::jsonb,
    'approved',
    (SELECT user_id FROM users WHERE email = 'admin@seims.edu' LIMIT 1)
)
ON CONFLICT (admission_number) DO NOTHING;

-- Create learning_difficulties table
CREATE TABLE IF NOT EXISTS learning_difficulties (
    difficulty_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    difficulty_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    diagnosis_date DATE NOT NULL,
    diagnosis_code VARCHAR(50),
    diagnosing_practitioner VARCHAR(255),
    assessment_scores JSONB,
    impact_statement TEXT,
    previous_interventions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_learning_difficulties_student ON learning_difficulties(student_id);

-- Create ieps table
CREATE TABLE IF NOT EXISTS ieps (
    iep_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    academic_year VARCHAR(20) NOT NULL,
    quarter VARCHAR(20),
    status VARCHAR(50) DEFAULT 'draft',
    effective_date DATE,
    review_date DATE,
    version_number INTEGER DEFAULT 1,
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ieps_student ON ieps(student_id);
CREATE INDEX IF NOT EXISTS idx_ieps_status ON ieps(status);

-- Create goals table
CREATE TABLE IF NOT EXISTS goals (
    goal_id SERIAL PRIMARY KEY,
    iep_id INTEGER NOT NULL REFERENCES ieps(iep_id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    baseline TEXT,
    target TEXT NOT NULL,
    measurement_method TEXT,
    success_criteria TEXT,
    time_frame VARCHAR(50) NOT NULL,
    assigned_to INTEGER REFERENCES users(user_id),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_goals_iep ON goals(iep_id);
CREATE INDEX IF NOT EXISTS idx_goals_assigned ON goals(assigned_to);

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    session_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    teacher_id INTEGER NOT NULL REFERENCES users(user_id),
    iep_id INTEGER REFERENCES ieps(iep_id),
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    session_type VARCHAR(50),
    location VARCHAR(100),
    goals_addressed JSONB,
    teaching_methods JSONB,
    observations TEXT,
    progress_ratings JSONB,
    evidence_files JSONB,
    student_engagement VARCHAR(50),
    challenges_encountered TEXT,
    next_steps TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_student ON sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_sessions_teacher ON sessions(teacher_id);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(session_date);

-- Create assessments table
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    quarter VARCHAR(20) NOT NULL,
    assessment_date DATE NOT NULL,
    assessment_type VARCHAR(100) NOT NULL,
    scores JSONB,
    report_url VARCHAR(500),
    conducted_by INTEGER NOT NULL REFERENCES users(user_id),
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_assessments_student ON assessments(student_id);
CREATE INDEX IF NOT EXISTS idx_assessments_quarter ON assessments(quarter);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_students_updated_at ON students;
CREATE TRIGGER update_students_updated_at
    BEFORE UPDATE ON students
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_ieps_updated_at ON ieps;
CREATE TRIGGER update_ieps_updated_at
    BEFORE UPDATE ON ieps
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Database tables created successfully!';
    RAISE NOTICE '📝 Next step: Create an admin user (run python create_admin.py)';
END $$;


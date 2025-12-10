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
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_students_admission ON students(admission_number);
CREATE INDEX IF NOT EXISTS idx_students_status ON students(status);

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


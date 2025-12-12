"""
SQLAlchemy database models
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    created_students = relationship("Student", back_populates="created_by_user", foreign_keys="[Student.created_by]")
    created_ieps = relationship("IEP", back_populates="created_by_user")
    sessions = relationship("Session", back_populates="teacher")

class Student(Base):
    """Student model"""
    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True, index=True)
    admission_number = Column(String(50), unique=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    preferred_name = Column(String(100), nullable=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=True)
    nationality = Column(String(100), nullable=True)
    grade = Column(String(20), nullable=True)
    section = Column(String(20), nullable=True)
    enrollment_date = Column(Date, nullable=False)
    expected_graduation_date = Column(Date, nullable=True)
    status = Column(String(50), default="active")

    # Registration workflow & extended profile
    registration_status = Column(  # draft, pending_review, approved, denied
        String(50), default="draft", index=True
    )
    registration_step = Column(Integer, default=0)  # highest completed step (0–6)

    # JSON blobs for wizard steps beyond basic student fields
    contact_info = Column(JSON, nullable=True)      # guardians, address, emergency contacts
    academic_info = Column(JSON, nullable=True)     # grade/section, teachers, schedule prefs
    medical_info = Column(JSON, nullable=True)      # conditions, allergies, medications
    learning_profile = Column(JSON, nullable=True)  # diagnosis, impact areas, documents

    # Approval workflow
    internal_notes = Column(Text, nullable=True)  # Staff/department comments (not visible to parents)
    parent_notes = Column(Text, nullable=True)    # Comments visible to parents/guardians
    reviewed_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User", back_populates="created_students", foreign_keys=[created_by])
    reviewed_by_user = relationship("User", foreign_keys=[reviewed_by])
    learning_difficulties = relationship("LearningDifficulty", back_populates="student")
    ieps = relationship("IEP", back_populates="student")
    sessions = relationship("Session", back_populates="student")
    assessments = relationship("Assessment", back_populates="student")

class LearningDifficulty(Base):
    """Learning difficulty model"""
    __tablename__ = "learning_difficulties"
    
    difficulty_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    difficulty_type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    diagnosis_date = Column(Date, nullable=False)
    diagnosis_code = Column(String(50), nullable=True)
    diagnosing_practitioner = Column(String(255), nullable=True)
    assessment_scores = Column(JSON, nullable=True)
    impact_statement = Column(Text, nullable=True)
    previous_interventions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="learning_difficulties")

class IEP(Base):
    """IEP document model"""
    __tablename__ = "ieps"
    
    iep_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    academic_year = Column(String(20), nullable=False)
    quarter = Column(String(20), nullable=True)
    status = Column(String(50), default="draft")
    effective_date = Column(Date, nullable=True)
    review_date = Column(Date, nullable=True)
    version_number = Column(Integer, default=1)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="ieps")
    created_by_user = relationship("User", back_populates="created_ieps")
    goals = relationship("Goal", back_populates="iep")
    sessions = relationship("Session", back_populates="iep")

class Goal(Base):
    """IEP Goal model"""
    __tablename__ = "goals"
    
    goal_id = Column(Integer, primary_key=True, index=True)
    iep_id = Column(Integer, ForeignKey("ieps.iep_id"), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    baseline = Column(Text, nullable=True)
    target = Column(Text, nullable=False)
    measurement_method = Column(Text, nullable=True)
    success_criteria = Column(Text, nullable=True)
    time_frame = Column(String(50), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    iep = relationship("IEP", back_populates="goals")

class Session(Base):
    """Session logging model"""
    __tablename__ = "sessions"
    
    session_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    iep_id = Column(Integer, ForeignKey("ieps.iep_id"), nullable=True)
    session_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    session_type = Column(String(50), nullable=True)
    location = Column(String(100), nullable=True)
    goals_addressed = Column(JSON, nullable=True)
    teaching_methods = Column(JSON, nullable=True)
    observations = Column(Text, nullable=True)
    progress_ratings = Column(JSON, nullable=True)
    evidence_files = Column(JSON, nullable=True)
    student_engagement = Column(String(50), nullable=True)
    challenges_encountered = Column(Text, nullable=True)
    next_steps = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="sessions")
    teacher = relationship("User", back_populates="sessions")
    iep = relationship("IEP", back_populates="sessions")

class Assessment(Base):
    """Assessment model"""
    __tablename__ = "assessments"
    
    assessment_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    quarter = Column(String(20), nullable=False)
    assessment_date = Column(Date, nullable=False)
    assessment_type = Column(String(100), nullable=False)
    scores = Column(JSON, nullable=True)
    report_url = Column(String(500), nullable=True)
    conducted_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="assessments")


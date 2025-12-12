"""
Dashboard page - Role-specific dashboard with approval workflow
"""

import streamlit as st
from datetime import datetime
from src.auth.permissions import get_role_display_name, can_approve_registrations
from src.database.connection import get_db_session
from src.database.models import User, Student

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

if not st.session_state.get('authenticated'):
    st.error("Please log in to access this page.")
    st.stop()

user_role = st.session_state.get('user_role')
user_name = st.session_state.get('user_name', 'User')
user_id = st.session_state.get('user_id')

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _load_dashboard_metrics():
    """Load dashboard metrics from database"""
    with get_db_session() as session:
        total_users = session.query(User).filter(User.is_active == True).count()
        active_students = session.query(Student).filter(Student.status == 'active').count()
        pending_approvals = session.query(Student).filter(
            Student.registration_status == 'pending_review'
        ).count()
        on_hold = session.query(Student).filter(
            Student.registration_status == 'on_hold'
        ).count()
        return {
            'total_users': total_users,
            'active_students': active_students,
            'pending_approvals': pending_approvals,
            'on_hold': on_hold
        }

def _load_pending_registrations():
    """Load students pending approval"""
    with get_db_session() as session:
        students = session.query(Student).filter(
            Student.registration_status.in_(['pending_review', 'on_hold'])
        ).order_by(Student.created_at.desc()).all()
        # Detach from session to use outside
        result = []
        for s in students:
            result.append({
                'student_id': s.student_id,
                'admission_number': s.admission_number,
                'first_name': s.first_name,
                'last_name': s.last_name,
                'preferred_name': s.preferred_name,
                'date_of_birth': s.date_of_birth,
                'gender': s.gender,
                'enrollment_date': s.enrollment_date,
                'registration_status': s.registration_status,
                'registration_step': s.registration_step,
                'contact_info': s.contact_info or {},
                'academic_info': s.academic_info or {},
                'medical_info': s.medical_info or {},
                'learning_profile': s.learning_profile or {},
                'internal_notes': s.internal_notes or '',
                'parent_notes': s.parent_notes or '',
                'created_at': s.created_at,
                'created_by': s.created_by_user.name if s.created_by_user else 'Unknown'
            })
        return result

def _get_student_by_id(student_id: int):
    """Load a single student for detail view"""
    with get_db_session() as session:
        s = session.query(Student).filter(Student.student_id == student_id).first()
        if not s:
            return None
        return {
            'student_id': s.student_id,
            'admission_number': s.admission_number,
            'first_name': s.first_name,
            'last_name': s.last_name,
            'preferred_name': s.preferred_name,
            'date_of_birth': s.date_of_birth,
            'gender': s.gender,
            'enrollment_date': s.enrollment_date,
            'grade': s.grade,
            'section': s.section,
            'registration_status': s.registration_status,
            'registration_step': s.registration_step,
            'contact_info': s.contact_info or {},
            'academic_info': s.academic_info or {},
            'medical_info': s.medical_info or {},
            'learning_profile': s.learning_profile or {},
            'internal_notes': s.internal_notes or '',
            'parent_notes': s.parent_notes or '',
            'created_at': s.created_at,
            'created_by': s.created_by_user.name if s.created_by_user else 'Unknown'
        }

def _update_registration_status(student_id: int, new_status: str, internal_notes: str, parent_notes: str, reviewer_id: int):
    """Update student registration status and notes"""
    with get_db_session() as session:
        student = session.query(Student).filter(Student.student_id == student_id).first()
        if student:
            student.registration_status = new_status
            student.internal_notes = internal_notes
            student.parent_notes = parent_notes
            student.reviewed_by = reviewer_id
            student.reviewed_at = datetime.utcnow()
            # If approved, also set status to active
            if new_status == 'approved':
                student.status = 'active'
            session.commit()
            return True
    return False

# ---------------------------------------------------------------------------
# Dashboard Header
# ---------------------------------------------------------------------------

st.title("🏠 Dashboard")
st.markdown(f"### Welcome, {user_name}")
st.caption(f"Role: {get_role_display_name(user_role)}")

# Load metrics
try:
    metrics = _load_dashboard_metrics()
except Exception as e:
    st.error(f"Could not load dashboard metrics: {e}")
    metrics = {'total_users': 0, 'active_students': 0, 'pending_approvals': 0, 'on_hold': 0}

# ---------------------------------------------------------------------------
# Role-specific dashboard content
# ---------------------------------------------------------------------------

if user_role == 'admin':
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", metrics['total_users'])
    with col2:
        st.metric("Active Students", metrics['active_students'])
    with col3:
        st.metric("Pending Approvals", metrics['pending_approvals'], 
                  delta=f"+{metrics['on_hold']} on hold" if metrics['on_hold'] else None)
    with col4:
        st.metric("On Hold", metrics['on_hold'])

elif user_role in ('hod', 'special_educator'):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Students", metrics['active_students'])
    with col2:
        st.metric("Pending Approvals", metrics['pending_approvals'])
    with col3:
        st.metric("On Hold", metrics['on_hold'])

elif user_role == 'teacher' or user_role == 'therapist':
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Today's Sessions", "0")
    with col2:
        st.metric("Assigned Students", "0")
    with col3:
        st.metric("Pending Logs", "0")
    st.info("Teacher/Therapist dashboard - Session management coming soon")

elif user_role == 'parent':
    st.info("Parent dashboard - View your child's progress coming soon")

else:
    st.info("Dashboard content for your role is being developed.")

# ---------------------------------------------------------------------------
# Approval Queue (for admin, hod, special_educator)
# ---------------------------------------------------------------------------

if can_approve_registrations(user_role):
    st.markdown("---")
    st.subheader("📋 Registration Approval Queue")
    
    # Check if viewing a specific student
    if 'approval_view_student' in st.session_state and st.session_state.approval_view_student:
        student_id = st.session_state.approval_view_student
        student = _get_student_by_id(student_id)
        
        if not student:
            st.error("Student not found.")
            if st.button("← Back to Queue"):
                st.session_state.approval_view_student = None
                st.rerun()
        else:
            # Back button
            if st.button("← Back to Queue"):
                st.session_state.approval_view_student = None
                st.rerun()
            
            st.markdown("---")
            
            # Status badge
            status = student['registration_status']
            if status == 'pending_review':
                st.info("🔵 **Status: Pending Review**")
            elif status == 'on_hold':
                st.warning("🟡 **Status: On Hold** - Awaiting additional information")
            
            # Student profile summary
            st.markdown(f"## {student['first_name']} {student['last_name']}")
            if student['preferred_name']:
                st.caption(f"Preferred name: {student['preferred_name']}")
            st.caption(f"Admission #: {student['admission_number']} | Submitted by: {student['created_by']} on {student['created_at'].strftime('%Y-%m-%d %H:%M') if student['created_at'] else 'N/A'}")
            
            # Expandable sections for each registration step
            with st.expander("📝 Step 1: Basic Information", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**First Name:** {student['first_name']}")
                    st.write(f"**Last Name:** {student['last_name']}")
                    st.write(f"**Preferred Name:** {student['preferred_name'] or '—'}")
                with col2:
                    st.write(f"**Date of Birth:** {student['date_of_birth']}")
                    st.write(f"**Gender:** {student['gender'] or '—'}")
                    st.write(f"**Enrollment Date:** {student['enrollment_date']}")
            
            with st.expander("👨‍👩‍👧 Step 2: Contact Information"):
                contact = student['contact_info']
                if contact:
                    primary = contact.get('primary_guardian', {})
                    if primary:
                        st.markdown("**Primary Guardian**")
                        st.write(f"- Name: {primary.get('name', '—')}")
                        st.write(f"- Relationship: {primary.get('relationship', '—')}")
                        st.write(f"- Phone: {primary.get('phone', '—')}")
                        st.write(f"- Email: {primary.get('email', '—')}")
                        st.write(f"- Language: {primary.get('language', '—')}")
                    address = contact.get('address', {})
                    if address:
                        st.markdown("**Address**")
                        st.write(f"{address.get('street', '')} {address.get('city', '')} {address.get('state', '')} {address.get('zip', '')}")
                    emergency = contact.get('emergency_contacts', [])
                    if emergency:
                        st.markdown("**Emergency Contacts**")
                        for i, ec in enumerate(emergency, 1):
                            st.write(f"{i}. {ec.get('name', '—')} ({ec.get('relationship', '—')}) - {ec.get('phone', '—')}")
                else:
                    st.caption("No contact information provided.")
            
            with st.expander("🎓 Step 3: Academic Information"):
                academic = student['academic_info']
                if academic:
                    st.write(f"**Grade Level:** {academic.get('grade_level', '—')}")
                    st.write(f"**Section:** {academic.get('section', '—')}")
                    st.write(f"**Previous School:** {academic.get('previous_school', '—')}")
                    st.write(f"**Transfer Reason:** {academic.get('transfer_reason', '—')}")
                    prefs = academic.get('schedule_preferences', {})
                    if prefs:
                        st.markdown("**Schedule Preferences**")
                        if prefs.get('morning_sessions'):
                            st.write("- Prefers morning sessions")
                        if prefs.get('transportation'):
                            st.write("- Requires transportation assistance")
                        if prefs.get('sibling'):
                            st.write("- Has sibling in same school")
                else:
                    st.caption("No academic information provided.")
            
            with st.expander("🏥 Step 4: Medical & Health"):
                medical = student['medical_info']
                if medical:
                    cond = medical.get('condition', {})
                    if cond.get('name'):
                        st.markdown("**Medical Condition**")
                        st.write(f"- Condition: {cond.get('name')} ({cond.get('severity', '—')})")
                        st.write(f"- Diagnosed by: {cond.get('diagnosed_by', '—')}")
                        st.write(f"- Treatment: {cond.get('treatment', '—')}")
                    
                    allergy = medical.get('allergy', {})
                    if allergy.get('allergen'):
                        st.markdown("**Allergy**")
                        st.write(f"- Allergen: {allergy.get('allergen')} ({allergy.get('severity', '—')})")
                        st.write(f"- Reaction: {allergy.get('reaction', '—')}")
                    
                    med = medical.get('medication', {})
                    if med.get('name'):
                        st.markdown("**Medication**")
                        st.write(f"- Medication: {med.get('name')}")
                        st.write(f"- Dosage: {med.get('dosage', '—')}, {med.get('frequency', '—')}")
                        st.write(f"- Prescribed for: {med.get('prescribed_for', '—')}")
                else:
                    st.caption("No medical information provided.")
            
            with st.expander("🧠 Step 5: Learning Profile"):
                profile = student['learning_profile']
                if profile:
                    st.write(f"**Primary Diagnosis:** {profile.get('diagnosis', '—')}")
                    st.write(f"**Impact Level:** {profile.get('impact_level', '—')}")
                    affected = profile.get('affected_areas', [])
                    if affected:
                        st.write(f"**Affected Areas:** {', '.join(affected)}")
                else:
                    st.caption("No learning profile provided.")
            
            st.markdown("---")
            st.subheader("📝 Review & Decision")
            
            # Notes input
            col_notes1, col_notes2 = st.columns(2)
            with col_notes1:
                internal_notes = st.text_area(
                    "Internal Notes (Staff Only)",
                    value=student['internal_notes'],
                    height=120,
                    help="These notes are only visible to staff members."
                )
            with col_notes2:
                parent_notes = st.text_area(
                    "Parent/Guardian Notes",
                    value=student['parent_notes'],
                    height=120,
                    help="These notes will be shared with the parent/guardian."
                )
            
            st.markdown("---")
            
            # Action buttons
            col_act1, col_act2, col_act3, col_act4 = st.columns(4)
            
            with col_act1:
                if st.button("✅ Approve", type="primary", use_container_width=True):
                    if _update_registration_status(student_id, 'approved', internal_notes, parent_notes, user_id):
                        st.success("Registration approved! Student is now active.")
                        st.session_state.approval_view_student = None
                        st.rerun()
                    else:
                        st.error("Failed to approve registration.")
            
            with col_act2:
                if st.button("❌ Deny", type="secondary", use_container_width=True):
                    if _update_registration_status(student_id, 'denied', internal_notes, parent_notes, user_id):
                        st.warning("Registration denied. Creator can edit and resubmit.")
                        st.session_state.approval_view_student = None
                        st.rerun()
                    else:
                        st.error("Failed to deny registration.")
            
            with col_act3:
                if st.button("⏸️ Withhold", type="secondary", use_container_width=True):
                    if _update_registration_status(student_id, 'on_hold', internal_notes, parent_notes, user_id):
                        st.info("Registration on hold. Creator will be notified to provide more information.")
                        st.session_state.approval_view_student = None
                        st.rerun()
                    else:
                        st.error("Failed to put registration on hold.")
            
            with col_act4:
                if st.button("💾 Save Notes Only", use_container_width=True):
                    if _update_registration_status(student_id, student['registration_status'], internal_notes, parent_notes, user_id):
                        st.success("Notes saved.")
                    else:
                        st.error("Failed to save notes.")
    
    else:
        # Show the approval queue list
        pending = _load_pending_registrations()
        
        if not pending:
            st.success("✅ No registrations pending approval.")
        else:
            st.write(f"**{len(pending)}** registration(s) awaiting review:")
            
            for student in pending:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        name = f"{student['first_name']} {student['last_name']}"
                        if student['preferred_name']:
                            name += f" ({student['preferred_name']})"
                        st.markdown(f"**{name}**")
                        st.caption(f"Admission #: {student['admission_number']}")
                    
                    with col2:
                        status = student['registration_status']
                        if status == 'pending_review':
                            st.markdown("🔵 Pending Review")
                        elif status == 'on_hold':
                            st.markdown("🟡 On Hold")
                    
                    with col3:
                        st.caption(f"Submitted: {student['created_at'].strftime('%Y-%m-%d') if student['created_at'] else 'N/A'}")
                        st.caption(f"By: {student['created_by']}")
                    
                    with col4:
                        if st.button("Review", key=f"review_{student['student_id']}"):
                            st.session_state.approval_view_student = student['student_id']
                            st.rerun()
                    
                    st.markdown("---")

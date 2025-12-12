"""
Student Management page – includes multi-step registration wizard.
"""

from datetime import date
from typing import Dict, Any, Optional

import streamlit as st
from sqlalchemy import asc

from src.database.connection import get_db_session
from src.database.models import Student, User


st.set_page_config(page_title="Student Management", page_icon="👥", layout="wide")

if not st.session_state.get("authenticated"):
    st.error("Please log in to access this page.")
    st.stop()

user_role = st.session_state.get("user_role")
current_user_id = st.session_state.get("user_id")

# Check permissions
if user_role not in ["admin", "special_educator", "junior_staff"]:
    st.error("You do not have permission to access this page.")
    st.stop()

st.title("👥 Student Management")

tab1, tab2, tab3 = st.tabs(["Student List", "Register New Student", "Student Profiles"])


def _registration_badge(status: str, step: int) -> str:
    """Textual badge summarising registration status & progress."""
    step = step or 0
    if status == "approved":
        return f"✅ Approved · Step {step}/6"
    if status == "pending_review":
        return f"⏳ Pending Review · Step {step}/6"
    if status == "denied":
        return f"❌ Denied (Edit & Resubmit)"
    if status == "on_hold":
        return f"🟡 On Hold (Edit & Resubmit)"
    return f"📝 Draft · Step {step}/6"


def _load_registrations(for_user_id: Optional[int] = None):
    with get_db_session() as session:
        q = session.query(Student).order_by(asc(Student.first_name), asc(Student.last_name))
        if for_user_id is not None:
            q = q.filter(Student.created_by == for_user_id)
        return q.all()


def _load_teachers(session):
    """Return simple list of teacher users for dropdowns (name, id)."""
    teachers = (
        session.query(User)
        .filter(User.role.in_(["teacher", "therapist", "special_educator"]))
        .order_by(User.name)
        .all()
    )
    return teachers


def _ensure_current_registration() -> Optional[Student]:
    """Return the Student being edited in the wizard (or None)."""
    reg_id = st.session_state.get("current_registration_id")
    if not reg_id:
        return None
    with get_db_session() as session:
        student = session.query(Student).filter(Student.student_id == reg_id).first()
        return student


def _create_or_update_student_basic(
    student: Optional[Student], data: Dict[str, Any], step_number: int
) -> Student:
    """Create or update basic student info (step 1)."""
    with get_db_session() as session:
        if student:
            db_student = (
                session.query(Student)
                .filter(Student.student_id == student.student_id)
                .first()
            )
        else:
            # Create new student – set ALL required NOT NULL fields before flush
            db_student = Student()
            if current_user_id:
                db_student.created_by = current_user_id
            db_student.status = "pending"
            setattr(db_student, "registration_status", "draft")
            setattr(db_student, "registration_step", 0)
            session.add(db_student)

        # Set required fields (must happen before flush for new records)
        db_student.first_name = data["first_name"]
        db_student.last_name = data["last_name"]
        db_student.preferred_name = data["preferred_name"] or None
        db_student.date_of_birth = data["dob"]
        db_student.gender = data["gender"]
        db_student.enrollment_date = data["enrollment_date"]

        # Flush to get student_id for new records
        session.flush()

        # Admission number auto-generation (needs student_id from flush)
        if not db_student.admission_number and db_student.student_id:
            year = date.today().year
            db_student.admission_number = f"S-{year}-{db_student.student_id:04d}"

        # Track highest completed step
        db_student.registration_step = max(db_student.registration_step or 0, step_number)

        st.session_state["current_registration_id"] = db_student.student_id
        return db_student


def _update_json_field(student: Student, field_name: str, payload: Dict[str, Any], step: int):
    """Update one of the JSON fields and registration step."""
    with get_db_session() as session:
        db_student = (
            session.query(Student)
            .filter(Student.student_id == student.student_id)
            .first()
        )
        if not db_student:
            return
        setattr(db_student, field_name, payload)
        db_student.registration_step = max(db_student.registration_step or 0, step)


with tab1:
    st.subheader("Student List & Registration Status")

    registrations = _load_registrations()
    if not registrations:
        st.info("No students or registrations found yet.")
    else:
        rows = []
        for s in registrations:
            rows.append(
                {
                    "Admission #": s.admission_number or "—",
                    "Name": f"{s.first_name} {s.last_name}",
                    "Grade": s.grade or "—",
                    "Section": s.section or "—",
                    "Reg. Status": s.registration_status or "draft",
                    "Workflow": _registration_badge(
                        s.registration_status or "draft", s.registration_step or 0
                    ),
                }
            )
        st.dataframe(rows, hide_index=True, use_container_width=True)


with tab2:
    st.subheader("Register New Student")

    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.markdown("#### Your Registrations")
        my_regs = _load_registrations(for_user_id=current_user_id)
        if not my_regs:
            st.caption("You have no registrations yet.")
        else:
            for s in my_regs:
                sel = st.button(
                    f"{s.first_name} {s.last_name} "
                    f"({s.admission_number or 'unassigned'})",
                    key=f"select_reg_{s.student_id}",
                )
                st.caption(_registration_badge(s.registration_status, s.registration_step or 0))
                # Show reviewer feedback for denied/on_hold
                if s.registration_status in ("denied", "on_hold") and s.parent_notes:
                    st.caption(f"💬 Feedback: {s.parent_notes[:50]}...")
                if sel:
                    st.session_state["current_registration_id"] = s.student_id
                    st.session_state["_pending_step"] = s.registration_step or 1
                    st.rerun()

        if st.button("➕ Start new registration"):
            st.session_state["current_registration_id"] = None
            st.session_state["_pending_step"] = 1
            st.rerun()

    with col_right:
        # Handle pending step navigation (must happen before widget renders)
        if "_pending_step" in st.session_state:
            st.session_state["registration_step_ui"] = st.session_state.pop("_pending_step")

        # Determine current step in UI
        current_step = st.session_state.get("registration_step_ui", 1)
        current_student = _ensure_current_registration()

        if current_student:
            st.markdown(
                f"**Admission #:** `{current_student.admission_number or 'pending'}`  ·  "
                f"**Status:** {_registration_badge(current_student.registration_status, current_student.registration_step)}"
            )

        step_labels = [
            "1. Basic Info",
            "2. Contact",
            "3. Academic",
            "4. Medical",
            "5. Learning Profile",
            "6. Review & Submit",
        ]
        st.radio(
            "Registration step",
            options=list(range(1, 7)),
            format_func=lambda i: step_labels[i - 1],
            index=current_step - 1,
            key="registration_step_ui",
            horizontal=True,
        )
        current_step = st.session_state["registration_step_ui"]

        # ----- STEP 1: BASIC INFORMATION -----
        if current_step == 1:
            st.markdown("### Step 1: Student Identification")

            # Prefill values if editing
            first_name = current_student.first_name if current_student else ""
            last_name = current_student.last_name if current_student else ""
            preferred_name = current_student.preferred_name if current_student else ""
            dob = current_student.date_of_birth if current_student else None
            gender = current_student.gender if current_student else "Prefer not to say"
            enrollment_date = (
                current_student.enrollment_date if current_student else date.today()
            )

            with st.form("step1_basic_form"):
                st.text_input(
                    "Admission Number (auto-generated)",
                    value=current_student.admission_number if current_student else "Will be generated after save",
                    disabled=True,
                )
                col1, col2 = st.columns(2)
                with col1:
                    first_name_val = st.text_input("First Name *", value=first_name)
                    preferred_name_val = st.text_input(
                        "Preferred Name", value=preferred_name or ""
                    )
                with col2:
                    last_name_val = st.text_input("Last Name *", value=last_name)
                    dob_val = st.date_input("Date of Birth *", value=dob or date(2015, 1, 1))

                col3, col4 = st.columns(2)
                with col3:
                    gender_val = st.selectbox(
                        "Gender *",
                        options=["Male", "Female", "Other", "Prefer not to say"],
                        index=[
                            "Male",
                            "Female",
                            "Other",
                            "Prefer not to say",
                        ].index(gender or "Prefer not to say"),
                    )
                with col4:
                    enrollment_val = st.date_input(
                        "Enrollment Date *", value=enrollment_date
                    )

                col_buttons = st.columns(2)
                with col_buttons[0]:
                    cancel = st.form_submit_button("Cancel")
                with col_buttons[1]:
                    save_next = st.form_submit_button("Save & Next ▶", type="primary")

            if cancel:
                st.session_state["current_registration_id"] = None
                st.success("Registration editing cancelled.")
            if save_next:
                if not first_name_val or not last_name_val:
                    st.error("First name and last name are required.")
                else:
                    data = {
                        "first_name": first_name_val.strip(),
                        "last_name": last_name_val.strip(),
                        "preferred_name": preferred_name_val.strip(),
                        "dob": dob_val,
                        "gender": gender_val,
                        "enrollment_date": enrollment_val,
                    }
                    student = _create_or_update_student_basic(current_student, data, step_number=1)
                    st.success("Step 1 saved.")
                    st.session_state["current_registration_id"] = student.student_id
                    st.session_state["_pending_step"] = 2
                    st.rerun()

        # ----- STEP 2: CONTACT INFORMATION -----
        elif current_step == 2:
            st.markdown("### Step 2: Contact & Family Information")

            if not current_student:
                st.warning("Please complete Step 1 first.")
            else:
                contact = current_student.contact_info or {}
                primary = contact.get("primary_guardian", {})
                address = contact.get("address", {})
                emergency = contact.get("emergency_contacts", [])

                with st.form("step2_contact_form"):
                    st.markdown("**Primary Guardian**")
                    col1, col2 = st.columns(2)
                    with col1:
                        rel = st.selectbox(
                            "Relationship *",
                            options=["Mother", "Father", "Guardian", "Other"],
                            index=[
                                "Mother",
                                "Father",
                                "Guardian",
                                "Other",
                            ].index(primary.get("relationship", "Mother")),
                        )
                        full_name = st.text_input(
                            "Full Name *", value=primary.get("full_name", "")
                        )
                        phone = st.text_input(
                            "Contact Number *", value=primary.get("phone", "")
                        )
                    with col2:
                        email = st.text_input(
                            "Email *", value=primary.get("email", "")
                        )
                        pref_lang = st.text_input(
                            "Preferred Language", value=primary.get("language", "English")
                        )
                        comm_pref = st.selectbox(
                            "Communication Preference",
                            options=["Email", "SMS", "Both"],
                            index=["Email", "SMS", "Both"].index(
                                primary.get("communication_pref", "Email")
                            ),
                        )

                    st.markdown("**Address**")
                    addr_line = st.text_input(
                        "Address Line", value=address.get("line1", "")
                    )
                    city_state_zip = st.text_input(
                        "City, State, ZIP", value=address.get("city_state_zip", "")
                    )

                    st.markdown("**Emergency Contacts (at least 2 recommended)**")
                    ec1 = emergency[0] if len(emergency) > 0 else {}
                    ec2 = emergency[1] if len(emergency) > 1 else {}

                    col_e1 = st.columns(3)
                    with col_e1[0]:
                        ec1_name = st.text_input("Contact 1 Name", value=ec1.get("name", ""))
                    with col_e1[1]:
                        ec1_phone = st.text_input("Contact 1 Phone", value=ec1.get("phone", ""))
                    with col_e1[2]:
                        ec1_rel = st.text_input(
                            "Contact 1 Relationship", value=ec1.get("relationship", "")
                        )

                    col_e2 = st.columns(3)
                    with col_e2[0]:
                        ec2_name = st.text_input("Contact 2 Name", value=ec2.get("name", ""))
                    with col_e2[1]:
                        ec2_phone = st.text_input("Contact 2 Phone", value=ec2.get("phone", ""))
                    with col_e2[2]:
                        ec2_rel = st.text_input(
                            "Contact 2 Relationship", value=ec2.get("relationship", "")
                        )

                    col_buttons = st.columns(2)
                    with col_buttons[0]:
                        back = st.form_submit_button("◀ Back to Step 1")
                    with col_buttons[1]:
                        save_next = st.form_submit_button("Save & Next ▶", type="primary")

                if back:
                    st.session_state["_pending_step"] = 1
                    st.rerun()
                if save_next:
                    if not full_name or not phone or not email:
                        st.error("Primary guardian name, phone and email are required.")
                    else:
                        emergency_list = []
                        if ec1_name or ec1_phone:
                            emergency_list.append(
                                {"name": ec1_name, "phone": ec1_phone, "relationship": ec1_rel}
                            )
                        if ec2_name or ec2_phone:
                            emergency_list.append(
                                {"name": ec2_name, "phone": ec2_phone, "relationship": ec2_rel}
                            )

                        payload = {
                            "primary_guardian": {
                                "relationship": rel,
                                "full_name": full_name,
                                "phone": phone,
                                "email": email,
                                "language": pref_lang,
                                "communication_pref": comm_pref,
                            },
                            "address": {
                                "line1": addr_line,
                                "city_state_zip": city_state_zip,
                            },
                            "emergency_contacts": emergency_list,
                        }
                        _update_json_field(current_student, "contact_info", payload, step=2)
                        st.success("Step 2 saved.")
                        st.session_state["_pending_step"] = 3
                        st.rerun()

        # ----- STEP 3: ACADEMIC DETAILS -----
        elif current_step == 3:
            st.markdown("### Step 3: Academic Information")

            if not current_student:
                st.warning("Please complete Step 1 first.")
            else:
                acad = current_student.academic_info or {}
                current_enrollment = acad.get("current_enrollment", {})
                schedule = acad.get("schedule_preferences", {})

                with get_db_session() as session:
                    teachers = _load_teachers(session)

                teacher_names = [t.name for t in teachers]

                with st.form("step3_academic_form"):
                    st.markdown("**Current Enrollment**")
                    col1, col2 = st.columns(2)
                    with col1:
                        grade_val = st.text_input(
                            "Grade Level *", value=current_enrollment.get("grade", "")
                        )
                        section_val = st.text_input(
                            "Section", value=current_enrollment.get("section", "")
                        )
                    with col2:
                        teacher_idx = (
                            teacher_names.index(current_enrollment.get("class_teacher"))
                            if current_enrollment.get("class_teacher") in teacher_names
                            else 0
                        ) if teacher_names else 0
                        class_teacher = st.selectbox(
                            "Class Teacher",
                            options=teacher_names or ["(None configured)"],
                            index=teacher_idx if teacher_names else 0,
                        )
                        prev_school = st.text_input(
                            "Previous School", value=current_enrollment.get("previous_school", "")
                        )

                    transfer_reason = st.text_area(
                        "Transfer Reason", value=current_enrollment.get("transfer_reason", "")
                    )

                    st.markdown("**Schedule & Preferences**")
                    colp1, colp2, colp3 = st.columns(3)
                    with colp1:
                        prefers_morning = st.checkbox(
                            "Prefers morning sessions",
                            value=schedule.get("prefers_morning", False),
                        )
                    with colp2:
                        transport = st.checkbox(
                            "Requires transportation assistance",
                            value=schedule.get("transport_assistance", False),
                        )
                    with colp3:
                        has_sibling = st.checkbox(
                            "Has sibling in same school",
                            value=schedule.get("has_sibling", False),
                        )

                    col_buttons = st.columns(2)
                    with col_buttons[0]:
                        back = st.form_submit_button("◀ Back to Step 2")
                    with col_buttons[1]:
                        save_next = st.form_submit_button("Save & Next ▶", type="primary")

                if back:
                    st.session_state["_pending_step"] = 2
                    st.rerun()
                if save_next:
                    if not grade_val:
                        st.error("Grade level is required.")
                    else:
                        payload = {
                            "current_enrollment": {
                                "grade": grade_val,
                                "section": section_val,
                                "class_teacher": class_teacher,
                                "previous_school": prev_school,
                                "transfer_reason": transfer_reason,
                            },
                            "schedule_preferences": {
                                "prefers_morning": prefers_morning,
                                "transport_assistance": transport,
                                "has_sibling": has_sibling,
                            },
                        }
                        _update_json_field(current_student, "academic_info", payload, step=3)
                        # Also keep core grade/section fields in sync
                        with get_db_session() as session:
                            db_student = (
                                session.query(Student)
                                .filter(Student.student_id == current_student.student_id)
                                .first()
                            )
                            if db_student:
                                db_student.grade = grade_val
                                db_student.section = section_val
                        st.success("Step 3 saved.")
                        st.session_state["_pending_step"] = 4
                        st.rerun()

        # ----- STEP 4: MEDICAL & HEALTH -----
        elif current_step == 4:
            st.markdown("### Step 4: Medical & Health")

            if not current_student:
                st.warning("Please complete Step 1 first.")
            else:
                med = current_student.medical_info or {}
                cond = med.get("conditions", [{}])[0] if med.get("conditions") else {}
                allergy = med.get("allergies", [{}])[0] if med.get("allergies") else {}
                medication = med.get("medications", [{}])[0] if med.get("medications") else {}

                with st.form("step4_medical_form"):
                    st.markdown("**Medical Conditions**")
                    has_cond = st.checkbox(
                        "Any known conditions?", value=bool(cond.get("name"))
                    )
                    cond_name = ""
                    cond_severity = "Mild"
                    cond_doctor = ""
                    cond_notes = ""
                    if has_cond:
                        col1, col2 = st.columns(2)
                        with col1:
                            cond_name = st.text_input(
                                "Condition", value=cond.get("name", "")
                            )
                            cond_severity = st.selectbox(
                                "Severity",
                                options=["Mild", "Moderate", "Severe"],
                                index=["Mild", "Moderate", "Severe"].index(
                                    cond.get("severity", "Mild")
                                ),
                                key="cond_severity",
                            )
                        with col2:
                            cond_doctor = st.text_input(
                                "Diagnosed by", value=cond.get("diagnosed_by", "")
                            )
                            cond_notes = st.text_area(
                                "Current treatment", value=cond.get("treatment", "")
                            )

                    st.markdown("---")
                    st.markdown("**Allergies**")
                    has_allergy = st.checkbox(
                        "Any allergies?", value=bool(allergy.get("allergen"))
                    )
                    allergy_name = ""
                    allergy_reaction = ""
                    allergy_sev = "Mild"
                    if has_allergy:
                        col3, col4 = st.columns(2)
                        with col3:
                            allergy_name = st.text_input(
                                "Allergen", value=allergy.get("allergen", "")
                            )
                            allergy_reaction = st.text_input(
                                "Reaction", value=allergy.get("reaction", "")
                            )
                        with col4:
                            allergy_sev = st.selectbox(
                                "Severity",
                                options=["Mild", "Moderate", "Severe"],
                                index=["Mild", "Moderate", "Severe"].index(
                                    allergy.get("severity", "Mild")
                                ),
                                key="allergy_severity",
                            )

                    st.markdown("---")
                    st.markdown("**Medications**")
                    has_med = st.checkbox(
                        "Currently on medication?", value=bool(medication.get("name"))
                    )
                    med_name = ""
                    med_dosage = ""
                    med_reason = ""
                    if has_med:
                        col5, col6 = st.columns(2)
                        with col5:
                            med_name = st.text_input(
                                "Medication", value=medication.get("name", "")
                            )
                            med_dosage = st.text_input(
                                "Dosage / Times per day",
                                value=medication.get("dosage", ""),
                            )
                        with col6:
                            med_reason = st.text_input(
                                "Prescribed for", value=medication.get("reason", "")
                            )

                    st.markdown("---")
                    col_buttons = st.columns(2)
                    with col_buttons[0]:
                        back = st.form_submit_button("◀ Back to Step 3")
                    with col_buttons[1]:
                        save_next = st.form_submit_button("Save & Next ▶", type="primary")

                if back:
                    st.session_state["_pending_step"] = 3
                    st.rerun()
                if save_next:
                    payload = {}
                    if has_cond and cond_name:
                        payload.setdefault("conditions", []).append(
                            {
                                "name": cond_name,
                                "severity": cond_severity,
                                "diagnosed_by": cond_doctor,
                                "treatment": cond_notes,
                            }
                        )
                    if has_allergy and allergy_name:
                        payload.setdefault("allergies", []).append(
                            {
                                "allergen": allergy_name,
                                "reaction": allergy_reaction,
                                "severity": allergy_sev,
                            }
                        )
                    if has_med and med_name:
                        payload.setdefault("medications", []).append(
                            {
                                "name": med_name,
                                "dosage": med_dosage,
                                "reason": med_reason,
                            }
                        )
                    _update_json_field(current_student, "medical_info", payload, step=4)
                    st.success("Step 4 saved.")
                    st.session_state["_pending_step"] = 5
                    st.rerun()

        # ----- STEP 5: LEARNING DIFFICULTY PROFILE -----
        elif current_step == 5:
            st.markdown("### Step 5: Learning Difficulty Profile")

            if not current_student:
                st.warning("Please complete Step 1 first.")
            else:
                lp = current_student.learning_profile or {}
                primary_diag = lp.get("primary_diagnosis", "")
                other_diag = lp.get("other_diagnosis", "")
                impact_level = lp.get("impact_level", "Mild")
                affected_areas = lp.get("affected_areas", [])

                diagnosis_options = [
                    "Dyslexia",
                    "Dysgraphia",
                    "Dyscalculia",
                    "ADHD",
                    "Executive Function",
                    "Auditory Processing",
                    "Visual Processing",
                    "Language Processing",
                    "Non-Verbal Learning",
                    "Dyspraxia",
                    "Other",
                ]

                with st.form("step5_learning_form"):
                    st.markdown("**Primary Diagnosis (Required)**")
                    diag = st.selectbox(
                        "Primary Diagnosis *",
                        options=diagnosis_options,
                        index=diagnosis_options.index(primary_diag)
                        if primary_diag in diagnosis_options
                        else diagnosis_options.index("Other"),
                    )
                    other_diag_val = ""
                    if diag == "Other":
                        other_diag_val = st.text_input(
                            "Other diagnosis description",
                            value=other_diag or "",
                        )

                    col1, col2 = st.columns(2)
                    with col1:
                        diag_date = st.date_input(
                            "Diagnosis Date",
                            value=lp.get("diagnosis_date", date.today()),
                        )
                    with col2:
                        agency = st.text_input(
                            "Diagnosing Agency",
                            value=lp.get("diagnosing_agency", ""),
                        )

                    ref_num = st.text_input(
                        "Report Reference #", value=lp.get("report_ref", "")
                    )

                    st.markdown("**Severity & Impact**")
                    impact = st.selectbox(
                        "Impact Level",
                        options=["Mild", "Moderate", "Severe"],
                        index=["Mild", "Moderate", "Severe"].index(impact_level),
                    )

                    areas = st.multiselect(
                        "Affected Areas",
                        options=[
                            "Reading",
                            "Writing",
                            "Math",
                            "Attention",
                            "Memory",
                            "Organization",
                            "Social Skills",
                            "Motor Skills",
                        ],
                        default=affected_areas,
                    )

                    col_buttons = st.columns(2)
                    with col_buttons[0]:
                        back = st.form_submit_button("◀ Back to Step 4")
                    with col_buttons[1]:
                        save_next = st.form_submit_button("Save & Next ▶", type="primary")

                if back:
                    st.session_state["_pending_step"] = 4
                    st.rerun()
                if save_next:
                    if not diag:
                        st.error("Primary diagnosis is required.")
                    else:
                        payload = {
                            "primary_diagnosis": diag,
                            "other_diagnosis": other_diag_val,
                            "diagnosis_date": str(diag_date),
                            "diagnosing_agency": agency,
                            "report_ref": ref_num,
                            "impact_level": impact,
                            "affected_areas": areas,
                        }
                        _update_json_field(current_student, "learning_profile", payload, step=5)
                        st.success("Step 5 saved.")
                        st.session_state["_pending_step"] = 6
                        st.rerun()

        # ----- STEP 6: REVIEW & SUBMISSION -----
        elif current_step == 6:
            st.markdown("### Step 6: Review & Submit")

            if not current_student:
                st.warning("Please complete previous steps first.")
            else:
                # Show reviewer feedback if denied or on_hold
                reg_status = current_student.registration_status or "draft"
                if reg_status == "denied":
                    st.error("❌ **This registration was denied.** Please review the feedback below, make corrections, and resubmit.")
                    if current_student.parent_notes:
                        st.warning(f"**Reviewer Feedback:** {current_student.parent_notes}")
                elif reg_status == "on_hold":
                    st.warning("🟡 **This registration is on hold.** Additional information is required. Please review the feedback, update the relevant sections, and resubmit.")
                    if current_student.parent_notes:
                        st.info(f"**Reviewer Feedback:** {current_student.parent_notes}")
                
                st.markdown("#### Summary")
                st.write(
                    f"**Student:** {current_student.first_name} {current_student.last_name} "
                    f"({current_student.admission_number or 'pending'})"
                )
                st.write(_registration_badge(current_student.registration_status, current_student.registration_step))

                with st.expander("Basic Information", expanded=True):
                    st.json(
                        {
                            "first_name": current_student.first_name,
                            "last_name": current_student.last_name,
                            "preferred_name": current_student.preferred_name,
                            "date_of_birth": str(current_student.date_of_birth),
                            "gender": current_student.gender,
                            "enrollment_date": str(current_student.enrollment_date),
                        }
                    )

                with st.expander("Contact & Family"):
                    st.json(current_student.contact_info or {})

                with st.expander("Academic Details"):
                    st.json(current_student.academic_info or {})

                with st.expander("Medical & Health"):
                    st.json(current_student.medical_info or {})

                with st.expander("Learning Profile"):
                    st.json(current_student.learning_profile or {})

                # Determine if this is a resubmission
                is_resubmit = reg_status in ("denied", "on_hold")
                submit_label = "Resubmit for Review 🔄" if is_resubmit else "Submit Registration ✅"
                
                with st.form("step6_review_form"):
                    st.markdown("**Permissions & Consents**")
                    confirm_info = st.checkbox("I confirm all information is accurate", value=False)
                    confirm_docs = st.checkbox(
                        "I have verified any uploaded documents", value=False
                    )
                    notify_parent = st.checkbox(
                        "Notify parents via email (when implemented)", value=False
                    )

                    col_buttons = st.columns(2)
                    with col_buttons[0]:
                        back = st.form_submit_button("◀ Back to Step 5")
                    with col_buttons[1]:
                        submit = st.form_submit_button(submit_label, type="primary")

                if back:
                    st.session_state["_pending_step"] = 5
                    st.rerun()
                if submit:
                    if not (confirm_info and confirm_docs):
                        st.error(
                            "Please confirm that the information and documents are accurate."
                        )
                    else:
                        with get_db_session() as session:
                            db_student = (
                                session.query(Student)
                                .filter(Student.student_id == current_student.student_id)
                                .first()
                            )
                            if db_student:
                                db_student.registration_status = "pending_review"
                                db_student.registration_step = max(
                                    db_student.registration_step or 0, 6
                                )
                                db_student.status = "pending"
                                # Clear previous review notes on resubmission
                                if is_resubmit:
                                    db_student.internal_notes = None
                                    db_student.parent_notes = None
                                    db_student.reviewed_by = None
                                    db_student.reviewed_at = None
                        if is_resubmit:
                            st.success(
                                "Registration resubmitted and marked as **Pending Review**. "
                                "The reviewer will be notified of your updates."
                            )
                        else:
                            st.success(
                                "Registration submitted and marked as **Pending Review**. "
                                "An administrator or HoD can now approve or deny this registration."
                            )
                        st.session_state["current_registration_id"] = None
                        st.session_state["_pending_step"] = 1
                        st.rerun()


with tab3:
    st.subheader("Student Profiles")
    
    # Helper to load full student profile
    def _get_full_student_profile(student_id: int):
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
                'contact_info': s.contact_info or {},
                'academic_info': s.academic_info or {},
                'medical_info': s.medical_info or {},
                'learning_profile': s.learning_profile or {},
                'created_at': s.created_at,
            }
    
    # Load approved students for cards
    def _load_approved_students():
        with get_db_session() as session:
            students = session.query(Student).filter(
                Student.registration_status == 'approved'
            ).order_by(Student.first_name, Student.last_name).all()
            
            result = []
            for s in students:
                acad = s.academic_info or {}
                enrollment = acad.get('current_enrollment', {})
                contact = s.contact_info or {}
                primary_guardian = contact.get('primary_guardian', {})
                
                result.append({
                    'student_id': s.student_id,
                    'admission_number': s.admission_number or '—',
                    'first_name': s.first_name,
                    'last_name': s.last_name,
                    'preferred_name': s.preferred_name,
                    'grade': s.grade or enrollment.get('grade', '—'),
                    'section': s.section or enrollment.get('section', '—'),
                    'guardian_name': primary_guardian.get('full_name', '—'),
                    'guardian_phone': primary_guardian.get('phone', '—'),
                    'guardian_email': primary_guardian.get('email', '—'),
                    'class_teacher': enrollment.get('class_teacher', '—'),
                    'gender': s.gender or '—',
                })
            return result
    
    # Helper to render inline profile panel
    def _render_inline_profile(student_id):
        """Render an expandable profile panel for the selected student."""
        student = _get_full_student_profile(student_id)
        if not student:
            st.error("Student not found.")
            return
        
        # Profile panel with styled container
        st.markdown("""
        <style>
        .profile-panel {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            color: #eee;
            border: 2px solid #667eea;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }
        .profile-header {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .profile-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            font-weight: bold;
            color: white;
            border: 3px solid rgba(255,255,255,0.3);
        }
        .profile-title {
            font-size: 1.5em;
            font-weight: 600;
            margin: 0;
            color: white;
        }
        .profile-subtitle {
            color: #aaa;
            font-size: 0.9em;
        }
        </style>
        """, unsafe_allow_html=True)
        
        initials = f"{student['first_name'][0]}{student['last_name'][0]}".upper()
        
        # Close button
        col_close = st.columns([6, 1])
        with col_close[1]:
            if st.button("✕ Close", key="close_profile", type="secondary"):
                st.session_state['expanded_profile_id'] = None
                st.rerun()
        
        # Profile header
        st.markdown(f"""
        <div class="profile-panel">
            <div class="profile-header">
                <div class="profile-avatar">{initials}</div>
                <div>
                    <p class="profile-title">{student['first_name']} {student['last_name']}</p>
                    <p class="profile-subtitle">📋 {student['admission_number']} · {student['preferred_name'] or 'No preferred name'}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Profile sections in expanders
        with st.expander("📝 Basic Information", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**First Name:** {student['first_name']}")
                st.write(f"**Last Name:** {student['last_name']}")
                st.write(f"**Preferred Name:** {student['preferred_name'] or '—'}")
            with col2:
                st.write(f"**Date of Birth:** {student['date_of_birth']}")
                st.write(f"**Gender:** {student['gender'] or '—'}")
                st.write(f"**Enrollment Date:** {student['enrollment_date']}")
        
        with st.expander("👨‍👩‍👧 Contact Information"):
            contact = student['contact_info']
            if contact:
                primary = contact.get('primary_guardian', {})
                if primary:
                    st.markdown("**Primary Guardian**")
                    st.write(f"- Name: {primary.get('full_name', '—')}")
                    st.write(f"- Relationship: {primary.get('relationship', '—')}")
                    st.write(f"- Phone: {primary.get('phone', '—')}")
                    st.write(f"- Email: {primary.get('email', '—')}")
                address = contact.get('address', {})
                if address:
                    st.markdown("**Address**")
                    st.write(f"{address.get('line1', '')} {address.get('city_state_zip', '')}")
                emergency = contact.get('emergency_contacts', [])
                if emergency:
                    st.markdown("**Emergency Contacts**")
                    for i, ec in enumerate(emergency, 1):
                        st.write(f"{i}. {ec.get('name', '—')} ({ec.get('relationship', '—')}) - {ec.get('phone', '—')}")
            else:
                st.caption("No contact information provided.")
        
        with st.expander("🎓 Academic Information"):
            academic = student['academic_info']
            if academic:
                enrollment = academic.get('current_enrollment', {})
                st.write(f"**Grade Level:** {enrollment.get('grade', '—')}")
                st.write(f"**Section:** {enrollment.get('section', '—')}")
                st.write(f"**Class Teacher:** {enrollment.get('class_teacher', '—')}")
                st.write(f"**Previous School:** {enrollment.get('previous_school', '—')}")
            else:
                st.caption("No academic information provided.")
        
        with st.expander("🏥 Medical & Health"):
            medical = student['medical_info']
            if medical:
                conditions = medical.get('conditions', [])
                if conditions:
                    for cond in conditions:
                        st.write(f"• {cond.get('name', '—')} ({cond.get('severity', '—')})")
                allergies = medical.get('allergies', [])
                if allergies:
                    st.markdown("**Allergies:**")
                    for allergy in allergies:
                        st.write(f"• {allergy.get('allergen', '—')} ({allergy.get('severity', '—')})")
                medications = medical.get('medications', [])
                if medications:
                    st.markdown("**Medications:**")
                    for med in medications:
                        st.write(f"• {med.get('name', '—')} - {med.get('dosage', '—')}")
            else:
                st.caption("No medical information provided.")
        
        with st.expander("🧠 Learning Profile"):
            profile = student['learning_profile']
            if profile:
                diag = profile.get('primary_diagnosis', '—')
                st.write(f"**Primary Diagnosis:** {diag}")
                st.write(f"**Impact Level:** {profile.get('impact_level', '—')}")
                affected = profile.get('affected_areas', [])
                if affected:
                    st.write(f"**Affected Areas:** {', '.join(affected)}")
            else:
                st.caption("No learning profile provided.")
        
        st.info("📚 **IEP Management** and **Session History** coming soon.")
        st.markdown("---")
    
    # Show expanded profile panel if one is selected
    if st.session_state.get('expanded_profile_id'):
        _render_inline_profile(st.session_state['expanded_profile_id'])
    
    # Always show the student cards grid below
    approved_students = _load_approved_students()
    
    if not approved_students:
        st.info("No approved students yet. Students will appear here after their registration is approved.")
    else:
        # Search/filter
        search_term = st.text_input("🔍 Search students", placeholder="Search by name, admission # or grade...", key="profile_search")
        
        # Filter students based on search
        if search_term:
            search_lower = search_term.lower()
            approved_students = [
                s for s in approved_students
                if search_lower in s['first_name'].lower()
                or search_lower in s['last_name'].lower()
                or search_lower in s['admission_number'].lower()
                or search_lower in s['grade'].lower()
            ]
        
        st.caption(f"📌 {len(approved_students)} student(s) · Click avatar to expand profile")
        
        # CSS for student cards with clickable avatar button
        st.markdown("""
        <style>
        /* Avatar button styling */
        [data-testid="stButton"] button {
            border-radius: 50% !important;
        }
        .student-card-body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 15px;
            margin: 5px 0 10px 0;
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        .student-info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            font-size: 0.85em;
        }
        .info-item {
            background: rgba(255,255,255,0.1);
            padding: 8px 10px;
            border-radius: 8px;
        }
        .info-label {
            font-size: 0.75em;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .info-value {
            font-weight: 500;
            margin-top: 2px;
        }
        .stakeholder-section {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
        .stakeholder-tag {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            margin: 3px 3px 0 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display cards in a 2-column grid
        cols = st.columns(2)
        
        for idx, student in enumerate(approved_students):
            with cols[idx % 2]:
                # Generate initials for avatar
                initials = f"{student['first_name'][0]}{student['last_name'][0]}".upper()
                
                # Build stakeholder tags
                stakeholders = []
                if student['class_teacher'] and student['class_teacher'] != '—':
                    stakeholders.append(f"👨‍🏫 {student['class_teacher']}")
                
                stakeholder_html = "".join([
                    f'<span class="stakeholder-tag">{s}</span>' for s in stakeholders
                ]) if stakeholders else '<span class="stakeholder-tag">👤 No assigned staff</span>'
                
                # Truncate long values
                guardian_name = student['guardian_name'][:20] + "..." if len(student['guardian_name']) > 20 else student['guardian_name']
                guardian_phone = student['guardian_phone'][:15] if student['guardian_phone'] else '—'
                
                student_id = student['student_id']
                
                # Use container for card with avatar button
                with st.container():
                    # Avatar button row
                    avatar_col, content_col = st.columns([1, 5])
                    
                    with avatar_col:
                        # Clickable avatar button
                        if st.button(initials, key=f"avatar_{student_id}", help="Click to view profile"):
                            st.session_state['expanded_profile_id'] = student_id
                            st.rerun()
                    
                    with content_col:
                        st.markdown(f"**{student['first_name']} {student['last_name']}**")
                        st.caption(f"📋 {student['admission_number']}")
                    
                    # Card content (without avatar)
                    card_html = f"""
                    <div class="student-card-body">
                        <div class="student-info-grid">
                            <div class="info-item">
                                <div class="info-label">Grade & Section</div>
                                <div class="info-value">🎓 {student['grade']} - {student['section']}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Gender</div>
                                <div class="info-value">{'👦' if student['gender'] == 'Male' else '👧' if student['gender'] == 'Female' else '🧑'} {student['gender']}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Guardian</div>
                                <div class="info-value">👨‍👩‍👧 {guardian_name}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Contact</div>
                                <div class="info-value">📞 {guardian_phone}</div>
                            </div>
                        </div>
                        <div class="stakeholder-section">
                            <div class="info-label" style="margin-bottom: 6px;">Assigned Staff</div>
                            {stakeholder_html}
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    st.markdown("---")

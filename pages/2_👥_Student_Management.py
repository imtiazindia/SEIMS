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
        return f"❌ Denied · Step {step}/6"
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
            # Use attribute assignment instead of constructor kwargs to avoid
            # issues if new fields are not yet present in older DB/model versions.
            db_student = Student()
            if current_user_id:
                # Only set if known; avoids FK issues when session user is not in DB
                db_student.created_by = current_user_id
            db_student.status = "pending"
            # These attributes exist in the current model, but we set them
            # defensively via setattr in case of partial upgrades.
            setattr(db_student, "registration_status", "draft")
            setattr(db_student, "registration_step", 0)

            session.add(db_student)
            session.flush()  # ensure student_id is assigned

        db_student.first_name = data["first_name"]
        db_student.last_name = data["last_name"]
        db_student.preferred_name = data["preferred_name"] or None
        db_student.date_of_birth = data["dob"]
        db_student.gender = data["gender"]
        db_student.enrollment_date = data["enrollment_date"]

        # Admission number auto-generation if not already set
        if not db_student.admission_number:
            year = date.today().year
            db_student.admission_number = f"S-{year}-{db_student.student_id:04d}"

        # Track highest completed step
        db_student.registration_step = max(db_student.registration_step or 0, step_number)

        session.flush()
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
                if sel:
                    st.session_state["current_registration_id"] = s.student_id
                    st.session_state["registration_step_ui"] = s.registration_step or 1
                    st.experimental_rerun()

        if st.button("➕ Start new registration"):
            st.session_state["current_registration_id"] = None
            st.session_state["registration_step_ui"] = 1

    with col_right:
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
                    st.session_state["registration_step_ui"] = 2
                    st.experimental_rerun()

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
                    st.session_state["registration_step_ui"] = 1
                    st.experimental_rerun()
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
                        st.session_state["registration_step_ui"] = 3
                        st.experimental_rerun()

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
                    st.session_state["registration_step_ui"] = 2
                    st.experimental_rerun()
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
                        st.session_state["registration_step_ui"] = 4
                        st.experimental_rerun()

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

                    col_buttons = st.columns(2)
                    with col_buttons[0]:
                        back = st.form_submit_button("◀ Back to Step 3")
                    with col_buttons[1]:
                        save_next = st.form_submit_button("Save & Next ▶", type="primary")

                if back:
                    st.session_state["registration_step_ui"] = 3
                    st.experimental_rerun()
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
                    st.session_state["registration_step_ui"] = 5
                    st.experimental_rerun()

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
                    st.session_state["registration_step_ui"] = 4
                    st.experimental_rerun()
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
                        st.session_state["registration_step_ui"] = 6
                        st.experimental_rerun()

        # ----- STEP 6: REVIEW & SUBMISSION -----
        elif current_step == 6:
            st.markdown("### Step 6: Review & Submit")

            if not current_student:
                st.warning("Please complete previous steps first.")
            else:
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
                        submit = st.form_submit_button("Submit Registration ✅", type="primary")

                if back:
                    st.session_state["registration_step_ui"] = 5
                    st.experimental_rerun()
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
                        st.success(
                            "Registration submitted and marked as **Pending Review**. "
                            "An administrator or HoD can now approve or deny this registration."
                        )
                        st.session_state["registration_step_ui"] = 1
                        st.session_state["current_registration_id"] = None
                        st.experimental_rerun()


with tab3:
    st.subheader("Student Profiles")
    st.info(
        "Student profile management (including IEP links and session history) "
        "will be implemented here in a later phase."
    )



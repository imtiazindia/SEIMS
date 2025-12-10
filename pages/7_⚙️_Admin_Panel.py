"""
Admin Panel page – includes User Management (create, modify, roles).
"""

import streamlit as st
from sqlalchemy import desc
import secrets
import string

from src.auth.permissions import ROLES, get_role_display_name
from src.auth.authenticator import get_password_hash
from src.database.connection import get_db_session
from src.database.models import User


st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")

if not st.session_state.get("authenticated"):
    st.error("Please log in to access this page.")
    st.stop()

user_role = st.session_state.get("user_role")
current_user_id = st.session_state.get("user_id")

# Check permissions
if user_role != "admin":
    st.error("You do not have permission to access this page.")
    st.stop()

st.title("⚙️ Admin Panel")
st.caption(
    "System administration tools for user accounts, roles and future configuration."
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["User Management", "System Configuration", "Audit Logs", "Backup & Restore"]
)


def _load_users():
    """Fetch all users ordered by creation date."""
    try:
        with get_db_session() as session:
            users = session.query(User).order_by(desc(User.created_at)).all()
        return users, None
    except Exception as e:
        return [], str(e)


with tab1:
    st.subheader("User Management")
    st.markdown(
        "Manage **user accounts**, update details, and control **roles & activation**."
    )

    user_tab_create, user_tab_edit, user_tab_roles = st.tabs(
        ["Create User", "Modify User", "Roles Management"]
    )

    # --------- Create User ---------
    with user_tab_create:
        st.markdown("#### Create New User Account")

        with st.form("create_user_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                name = st.text_input("Full Name", help="E.g. Jane Doe")
                email = (
                    st.text_input(
                        "Email Address",
                        help="Used for login. Must be unique.",
                    )
                    .strip()
                    .lower()
                )
            with col_b:
                role_key = st.selectbox(
                    "Role",
                    options=list(ROLES.keys()),
                    format_func=lambda r: get_role_display_name(r),
                )
                is_active = st.checkbox("Active", value=True)

            st.markdown("**Set Initial Password**")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                password = st.text_input(
                    "Password",
                    type="password",
                    help="Minimum 8 characters; use a strong password.",
                )
            with col_p2:
                password_confirm = st.text_input(
                    "Confirm Password",
                    type="password",
                )

            submit_create = st.form_submit_button("Create User", type="primary")

        if submit_create:
            # Basic validation
            if not name or not email or not password or not password_confirm:
                st.error("Please fill in **name, email, and both password fields**.")
            elif len(password) < 8:
                st.error("Password must be **at least 8 characters** long.")
            elif password != password_confirm:
                st.error("Passwords do **not** match.")
            else:
                try:
                    with get_db_session() as session:
                        existing = session.query(User).filter(User.email == email).first()
                        if existing:
                            st.error(
                                f"A user with email `{email}` already exists. "
                                "Use the *Modify User* tab to update them."
                            )
                        else:
                            user = User(
                                email=email,
                                password_hash=get_password_hash(password),
                                name=name,
                                role=role_key,
                                is_active=is_active,
                            )
                            session.add(user)
                            # session.commit() will be called by context manager
                            st.success(
                                f"✅ User **{name}** (`{email}`) created as "
                                f"**{get_role_display_name(role_key)}**."
                            )
                except Exception as e:
                    st.error(f"Error creating user: `{e}`")

    # --------- Modify User ---------
    with user_tab_edit:
        st.markdown("#### Modify Existing User")

        search_query = st.text_input(
            "Search by name or email",
            help="Type part of a name or email address to filter users.",
        )

        users, load_err = _load_users()
        if load_err:
            st.error(f"Could not load users: `{load_err}`")
        elif not users:
            st.info("No users found yet. Create a user in the **Create User** tab.")
        else:
            if search_query:
                q = search_query.lower()
                users = [
                    u
                    for u in users
                    if q in (u.name or "").lower() or q in (u.email or "").lower()
                ]

            if not users:
                st.info("No users match your search.")
            else:
                # Map for selection
                user_options = {
                    f"{u.name} ({u.email}) [{get_role_display_name(u.role)}]": u
                    for u in users
                }

                selected_label = st.selectbox(
                    "Select user to edit",
                    options=list(user_options.keys()),
                )
                selected_user = user_options[selected_label]

                # Quick random password reset
                col_reset_btn, col_reset_help = st.columns([1, 3])
                with col_reset_btn:
                    gen_reset = st.button(
                        "Generate random password",
                        key=f"gen_pw_{selected_user.user_id}",
                        help="Sets a new strong password and shows it once.",
                    )
                with col_reset_help:
                    st.caption(
                        "Use this when a user is locked out or forgot their password. "
                        "Share the new password with them securely."
                    )

                if gen_reset:
                    alphabet = string.ascii_letters + string.digits
                    new_pw = "".join(secrets.choice(alphabet) for _ in range(12))
                    try:
                        with get_db_session() as session:
                            db_user = (
                                session.query(User)
                                .filter(User.user_id == selected_user.user_id)
                                .first()
                            )
                            if not db_user:
                                st.error("User no longer exists in the database.")
                            else:
                                db_user.password_hash = get_password_hash(new_pw)
                                st.success(
                                    f"Generated a new password for **{db_user.name}**."
                                )
                                st.info(
                                    "Share this password with the user and ask them to change it after login:"
                                )
                                st.code(new_pw, language=None)
                    except Exception as e:
                        st.error(f"Error generating new password: `{e}`")

                with st.form("edit_user_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input("Full Name", value=selected_user.name)
                        edit_email = (
                            st.text_input(
                                "Email Address",
                                value=selected_user.email,
                                help="Must remain unique.",
                            )
                            .strip()
                            .lower()
                        )
                    with col2:
                        edit_role = st.selectbox(
                            "Role",
                            options=list(ROLES.keys()),
                            index=list(ROLES.keys()).index(selected_user.role)
                            if selected_user.role in ROLES
                            else 0,
                            format_func=lambda r: get_role_display_name(r),
                        )
                        edit_active = st.checkbox(
                            "Active",
                            value=bool(selected_user.is_active),
                            help="Uncheck to disable login for this user.",
                        )

                    st.markdown("**Reset Password (optional)**")
                    colnp1, colnp2 = st.columns(2)
                    with colnp1:
                        new_password = st.text_input(
                            "New Password",
                            type="password",
                            help="Leave blank to keep current password.",
                        )
                    with colnp2:
                        new_password_confirm = st.text_input(
                            "Confirm New Password",
                            type="password",
                        )

                    submitted_edit = st.form_submit_button("Save Changes", type="primary")

            if submitted_edit:
                # Self-protection: avoid locking out current admin
                if selected_user.user_id == current_user_id and not edit_active:
                    st.error(
                        "You cannot **deactivate your own account** while logged in."
                    )
                elif (
                    selected_user.user_id == current_user_id
                    and selected_user.role == "admin"
                    and edit_role != "admin"
                ):
                    st.error(
                        "You cannot **remove your own admin role** from here. "
                        "Use another admin account if this is intentional."
                    )
                elif new_password and len(new_password) < 8:
                    st.error("New password must be **at least 8 characters** long.")
                elif new_password and new_password != new_password_confirm:
                    st.error("New passwords do **not** match.")
                else:
                    try:
                        with get_db_session() as session:
                            db_user = (
                                session.query(User)
                                .filter(User.user_id == selected_user.user_id)
                                .first()
                            )
                            if not db_user:
                                st.error("User no longer exists in the database.")
                            else:
                                # Check for email uniqueness
                                email_conflict = (
                                    session.query(User)
                                    .filter(
                                        User.email == edit_email,
                                        User.user_id != db_user.user_id,
                                    )
                                    .first()
                                )
                                if email_conflict:
                                    st.error(
                                        f"Another user already uses email `{edit_email}`. "
                                        "Choose a different email."
                                    )
                                else:
                                    db_user.name = edit_name
                                    db_user.email = edit_email
                                    db_user.role = edit_role
                                    db_user.is_active = edit_active

                                    if new_password:
                                        db_user.password_hash = get_password_hash(
                                            new_password
                                        )

                                    st.success("✅ User details updated successfully.")
                    except Exception as e:
                        st.error(f"Error updating user: `{e}`")

            # Summary table
            with st.expander("View all users", expanded=False):
                data = [
                    {
                        "ID": u.user_id,
                        "Name": u.name,
                        "Email": u.email,
                        "Role": get_role_display_name(u.role),
                        "Active": "Yes" if u.is_active else "No",
                        "Created": u.created_at,
                        "Last Login": u.last_login,
                    }
                    for u in users
                ]
                st.dataframe(data, hide_index=True, use_container_width=True)

    # --------- Roles Management (overview & quick actions) ---------
    with user_tab_roles:
        st.markdown("#### Roles Management")
        st.write(
            "Review available roles and quickly filter users by role to adjust assignments."
        )

        # Show any global role update message once, outside the row layout
        if "role_update_message" in st.session_state:
            st.success(st.session_state["role_update_message"])
            del st.session_state["role_update_message"]

        # Show defined roles
        st.markdown("**Available Roles**")
        for key, label in ROLES.items():
            st.markdown(f"- `{key}` – {label}")

        st.markdown("---")

        users, load_err = _load_users()
        if load_err:
            st.error(f"Could not load users: `{load_err}`")
        elif not users:
            st.info("No users found yet.")
        else:
            role_filter = st.selectbox(
                "Filter users by role",
                options=["(All)"] + list(ROLES.keys()),
                format_func=lambda r: "(All roles)"
                if r == "(All)"
                else get_role_display_name(r),
            )

            filtered = (
                [u for u in users if u.role == role_filter]
                if role_filter != "(All)"
                else users
            )

            st.markdown("**Users Matching Filter**")
            if not filtered:
                st.info("No users match this role filter.")
            else:
                for u in filtered:
                    cols = st.columns([3, 3, 3, 1.5])
                    with cols[0]:
                        st.write(f"**{u.name}**")
                        st.caption(f"`{u.email}`")
                    with cols[1]:
                        st.write(f"Role: {get_role_display_name(u.role)}")
                    with cols[2]:
                        st.write(f"Active: {'✅' if u.is_active else '⛔'}")
                    with cols[3]:
                        # Quick role change
                        new_role = st.selectbox(
                            "Change role",
                            options=list(ROLES.keys()),
                            index=list(ROLES.keys()).index(u.role)
                            if u.role in ROLES
                            else 0,
                            key=f"role_change_{u.user_id}",
                            label_visibility="collapsed",
                            format_func=lambda r: get_role_display_name(r),
                        )
                        if new_role != u.role:
                            # Apply change
                            try:
                                with get_db_session() as session:
                                    db_user = (
                                        session.query(User)
                                        .filter(User.user_id == u.user_id)
                                        .first()
                                    )
                                    if db_user:
                                        # Protect current admin from accidental demotion
                                        if (
                                            db_user.user_id == current_user_id
                                            and db_user.role == "admin"
                                            and new_role != "admin"
                                        ):
                                            st.warning(
                                                "You cannot change your own role away from **admin** here."
                                            )
                                        else:
                                            db_user.role = new_role
                                            # Store message and rerun so it renders once at top
                                            st.session_state[
                                                "role_update_message"
                                            ] = (
                                                f"Updated role for **{db_user.name}** "
                                                f"to **{get_role_display_name(new_role)}**."
                                            )
                                            st.rerun()
                            except Exception as e:
                                st.error(f"Error updating role: `{e}`")


with tab2:
    st.subheader("System Configuration")
    st.write("System parameters and settings will be configured here.")

with tab3:
    st.subheader("Audit Logs")
    st.write("System activity and audit logs will be displayed here.")

with tab4:
    st.subheader("Backup & Restore")
    st.write("Database backup and restoration will be managed here.")



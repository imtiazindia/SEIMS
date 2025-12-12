"""
Permission definitions and checks
"""

# Role definitions
ROLES = {
    'admin': 'System Administrator',
    'hod': 'Head of Department',
    'special_educator': 'Special Educator (Lead)',
    'junior_staff': 'Junior Staff (Data Entry)',
    'teacher': 'Teacher/Therapist',
    'therapist': 'Therapist',
    'parent': 'Parent/Guardian',
    'classroom_teacher': 'Classroom Teacher',
    'paraprofessional': 'Paraprofessional/Aide',
    'psychologist': 'School Psychologist'
}

# Roles that can approve student registrations
APPROVAL_ROLES = {'admin', 'hod', 'special_educator'}

# Permission matrix
PERMISSIONS = {
    'admin': {
        'user_management': True,
        'student_management': True,
        'iep_management': True,
        'session_logging': True,
        'assessment_reporting': True,
        'registration_approval': True,
        'system_config': True,
        'audit_logs': True
    },
    'hod': {
        'user_management': False,
        'student_management': True,
        'iep_management': True,
        'session_logging': True,
        'assessment_reporting': True,
        'registration_approval': True,
        'system_config': False,
        'audit_logs': True
    },
    'special_educator': {
        'user_management': False,
        'student_management': True,
        'iep_management': True,
        'session_logging': True,
        'assessment_reporting': True,
        'registration_approval': True,
        'system_config': False,
        'audit_logs': False
    },
    'junior_staff': {
        'user_management': False,
        'student_management': True,  # Registration only
        'iep_management': False,
        'session_logging': False,
        'assessment_reporting': False,
        'registration_approval': False,
        'system_config': False,
        'audit_logs': False
    },
    'teacher': {
        'user_management': False,
        'student_management': False,
        'iep_management': False,  # View only
        'session_logging': True,
        'assessment_reporting': False,  # View only
        'registration_approval': False,
        'system_config': False,
        'audit_logs': False
    },
    'parent': {
        'user_management': False,
        'student_management': False,
        'iep_management': False,  # View only
        'session_logging': False,
        'assessment_reporting': False,  # View only
        'registration_approval': False,
        'system_config': False,
        'audit_logs': False
    }
}

def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission"""
    return PERMISSIONS.get(role, {}).get(permission, False)

def can_approve_registrations(role: str) -> bool:
    """Check if a role can approve student registrations"""
    return role in APPROVAL_ROLES

def get_role_display_name(role: str) -> str:
    """Get display name for a role"""
    return ROLES.get(role, role)


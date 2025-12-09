"""
Permission definitions and checks
"""

# Role definitions
ROLES = {
    'admin': 'System Administrator',
    'special_educator': 'Special Educator (Lead)',
    'junior_staff': 'Junior Staff (Data Entry)',
    'teacher': 'Teacher/Therapist',
    'therapist': 'Therapist',
    'parent': 'Parent/Guardian',
    'classroom_teacher': 'Classroom Teacher',
    'paraprofessional': 'Paraprofessional/Aide',
    'psychologist': 'School Psychologist'
}

# Permission matrix
PERMISSIONS = {
    'admin': {
        'user_management': True,
        'student_management': True,
        'iep_management': True,
        'session_logging': True,
        'assessment_reporting': True,
        'system_config': True,
        'audit_logs': True
    },
    'special_educator': {
        'user_management': False,
        'student_management': True,
        'iep_management': True,
        'session_logging': True,
        'assessment_reporting': True,
        'system_config': False,
        'audit_logs': False
    },
    'junior_staff': {
        'user_management': False,
        'student_management': True,  # Registration only
        'iep_management': False,
        'session_logging': False,
        'assessment_reporting': False,
        'system_config': False,
        'audit_logs': False
    },
    'teacher': {
        'user_management': False,
        'student_management': False,
        'iep_management': False,  # View only
        'session_logging': True,
        'assessment_reporting': False,  # View only
        'system_config': False,
        'audit_logs': False
    },
    'parent': {
        'user_management': False,
        'student_management': False,
        'iep_management': False,  # View only
        'session_logging': False,
        'assessment_reporting': False,  # View only
        'system_config': False,
        'audit_logs': False
    }
}

def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission"""
    return PERMISSIONS.get(role, {}).get(permission, False)

def get_role_display_name(role: str) -> str:
    """Get display name for a role"""
    return ROLES.get(role, role)


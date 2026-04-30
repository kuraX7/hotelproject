"""
Injects dashboard_role, dashboard_role_info, and permission helpers
into every template context automatically.
"""
from dashboard.roles import ROLES, get_role, get_role_info, is_readonly, PERMISSIONS


def dashboard_role_context(request):
    role = get_role(request)
    role_info = ROLES.get(role) if role else None

    def can(url_name):
        if not role:
            return False
        allowed = PERMISSIONS.get(url_name)
        if allowed is None:
            return role == 'admin'
        return role in allowed

    return {
        'dashboard_role':       role,
        'dashboard_role_info':  role_info,
        'dashboard_roles':      ROLES,
        'dashboard_is_admin':   role == 'admin',
        'dashboard_is_manager': role == 'gestionnaire',
        'dashboard_is_director':role == 'directeur',
        'dashboard_readonly':   is_readonly(request),
        'dashboard_can':        can,
    }

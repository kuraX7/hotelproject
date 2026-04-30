"""
Système de rôles — Hôtel Al Andalus Dashboard
Trois rôles : admin, gestionnaire, directeur
Stocké en session : request.session['dashboard_role']
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

# ── ROLE DEFINITIONS ──────────────────────────────────────────────────────────

ROLES = {
    'admin': {
        'label':    'Administrateur',
        'password': 'admin123',
        'icon':     'fas fa-shield-alt',
        'color':    '#C9A96E',
        'desc':     'Accès complet à toutes les fonctionnalités',
    },
    'gestionnaire': {
        'label':    'Gestionnaire',
        'password': 'gestionnaire123',
        'icon':     'fas fa-concierge-bell',
        'color':    '#3B82F6',
        'desc':     'Gestion des réservations et opérations',
    },
    'directeur': {
        'label':    'Directeur',
        'password': 'directeur123',
        'icon':     'fas fa-chart-bar',
        'color':    '#8B5CF6',
        'desc':     'Consultation et statistiques (lecture seule)',
    },
}

# ── PERMISSIONS TABLE ─────────────────────────────────────────────────────────
# Maps URL name patterns → allowed roles (None = all authenticated)

PERMISSIONS = {
    # Dashboard home & stats
    'dashboard_home':               ['admin', 'gestionnaire', 'directeur'],
    'dashboard_reception':          ['admin', 'gestionnaire'],

    # Rooms — admin only for mutations
    'dashboard_rooms':              ['admin', 'gestionnaire', 'directeur'],
    'dashboard_room_add':           ['admin'],
    'dashboard_room_edit':          ['admin'],
    'dashboard_room_delete':        ['admin'],
    'dashboard_room_toggle':        ['admin'],
    'dashboard_room_status':        ['admin', 'gestionnaire'],
    'dashboard_room_image_add':     ['admin'],
    'dashboard_room_image_delete':  ['admin'],
    'dashboard_room_quick_status':  ['admin', 'gestionnaire'],

    # Bookings
    'dashboard_bookings':           ['admin', 'gestionnaire', 'directeur'],
    'dashboard_booking_status':     ['admin', 'gestionnaire'],
    'dashboard_booking_delete':     ['admin'],
    'dashboard_booking_notes':      ['admin', 'gestionnaire'],

    # Payments — admin only
    'dashboard_payments':           ['admin'],

    # Promotions — admin only
    'dashboard_promotions':         ['admin'],
    'dashboard_promotion_add':      ['admin'],
    'dashboard_promotion_edit':     ['admin'],
    'dashboard_promotion_delete':   ['admin'],
    'dashboard_promotion_toggle':   ['admin'],

    # CMS — admin only
    'dashboard_hero':               ['admin'],
    'dashboard_hotel_info':         ['admin'],
    'dashboard_services':           ['admin'],
    'dashboard_service_add':        ['admin'],
    'dashboard_service_edit':       ['admin'],
    'dashboard_service_delete':     ['admin'],
    'dashboard_service_toggle':     ['admin'],
    'dashboard_testimonials':       ['admin'],
    'dashboard_testimonial_add':    ['admin'],
    'dashboard_testimonial_edit':   ['admin'],
    'dashboard_testimonial_delete': ['admin'],
    'dashboard_media':              ['admin'],
    'dashboard_rules':              ['admin'],
    'dashboard_menu_card':          ['admin'],
    'dashboard_menu_card_add':      ['admin'],
    'dashboard_menu_card_edit':     ['admin'],
    'dashboard_menu_card_delete':   ['admin'],
    'dashboard_menu_card_toggle':   ['admin'],
    'dashboard_faq':                ['admin'],
    'dashboard_faq_add':            ['admin'],
    'dashboard_faq_edit':           ['admin'],
    'dashboard_faq_delete':         ['admin'],
    'dashboard_faq_toggle':         ['admin'],
    'dashboard_faq_toggle_featured':['admin'],
    'dashboard_activities':         ['admin'],
    'dashboard_activity_add':       ['admin'],
    'dashboard_activity_edit':      ['admin'],
    'dashboard_activity_delete':    ['admin'],
    'dashboard_activity_toggle':    ['admin'],

    # Emails — admin only
    'dashboard_email_settings':     ['admin'],
    'dashboard_email_test':         ['admin'],
    'dashboard_email_preview':      ['admin'],

    # Contact messages
    'dashboard_contact_messages':   ['admin', 'gestionnaire'],
    'dashboard_contact_status':     ['admin', 'gestionnaire'],
    'dashboard_contact_delete':     ['admin'],
}


# ── HELPERS ───────────────────────────────────────────────────────────────────

def get_role(request):
    """Return current role string or None."""
    return request.session.get('dashboard_role')


def get_role_info(request):
    """Return full role dict or None."""
    role = get_role(request)
    return ROLES.get(role) if role else None


def is_authenticated(request):
    return bool(get_role(request))


def can_access(request, url_name):
    """Check if current role can access a given URL name."""
    role = get_role(request)
    if not role:
        return False
    allowed = PERMISSIONS.get(url_name)
    if allowed is None:
        return role == 'admin'   # Unknown URLs → admin only by default
    return role in allowed


def is_readonly(request):
    """Directeur = read-only."""
    return get_role(request) == 'directeur'


# ── DECORATORS ────────────────────────────────────────────────────────────────

def dashboard_login_required(view_func):
    """Replaces @login_required — checks session role."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not is_authenticated(request):
            return redirect('dashboard_login')
        return view_func(request, *args, **kwargs)
    return _wrapped


def role_required(*allowed_roles):
    """Restrict view to specific roles. Usage: @role_required('admin')"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not is_authenticated(request):
                return redirect('dashboard_login')
            role = get_role(request)
            if role not in allowed_roles:
                messages.error(request,
                    f"Accès refusé. Cette fonctionnalité est réservée aux : "
                    f"{', '.join(ROLES[r]['label'] for r in allowed_roles if r in ROLES)}.")
                return redirect('dashboard_home')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def readonly_forbidden(view_func):
    """Block directeur (read-only) from mutations."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not is_authenticated(request):
            return redirect('dashboard_login')
        if is_readonly(request):
            messages.error(request, "Accès refusé. Le Directeur a un accès en lecture seule.")
            return redirect('dashboard_home')
        return view_func(request, *args, **kwargs)
    return _wrapped

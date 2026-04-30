"""
Availability engine — Al Andalus Hotel
========================================
Checks real inventory availability based on room_count.

Each Room record represents a TYPE of room (e.g. "Chambre Familiale").
room_count = how many physical rooms of this type exist (e.g. 15).

A new reservation is POSSIBLE only if:
  confirmed/pending bookings for that room on those dates < room_count

Examples:
  room_count=15, bookings_on_dates=14 → 1 disponible ✅
  room_count=15, bookings_on_dates=15 → COMPLET ❌
  room_count=15, bookings_on_dates=0  → 15 disponibles ✅
"""

from django.utils import timezone
from bookings.models import Booking


def count_bookings_on_dates(room, check_in, check_out, exclude_booking_id=None):
    """
    Count how many CONFIRMED or PENDING bookings overlap with [check_in, check_out]
    for this room type.
    """
    qs = Booking.objects.filter(
        room=room,
        status__in=['pending', 'confirmed'],
        check_in__lt=check_out,
        check_out__gt=check_in,
    )
    if exclude_booking_id:
        qs = qs.exclude(pk=exclude_booking_id)
    return qs.count()


def get_availability(room, check_in, check_out, exclude_booking_id=None):
    """
    Returns a dict with full availability info for a room type on given dates.

    Returns:
        {
            'available': True/False,
            'rooms_total': 15,
            'rooms_booked': 12,
            'rooms_free': 3,
            'message': str,
            'urgency': None / 'low' / 'medium' / 'high'  (for UI display)
        }
    """
    if not check_in or not check_out:
        return {'available': True, 'rooms_total': room.room_count,
                'rooms_booked': 0, 'rooms_free': room.room_count,
                'message': '', 'urgency': None}

    booked = count_bookings_on_dates(room, check_in, check_out, exclude_booking_id)
    total  = room.room_count
    free   = total - booked

    if free <= 0:
        return {
            'available': False,
            'rooms_total': total,
            'rooms_booked': booked,
            'rooms_free': 0,
            'message': f"Complet pour ces dates — toutes les {total} chambres sont réservées.",
            'urgency': 'full',
        }

    # Determine urgency level
    ratio = booked / total
    if ratio >= 0.8 and free <= 2:
        urgency = 'high'
        msg = f"Plus que {free} chambre{'s' if free > 1 else ''} disponible{'s' if free > 1 else ''} !"
    elif ratio >= 0.6 or free <= 5:
        urgency = 'medium'
        msg = f"Il reste {free} chambres disponibles"
    else:
        urgency = 'low'
        msg = f"{free} chambres disponibles"

    return {
        'available': True,
        'rooms_total': total,
        'rooms_booked': booked,
        'rooms_free': free,
        'message': msg,
        'urgency': urgency,
    }


def is_available(room, check_in, check_out, exclude_booking_id=None):
    """Simple True/False check."""
    return get_availability(room, check_in, check_out, exclude_booking_id)['available']


def get_availability_for_all_rooms(check_in=None, check_out=None):
    """
    Returns availability info for ALL room types.
    Used on the room list page.
    """
    from rooms.models import Room
    result = {}
    for room in Room.objects.all():
        result[room.id] = get_availability(room, check_in, check_out)
    return result


def get_next_available_date(room, from_date=None):
    """
    Find the next date where at least 1 room is free.
    Useful to suggest alternatives when a room is full.
    """
    import datetime
    if not from_date:
        from_date = timezone.now().date()

    # Check up to 90 days ahead
    for i in range(90):
        d = from_date + datetime.timedelta(days=i)
        d_end = d + datetime.timedelta(days=1)
        booked = count_bookings_on_dates(room, d, d_end)
        if booked < room.room_count:
            return d
    return None

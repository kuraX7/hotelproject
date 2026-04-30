from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Booking
from .forms import BookingForm
from rooms.models import Room
from rooms.availability import get_availability, is_available
from .email_service import (
    send_booking_confirmation_to_client,
    send_booking_notification_to_admin,
)
import datetime


def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    # Check if room status is maintenance
    if room.status == 'maintenance':
        messages.error(request, f"La chambre «{room.name}» est actuellement en maintenance. Veuillez choisir une autre chambre.")
        return redirect('room_list')

    # Pre-fill dates from URL params
    check_in_str  = request.GET.get('check_in', '')
    check_out_str = request.GET.get('check_out', '')
    avail_info = None

    if check_in_str and check_out_str:
        try:
            ci = datetime.date.fromisoformat(check_in_str)
            co = datetime.date.fromisoformat(check_out_str)
            avail_info = get_availability(room, ci, co)
            if not avail_info['available']:
                messages.error(request, avail_info['message'])
                return redirect('room_detail', slug=room.slug)
        except ValueError:
            pass

    if request.method == 'POST':
        form = BookingForm(request.POST, room=room)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room

            # ── AVAILABILITY CHECK (core logic) ──────────────────
            avail = get_availability(
                room,
                booking.check_in,
                booking.check_out,
            )

            if not avail['available']:
                messages.error(
                    request,
                    f"❌ {avail['message']} "
                    f"Toutes les {avail['rooms_total']} chambres de ce type sont réservées pour ces dates. "
                    f"Veuillez choisir d'autres dates ou un autre type de chambre."
                )
                return render(request, 'bookings/book_room.html', {
                    'form': form,
                    'room': room,
                    'avail': avail,
                })
            # ─────────────────────────────────────────────────────

            try:
                booking.clean()
                booking.save()

                # Send emails
                client_ok = send_booking_confirmation_to_client(booking)
                admin_ok  = send_booking_notification_to_admin(booking)

                if not client_ok:
                    messages.warning(
                        request,
                        "Réservation confirmée, mais l'email n'a pas pu être envoyé. "
                        "Contactez-nous pour confirmation."
                    )
                # Redirect to payment — confirmation only after payment
                return redirect('payment_initiate', booking_id=booking.id)

            except Exception as e:
                messages.error(request, str(e))
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, err)
    else:
        initial = {}
        if check_in_str:  initial['check_in']  = check_in_str
        if check_out_str: initial['check_out'] = check_out_str
        form = BookingForm(initial=initial, room=room)

    # Get availability info for pre-selected dates (for display)
    if not avail_info and check_in_str and check_out_str:
        try:
            ci = datetime.date.fromisoformat(check_in_str)
            co = datetime.date.fromisoformat(check_out_str)
            avail_info = get_availability(room, ci, co)
        except ValueError:
            pass

    return render(request, 'bookings/book_room.html', {
        'form': form,
        'room': room,
        'avail': avail_info,
    })


def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'bookings/confirmation.html', {'booking': booking})


def check_availability(request, room_id):
    """
    JSON API — checks real inventory availability.
    Called by the calendar JS widget.
    """
    room = get_object_or_404(Room, id=room_id)
    check_in  = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if not check_in or not check_out:
        return JsonResponse({'available': False, 'message': 'Dates manquantes'})

    try:
        ci = datetime.date.fromisoformat(check_in)
        co = datetime.date.fromisoformat(check_out)
    except ValueError:
        return JsonResponse({'available': False, 'message': 'Format de date invalide'})

    if ci >= co:
        return JsonResponse({'available': False, 'message': "Le départ doit être après l'arrivée"})
    if ci < timezone.now().date():
        return JsonResponse({'available': False, 'message': "La date d'arrivée ne peut pas être dans le passé"})

    # ── REAL INVENTORY CHECK ──────────────────────────────
    avail = get_availability(room, ci, co)
    nights = (co - ci).days
    total  = float(room.price) * nights

    if not avail['available']:
        return JsonResponse({
            'available': False,
            'message': avail['message'],
            'rooms_total':  avail['rooms_total'],
            'rooms_booked': avail['rooms_booked'],
            'rooms_free':   0,
        })

    return JsonResponse({
        'available':    True,
        'message':      f"✅ Disponible ! {nights} nuit(s) × {room.price} MAD = {total:.0f} MAD",
        'nights':       nights,
        'total':        total,
        'rooms_free':   avail['rooms_free'],
        'rooms_total':  avail['rooms_total'],
        'urgency':      avail['urgency'],
        'avail_message': avail['message'],
    })


def room_calendar_data(request, room_id):
    """
    Returns ALL booked dates for this room type
    (considers inventory — only marks a date as 'full' when ALL rooms are booked)
    """
    room = get_object_or_404(Room, id=room_id)
    today    = timezone.now().date()
    end_date = today + datetime.timedelta(days=365)

    # Build a set of FULLY BOOKED dates (booked_count >= room_count)
    from bookings.models import Booking
    bookings = Booking.objects.filter(
        room=room,
        status__in=['pending', 'confirmed'],
        check_out__gte=today,
        check_in__lte=end_date,
    ).values('check_in', 'check_out')

    # Count how many bookings cover each date
    date_counts = {}
    for b in bookings:
        cur = b['check_in']
        while cur < b['check_out']:
            date_counts[cur] = date_counts.get(cur, 0) + 1
            cur += datetime.timedelta(days=1)

    # Only mark as "booked" (red) if ALL rooms are taken
    fully_booked = [
        d.isoformat()
        for d, count in date_counts.items()
        if count >= room.room_count
    ]

    # Partially booked dates (for UI hint — optional)
    partially_booked = [
        d.isoformat()
        for d, count in date_counts.items()
        if 0 < count < room.room_count
    ]

    return JsonResponse({
        'room_id':          room_id,
        'room_name':        room.name,
        'price':            float(room.price),
        'room_count':       room.room_count,
        'booked_dates':     fully_booked,
        'partial_dates':    partially_booked,
        'today':            today.isoformat(),
    })


def booking_pdf(request, booking_id):
    """
    Generates and returns the booking confirmation PDF.
    """
    from django.http import HttpResponse
    from bookings.pdf_generator import generate_booking_pdf
    from django.conf import settings

    booking = get_object_or_404(Booking, id=booking_id)
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')

    buffer = generate_booking_pdf(booking, site_url=site_url)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="AlAndalus_Reservation_AL{booking.id:05d}.pdf"'
    )
    return response

# ═══════════════════════════════════════════════════════════════════
# TRACKING — Suivi de réservation par le client
# ═══════════════════════════════════════════════════════════════════

def _find_booking_by_code_email(code, email):
    """
    Cherche une réservation avec un code (ex: AL00042, AL42, ou juste 42)
    ET l'email correspondant. Retourne None si introuvable.
    """
    if not code or not email:
        return None
    # Extrait l'ID numérique du code (supporte AL00042, AL42, 42, al-00042...)
    import re
    digits = re.sub(r'[^\d]', '', code)
    if not digits:
        return None
    try:
        booking_id = int(digits)
    except ValueError:
        return None
    try:
        return Booking.objects.get(id=booking_id, email__iexact=email.strip())
    except Booking.DoesNotExist:
        return None


def tracking_search(request):
    """Page de recherche : formulaire code + email."""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        email = request.POST.get('email', '').strip()
        booking = _find_booking_by_code_email(code, email)
        if booking:
            # Stocke en session pour permettre modif/annulation sans redemander
            request.session['tracked_booking_id'] = booking.id
            return redirect('tracking_detail', booking_id=booking.id)
        else:
            messages.error(
                request,
                "Aucune réservation trouvée. Veuillez vérifier votre code et email, puis réessayer."
            )
    return render(request, 'bookings/tracking_page.html')


def _check_tracking_access(request, booking_id):
    """Vérifie que la session autorise l'accès à cette réservation."""
    tracked_id = request.session.get('tracked_booking_id')
    return tracked_id == booking_id


def tracking_detail(request, booking_id):
    """Détails de la réservation + actions."""
    if not _check_tracking_access(request, booking_id):
        messages.warning(request, "Veuillez rechercher votre réservation d'abord.")
        return redirect('tracking_search')
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'bookings/tracking_detail.html', {
        'booking': booking,
    })


def tracking_edit(request, booking_id):
    """Modifier les dates de la réservation."""
    if not _check_tracking_access(request, booking_id):
        messages.warning(request, "Veuillez rechercher votre réservation d'abord.")
        return redirect('tracking_search')
    booking = get_object_or_404(Booking, id=booking_id)

    if not booking.can_be_modified:
        messages.error(request, "Cette réservation ne peut plus être modifiée.")
        return redirect('tracking_detail', booking_id=booking.id)

    if request.method == 'POST':
        new_checkin_str = request.POST.get('check_in', '').strip()
        new_checkout_str = request.POST.get('check_out', '').strip()
        try:
            new_ci = datetime.date.fromisoformat(new_checkin_str)
            new_co = datetime.date.fromisoformat(new_checkout_str)
        except ValueError:
            messages.error(request, "Dates invalides.")
            return redirect('tracking_edit', booking_id=booking.id)

        if new_ci >= new_co:
            messages.error(request, "La date de départ doit être après la date d'arrivée.")
            return redirect('tracking_edit', booking_id=booking.id)

        if new_ci < timezone.now().date():
            messages.error(request, "La date d'arrivée ne peut pas être dans le passé.")
            return redirect('tracking_edit', booking_id=booking.id)

        # Vérifier disponibilité en excluant cette réservation
        avail = get_availability(
            booking.room, new_ci, new_co,
            exclude_booking_id=booking.id
        )
        if not avail['available']:
            messages.error(
                request,
                f"Désolé, ces dates ne sont pas disponibles : {avail['message']}"
            )
            return redirect('tracking_edit', booking_id=booking.id)

        # Tout est OK : on sauvegarde
        booking.check_in = new_ci
        booking.check_out = new_co
        booking.save()  # total_price est recalculé automatiquement
        messages.success(
            request,
            f"Vos dates ont été mises à jour. Nouveau total : {booking.total_price:.0f} MAD."
        )
        return redirect('tracking_detail', booking_id=booking.id)

    return render(request, 'bookings/tracking_edit.html', {
        'booking': booking,
    })


def tracking_cancel(request, booking_id):
    """Annuler la réservation (avec logique 48h)."""
    if not _check_tracking_access(request, booking_id):
        messages.warning(request, "Veuillez rechercher votre réservation d'abord.")
        return redirect('tracking_search')
    booking = get_object_or_404(Booking, id=booking_id)

    if not booking.can_be_cancelled:
        messages.error(request, "Cette réservation ne peut plus être annulée.")
        return redirect('tracking_detail', booking_id=booking.id)

    free_cancel = booking.free_cancellation_available

    if request.method == 'POST':
        # L'utilisateur a confirmé
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()

        # Remboursement si > 48h ET paiement existant et approuvé
        has_paid = False
        try:
            payment = booking.payment
            if payment and payment.status == 'approved':
                has_paid = True
        except Exception:
            payment = None

        if free_cancel and has_paid:
            booking.refund_requested = True
            if payment:
                # Le statut du paiement reste 'approved' jusqu'à la validation admin
                # L'admin changera manuellement en 'refunded' après traitement CMI
                pass
            messages.success(
                request,
                "Votre réservation est annulée. Un remboursement a été demandé et "
                "sera traité sous 5-7 jours ouvrés."
            )
        else:
            if free_cancel and not has_paid:
                messages.success(
                    request,
                    "Votre réservation est annulée avec succès."
                )
            else:
                messages.success(
                    request,
                    "Votre réservation est annulée. Conformément à nos conditions "
                    "(moins de 48h avant l'arrivée), aucun remboursement n'est possible."
                )

        booking.save()

        # Envoi email d'annulation
        try:
            from .email_service import send_booking_cancellation_to_client
            send_booking_cancellation_to_client(booking)
        except Exception:
            pass  # L'annulation reste valide même si l'email échoue

        return redirect('tracking_detail', booking_id=booking.id)

    return render(request, 'bookings/tracking_cancel.html', {
        'booking': booking,
        'free_cancel': free_cancel,
    })



def _send_confirmation_with_pdf(booking, pdf_buffer):
    """Send confirmation email with PDF attachment."""
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.conf import settings as _s
    from bookings.email_service import _build_context

    ctx = _build_context(booking)
    html = render_to_string('emails/booking_confirmation_client.html', ctx)
    import re
    text = re.sub(r'<[^>]+>', ' ', html).strip()

    msg = EmailMultiAlternatives(
        subject=f"✅ Confirmation de réservation #AL{booking.id:05d} — Al Andalus",
        body=text,
        from_email=_s.DEFAULT_FROM_EMAIL,
        to=[booking.email],
    )
    msg.attach_alternative(html, "text/html")
    msg.attach(
        f"AlAndalus_Reservation_AL{booking.id:05d}.pdf",
        pdf_buffer.read(),
        "application/pdf"
    )
    msg.send()
import uuid, json, logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from bookings.models import Booking
from .models import Payment
from .cmi_gateway import (
    build_payment_form,
    verify_callback,
    get_response_message,
)
from bookings.email_service import send_booking_confirmation_to_client

logger = logging.getLogger(__name__)


def _generate_order_id(booking):
    """Unique order ID: AL + booking_id + timestamp fragment."""
    ts = str(int(timezone.now().timestamp()))[-6:]
    return f"AL{booking.id:05d}-{ts}"


def payment_initiate(request, booking_id):
    """
    Step 1: Show the payment page with CMI form.
    Client sees booking summary + card form (hosted by CMI).
    """
    booking = get_object_or_404(Booking, id=booking_id)

    # Prevent double payment
    if hasattr(booking, 'payment') and booking.payment.is_paid:
        messages.info(request, "Cette réservation a déjà été payée.")
        return redirect('booking_confirmation', booking_id=booking.id)

    # Create or reuse a pending payment record
    if hasattr(booking, 'payment'):
        payment = booking.payment
        if payment.status == 'pending':
            order_id = payment.order_id
        else:
            order_id = _generate_order_id(booking)
            payment.order_id = order_id
            payment.status   = 'pending'
            payment.save()
    else:
        order_id = _generate_order_id(booking)
        payment = Payment.objects.create(
            booking=booking,
            order_id=order_id,
            amount=booking.total_price,
            status='pending',
        )

    is_test = getattr(settings, 'CMI_TEST_MODE', True)
    cmi_data = build_payment_form(booking, order_id, request)

    return render(request, 'payments/payment_page.html', {
        'booking':    booking,
        'payment':    payment,
        'cmi_data':   cmi_data,
        'is_test':    is_test,
    })


@csrf_exempt
def payment_callback(request):
    """
    CMI server-to-server callback (POST).
    Called directly by CMI servers — no browser involved.
    Must return "ACTION=POSTAUTH" to acknowledge.
    """
    if request.method != 'POST':
        return HttpResponse('OK')

    post_data = dict(request.POST)
    # Flatten single-value lists
    post_data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v
                 for k, v in post_data.items()}

    logger.info(f"CMI Callback received: {json.dumps(post_data, default=str)[:500]}")

    result = verify_callback(post_data)
    if not result['verified']:
        logger.error(f"CMI callback verification failed: {result['reason']}")
        return HttpResponse('FAILURE')

    order_id = result.get('order_id', '')
    try:
        payment = Payment.objects.get(order_id=order_id)
    except Payment.DoesNotExist:
        logger.error(f"Payment not found for order_id: {order_id}")
        return HttpResponse('FAILURE')

    # Update payment record
    payment.transaction_id   = result.get('transaction_id', '')
    payment.auth_code        = result.get('auth_code', '')
    payment.response_code    = result.get('response_code', '')
    payment.response_message = result.get('response_msg', '')
    payment.card_last4       = result.get('card_last4', '')
    payment.card_brand       = result.get('card_brand', '')
    payment.raw_response     = json.dumps(post_data, default=str)

    if result['approved']:
        payment.status  = 'approved'
        payment.paid_at = timezone.now()
        # Confirm the booking
        booking = payment.booking
        booking.status = 'confirmed'
        booking.save()
        # Send confirmation email
        try:
            from django.conf import settings as _s
            from bookings.pdf_generator import generate_booking_pdf
            site_url = getattr(_s, 'SITE_URL', 'http://127.0.0.1:8000')
            pdf_buffer = generate_booking_pdf(booking, site_url=site_url)
            _send_confirmation_with_pdf(booking, pdf_buffer)
        except Exception as e:
            logger.warning(f"Email/PDF failed after payment: {e}")
            try:
                send_booking_confirmation_to_client(booking)
            except Exception:
                pass
    else:
        payment.status = 'declined'

    payment.save()

    # CMI requires this exact response to finalize the transaction
    return HttpResponse('ACTION=POSTAUTH')


def payment_success(request):
    """
    Redirect page after successful payment (client browser redirect from CMI).
    """
    order_id = request.GET.get('oid') or request.POST.get('oid', '')
    try:
        payment = Payment.objects.select_related('booking__room').get(order_id=order_id)
        return render(request, 'payments/payment_success.html', {'payment': payment, 'booking': payment.booking})
    except Payment.DoesNotExist:
        messages.error(request, "Référence de paiement introuvable.")
        return redirect('home')


def payment_failure(request):
    """
    Redirect page after failed/cancelled payment.
    """
    order_id = request.GET.get('oid') or request.POST.get('oid', '')
    resp_code = request.GET.get('ProcReturnCode') or request.POST.get('ProcReturnCode', '')
    error_msg = get_response_message(resp_code) if resp_code else "Le paiement n'a pas abouti."

    try:
        payment = Payment.objects.select_related('booking__room').get(order_id=order_id)
        if payment.status == 'pending':
            payment.status = 'declined'
            payment.response_code = resp_code
            payment.save()
        return render(request, 'payments/payment_failure.html', {
            'payment':   payment,
            'booking':   payment.booking,
            'error_msg': error_msg,
        })
    except Payment.DoesNotExist:
        return render(request, 'payments/payment_failure.html', {
            'payment':   None,
            'error_msg': error_msg,
        })


@csrf_exempt
def payment_simulation(request, order_id):
    """
    Simulates CMI payment in TEST mode.
    Shows a fake card form — no real money involved.
    """
    if not getattr(settings, 'CMI_TEST_MODE', True):
        return HttpResponse("Simulation désactivée en production.", status=403)

    payment = get_object_or_404(Payment, order_id=order_id)

    if request.method == 'POST':
        action = request.POST.get('action', 'approve')
        card   = request.POST.get('card_number', '4111111111111111')

        if action == 'approve':
            payment.status         = 'approved'
            payment.paid_at        = timezone.now()
            payment.transaction_id = f"SIM-{uuid.uuid4().hex[:12].upper()}"
            payment.auth_code      = f"A{uuid.uuid4().hex[:5].upper()}"
            payment.response_code  = '00'
            payment.card_last4     = card[-4:]
            payment.card_brand     = 'Visa' if card.startswith('4') else 'Mastercard'
            payment.method         = 'simulation'
            payment.save()

            booking = payment.booking
            booking.status = 'confirmed'
            booking.save()

            try:
                send_booking_confirmation_to_client(booking)
            except Exception:
                pass

            return redirect('payment_success_with_pdf', booking_id=payment.booking.id)
        else:
            payment.status        = 'declined'
            payment.response_code = '05'
            payment.save()
            return redirect(f'/paiement/retour/echec/?oid={order_id}&ProcReturnCode=05')

    return render(request, 'payments/simulation.html', {'payment': payment, 'booking': payment.booking})


def payment_success_with_pdf(request, booking_id):
    """
    Success page shown immediately after payment approval.
    Displays booking summary + PDF download button.
    """
    from bookings.models import Booking
    booking = get_object_or_404(Booking, id=booking_id)
    try:
        payment = booking.payment
    except Exception:
        payment = None

    return render(request, 'payments/payment_success_pdf.html', {
        'booking': booking,
        'payment': payment,
    })

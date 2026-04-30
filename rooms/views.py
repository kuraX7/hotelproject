from django.shortcuts import render, get_object_or_404
from .models import Room, RoomImage
from django.utils import timezone
from django.http import JsonResponse
from content.models import HeroSection, HotelInfo, Service, ServiceGalleryImage, Testimonial, Promotion, ContactMessage

def get_site_context():
    hero = HeroSection.objects.filter(is_active=True).first()
    info = HotelInfo.objects.first()
    return {'hero': hero, 'info': info}

def home(request):
    featured_rooms  = Room.objects.filter(status='available')[:3]
    services        = Service.objects.filter(is_featured=True)[:6]
    testimonials    = Testimonial.objects.filter(is_featured=True)[:3]
    promotions      = Promotion.objects.filter(is_active=True, is_featured=True).order_by('order')[:3]
    from content.models import FAQ
    faqs = FAQ.objects.filter(is_active=True, is_featured=True).order_by('order')[:6]
    ctx = get_site_context()
    import datetime as _dt
    _info = ctx.get('info')
    if _info and _info.years_excellence:
        years_excellence = _info.years_excellence
    else:
        founded = (_info.founded_year if _info else 1985) or 1985
        try:
            years_excellence = _dt.date.today().year - int(founded)
        except Exception:
            years_excellence = 40

    ctx.update({
        'featured_rooms': featured_rooms,
        'services': services,
        'testimonials': testimonials,
        'promotions': promotions,
        'faqs': faqs,
        'years_excellence': years_excellence,
    })
    return render(request, 'home.html', ctx)

def room_list(request):
    from rooms.availability import get_availability
    import datetime

    rooms = Room.objects.all().exclude(status='maintenance')
    category = request.GET.get('category', '')
    if category:
        rooms = rooms.filter(category=category)

    # Check availability for requested dates (optional filters)
    check_in_str  = request.GET.get('check_in', '')
    check_out_str = request.GET.get('check_out', '')
    ci = co = None
    if check_in_str and check_out_str:
        try:
            ci = datetime.date.fromisoformat(check_in_str)
            co = datetime.date.fromisoformat(check_out_str)
        except ValueError:
            pass

    # Attach availability to each room
    rooms_with_avail = []
    for room in rooms:
        if ci and co:
            avail = get_availability(room, ci, co)
        else:
            avail = {'available': True, 'rooms_free': room.room_count,
                     'rooms_total': room.room_count, 'message': '', 'urgency': 'low'}
        rooms_with_avail.append({'room': room, 'avail': avail})

    ctx = get_site_context()
    ctx.update({
        'rooms_with_avail': rooms_with_avail,
        'rooms': rooms,
        'selected_category': category,
        'categories': Room.CATEGORY_CHOICES,
        'check_in':  check_in_str,
        'check_out': check_out_str,
    })
    return render(request, 'rooms/room_list.html', ctx)

def room_detail(request, slug):
    room       = get_object_or_404(Room, slug=slug)
    all_images = room.images.all().order_by('order')
    today      = timezone.now().date()
    room_promos= Promotion.objects.filter(room=room, is_active=True)
    ctx = get_site_context()
    ctx.update({
        'room':        room,
        'all_images':  all_images,
        'today':       today,
        'room_promos': room_promos,
    })
    return render(request, 'rooms/room_detail.html', ctx)

def promotions_page(request):
    promotions = Promotion.objects.filter(is_active=True).order_by('order')
    ctx = get_site_context()
    ctx.update({'promotions': promotions})
    return render(request, 'promotions.html', ctx)


def hotel_rules_page(request):
    from content.models import HotelRules
    rules = HotelRules.get_instance()
    ctx = get_site_context()
    ctx['rules'] = rules
    return render(request, 'hotel_rules.html', ctx)


def faq_page(request):
    from content.models import FAQ
    faqs = FAQ.objects.filter(is_active=True).order_by('order')
    ctx = get_site_context()
    ctx['faqs'] = faqs
    ctx['categories'] = FAQ.CATEGORY_CHOICES
    return render(request, 'faq.html', ctx)


def menu_card_page(request):
    from content.models import MenuCard
    cards = MenuCard.objects.filter(is_active=True).order_by('order')
    ctx = get_site_context()
    ctx['cards'] = cards
    return render(request, 'menu_card.html', ctx)


def service_detail(request, slug):
    from content.models import MenuCard, ServiceGalleryImage
    service = get_object_or_404(Service, slug=slug)
    gallery = service.gallery_images.all()

    # Detect restaurant service to show menu cards
    keywords = ['restaurant', 'cuisine', 'gastronomique', 'repas', 'menu', 'restauration']
    is_restaurant = any(kw in service.name.lower() or kw in service.description.lower() for kw in keywords)
    menu_cards = MenuCard.objects.filter(is_active=True).order_by('order') if is_restaurant else []

    # Other services for the "Discover also" section
    other_services = Service.objects.filter(is_featured=True).exclude(pk=service.pk)[:4]

    ctx = get_site_context()
    ctx.update({
        'service': service,
        'gallery': gallery,
        'menu_cards': menu_cards,
        'is_restaurant': is_restaurant,
        'other_services': other_services,
    })
    return render(request, 'service_detail.html', ctx)


def contact_submit(request):
    """Handle contact form submission — returns JSON for AJAX."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'}, status=405)

    name    = request.POST.get('name', '').strip()
    email   = request.POST.get('email', '').strip()
    phone   = request.POST.get('phone', '').strip()
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()

    # Basic validation
    errors = {}
    if not name:    errors['name']    = 'Le nom est requis.'
    if not email:   errors['email']   = "L'email est requis."
    if not subject: errors['subject'] = 'Le sujet est requis.'
    if not message: errors['message'] = 'Le message est requis.'
    if errors:
        return JsonResponse({'success': False, 'errors': errors}, status=400)

    # Get IP
    ip = (request.META.get('HTTP_X_FORWARDED_FOR') or '').split(',')[0].strip() \
         or request.META.get('REMOTE_ADDR')

    # Save to DB
    contact = ContactMessage.objects.create(
        name=name, email=email, phone=phone,
        subject=subject, message=message, ip_address=ip or None,
    )

    # Send emails (non-blocking — errors are swallowed)
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.conf import settings

        info     = HotelInfo.objects.first()
        site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        ctx      = {'contact': contact, 'info': info, 'site_url': site_url,
                    'dashboard_url': site_url}

        # 1. Notify admin
        admin_email = getattr(settings, 'ADMIN_EMAIL', None) \
                      or getattr(settings, 'EMAIL_HOST_USER', None)
        if admin_email:
            html_admin = render_to_string('emails/contact_notification_admin.html', ctx)
            msg = EmailMultiAlternatives(
                subject=f'[Contact] {subject} — {name}',
                body=f'Nouveau message de {name} ({email}):\n\n{message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[admin_email],
                reply_to=[email],
            )
            msg.attach_alternative(html_admin, 'text/html')
            msg.send(fail_silently=True)

        # 2. Confirm to visitor
        html_client = render_to_string('emails/contact_confirmation_client.html', ctx)
        msg2 = EmailMultiAlternatives(
            subject=f'Nous avons bien reçu votre message — {"Hotel Al Andalus" if not info else info.hotel_name}',
            body=f'Bonjour {name},\nVotre message a bien été reçu. Nous vous répondrons sous 24-48h.\n\nCordialement,\n{"Hôtel Al Andalus" if not info else info.hotel_name}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg2.attach_alternative(html_client, 'text/html')
        msg2.send(fail_silently=True)
    except Exception:
        pass  # Email failure must never break form submission

    return JsonResponse({'success': True,
                         'message': 'Votre message a été envoyé avec succès ! Nous vous répondrons dans les 24-48h.'})

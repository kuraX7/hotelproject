from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from rooms.models import Room, RoomImage
from bookings.models import Booking
from content.models import HeroSection, HotelInfo, Service, Testimonial
from rooms.forms import RoomForm
from dashboard.roles import (
    ROLES, get_role, get_role_info, is_authenticated, is_readonly,
    dashboard_login_required, role_required, readonly_forbidden
)
import datetime, json

INCLUDE_OPTIONS = [
    ('includes_breakfast',  'Petit-déj. inclus'),
    ('includes_parking',    'Parking inclus'),
    ('free_cancellation',   'Annulation gratuite'),
    ('no_prepayment',       'Paiement sur place'),
    ('has_garden_view',     'Vue sur jardin'),
    ('has_pool_view',       'Vue sur piscine'),
    ('has_terrace',         'Terrasse'),
    ('has_soundproofing',   'Insonorisation'),
    ('has_private_bathroom','Salle de bains privée'),
]

AMENITY_ROWS = [
    {'field':'has_wifi',    'label':'WiFi',        'icon':'fas fa-wifi',             'color':'#3B82F6'},
    {'field':'has_ac',      'label':'Climatisation','icon':'fas fa-snowflake',        'color':'#10B981'},
    {'field':'has_balcony', 'label':'Balcon',       'icon':'fas fa-door-open',        'color':'#F59E0B'},
    {'field':'has_sea_view','label':'Vue mer',      'icon':'fas fa-water',            'color':'#8B5CF6'},
    {'field':'has_tv',      'label':'TV',           'icon':'fas fa-tv',               'color':'#374151'},
    {'field':'has_minibar', 'label':'Mini-bar',     'icon':'fas fa-glass-martini-alt','color':'#F97316'},
    {'field':'has_safe',    'label':'Coffre-fort',  'icon':'fas fa-lock',             'color':'#6B7280'},
    {'field':'has_bathtub', 'label':'Baignoire',    'icon':'fas fa-bath',             'color':'#06B6D4'},
]

def get_amenities_rows(room=None):
    return [{**a,'checked':getattr(room,a['field'],False) if room else False} for a in AMENITY_ROWS]

# ── AUTH ──────────────────────────────────────────────
def dashboard_login(request):
    if is_authenticated(request):
        return redirect('dashboard_home')

    error = None
    if request.method == 'POST':
        role_key = request.POST.get('role', '').strip()
        password = request.POST.get('password', '').strip()

        role_info = ROLES.get(role_key)
        if role_info and password == role_info['password']:
            request.session['dashboard_role'] = role_key
            request.session.set_expiry(28800)  # 8h session
            return redirect('dashboard_home')
        else:
            error = 'Mot de passe incorrect ou rôle invalide.'

    return render(request, 'dashboard/login.html', {'roles': ROLES, 'error': error})

def dashboard_logout(request):
    request.session.flush()
    return redirect('dashboard_login')

# ── HOME ──────────────────────────────────────────────
@dashboard_login_required
def dashboard_home(request):
    today = timezone.now().date()
    total_rooms       = Room.objects.count()
    available_rooms   = Room.objects.filter(status='available').count()
    occupied_rooms    = Room.objects.filter(status='occupied').count()
    maintenance_rooms = Room.objects.filter(status='maintenance').count()
    total_bookings    = Booking.objects.count()
    confirmed_bookings= Booking.objects.filter(status='confirmed').count()
    pending_bookings  = Booking.objects.filter(status='pending').count()
    checkins_today    = Booking.objects.filter(check_in=today,  status__in=['confirmed','pending']).count()
    checkouts_today   = Booking.objects.filter(check_out=today, status='confirmed').count()
    revenue_total = Booking.objects.filter(status__in=['confirmed','completed']).aggregate(t=Sum('total_price'))['t'] or 0
    revenue_month = Booking.objects.filter(status__in=['confirmed','completed'],created_at__month=today.month,created_at__year=today.year).aggregate(t=Sum('total_price'))['t'] or 0

    monthly_data,monthly_labels=[],[]
    for i in range(5,-1,-1):
        d=today.replace(day=1)-datetime.timedelta(days=i*30)
        monthly_data.append(Booking.objects.filter(created_at__year=d.year,created_at__month=d.month).count())
        monthly_labels.append(d.strftime('%b %Y'))

    cat_labels,cat_data=[],[]
    for val,label in Room.CATEGORY_CHOICES:
        rev=Booking.objects.filter(room__category=val,status__in=['confirmed','completed']).aggregate(t=Sum('total_price'))['t'] or 0
        cat_labels.append(label); cat_data.append(float(rev))

    recent_bookings = Booking.objects.select_related('room').order_by('-created_at')[:8]
    upcoming = Booking.objects.filter(check_in__gte=today,status__in=['confirmed','pending']).select_related('room').order_by('check_in')[:5]

    # ── DISPONIBILITÉ EN TEMPS RÉEL ──
    avail_date_str = request.GET.get('avail_date', '')
    try:
        avail_date = datetime.date.fromisoformat(avail_date_str) if avail_date_str else today
    except ValueError:
        avail_date = today

    room_availability = []
    total_all = 0
    booked_all = 0
    for room in Room.objects.filter(is_available=True).order_by('name'):
        booked = Booking.objects.filter(
            room=room,
            status__in=['confirmed', 'pending'],
            check_in__lt=avail_date + datetime.timedelta(days=1),
            check_out__gt=avail_date,
        ).count()
        free = max(room.room_count - booked, 0)
        total_all += room.room_count
        booked_all += booked
        room_availability.append({
            'name': room.name,
            'total': room.room_count,
            'booked': booked,
            'free': free,
        })

    return render(request,'dashboard/home.html',{
        'total_rooms':total_rooms,'available_rooms':available_rooms,
        'occupied_rooms':occupied_rooms,'maintenance_rooms':maintenance_rooms,
        'total_bookings':total_bookings,'confirmed_bookings':confirmed_bookings,
        'pending_bookings':pending_bookings,
        'checkins_today':checkins_today,'checkouts_today':checkouts_today,
        'revenue_total':revenue_total,'revenue_month':revenue_month,
        'recent_bookings':recent_bookings,'upcoming':upcoming,
        'rooms':Room.objects.all(),
        'monthly_labels':json.dumps(monthly_labels),'monthly_data':json.dumps(monthly_data),
        'cat_labels':json.dumps(cat_labels),'cat_data':json.dumps(cat_data),
        'today':today,
        'room_availability': room_availability,
        'avail_date': avail_date,
        'avail_total_all': total_all,
        'avail_booked_all': booked_all,
        'avail_free_all': total_all - booked_all,
    })

# ── RECEPTIONIST DASHBOARD ────────────────────────────
@dashboard_login_required
def dashboard_reception(request):
    today    = timezone.now().date()
    # Date navigation
    date_str = request.GET.get('date', today.isoformat())
    try:
        view_date = datetime.date.fromisoformat(date_str)
    except ValueError:
        view_date = today

    prev_date = view_date - datetime.timedelta(days=1)
    next_date = view_date + datetime.timedelta(days=1)

    # All rooms with their booking status for view_date
    rooms = Room.objects.all().order_by('category','price')
    room_data = []

    for room in rooms:
        # Is this room occupied on view_date?
        current = Booking.objects.filter(
            room=room,
            check_in__lte=view_date,
            check_out__gt=view_date,
            status__in=['confirmed','pending']
        ).select_related().first()

        # Arrival on view_date?
        arrival = Booking.objects.filter(
            room=room, check_in=view_date,
            status__in=['confirmed','pending']
        ).first()

        # Departure on view_date?
        departure = Booking.objects.filter(
            room=room, check_out=view_date,
            status='confirmed'
        ).first()

        # Next upcoming booking
        next_booking = Booking.objects.filter(
            room=room, check_in__gt=view_date,
            status__in=['confirmed','pending']
        ).order_by('check_in').first()

        # Determine cell status
        if current:
            if arrival:
                cell_status = 'arriving'       # Arrives today
            elif departure:
                cell_status = 'departing'      # Departs today (should not be occupied after)
            else:
                cell_status = 'occupied'       # Mid-stay
        elif departure:
            cell_status = 'checkout'           # Just checked out
        elif arrival:
            cell_status = 'arriving'
        elif room.status == 'maintenance':
            cell_status = 'maintenance'
        else:
            cell_status = 'free'

        # Days in stay
        nights_in = None
        if current:
            nights_in = (view_date - current.check_in).days + 1
            total_nights = (current.check_out - current.check_in).days

        room_data.append({
            'room':         room,
            'status':       cell_status,
            'booking':      current,
            'arrival':      arrival,
            'departure':    departure,
            'next_booking': next_booking,
            'nights_in':    nights_in,
            'total_nights': total_nights if current else None,
        })

    # Today's summary stats
    arrivals_list  = Booking.objects.filter(check_in=view_date,  status__in=['confirmed','pending']).select_related('room').order_by('check_in')
    departures_list= Booking.objects.filter(check_out=view_date, status='confirmed').select_related('room').order_by('check_out')
    occupied_count = Booking.objects.filter(check_in__lte=view_date,check_out__gt=view_date,status__in=['confirmed','pending']).count()
    free_count     = rooms.count() - occupied_count
    occupancy_rate = round((occupied_count / rooms.count()) * 100) if rooms.count() else 0

    # 7-day planning ahead (for mini timeline)
    timeline_days = [view_date + datetime.timedelta(days=i) for i in range(7)]
    timeline_data = []
    for day in timeline_days:
        occ = Booking.objects.filter(check_in__lte=day,check_out__gt=day,status__in=['confirmed','pending']).count()
        arr = Booking.objects.filter(check_in=day, status__in=['confirmed','pending']).count()
        dep = Booking.objects.filter(check_out=day, status='confirmed').count()
        timeline_data.append({'date':day,'occupied':occ,'arrivals':arr,'departures':dep,'rate':round(occ/rooms.count()*100) if rooms.count() else 0})

    return render(request,'dashboard/reception.html',{
        'room_data':      room_data,
        'view_date':      view_date,
        'today':          today,
        'prev_date':      prev_date,
        'next_date':      next_date,
        'arrivals_list':  arrivals_list,
        'departures_list':departures_list,
        'occupied_count': occupied_count,
        'free_count':     free_count,
        'occupancy_rate': occupancy_rate,
        'total_rooms':    rooms.count(),
        'timeline_data':  timeline_data,
        'is_today':       view_date == today,
    })

@dashboard_login_required
def dashboard_room_quick_status(request, room_id):
    """Quick status change from the reception board."""
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Room.STATUS_CHOICES):
            room.status = new_status
            room.save()
            messages.success(request, f'{room.name} → {room.get_status_display()}')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard_reception'))

# ── ROOMS ─────────────────────────────────────────────
@dashboard_login_required
def dashboard_rooms(request):
    rooms=Room.objects.prefetch_related('images').all()
    sf=request.GET.get('status','')
    if sf: rooms=rooms.filter(status=sf)
    return render(request,'dashboard/rooms.html',{'rooms':rooms,'status_filter':sf,'status_choices':Room.STATUS_CHOICES})

@dashboard_login_required
@role_required('admin')
def dashboard_room_add(request):
    if request.method=='POST':
        name=request.POST.get('name','').strip()
        description=request.POST.get('description','').strip()
        price=request.POST.get('price','')
        if not name or not description or not price:
            messages.error(request,'Veuillez remplir tous les champs obligatoires.')
            return render(request,'dashboard/room_form.html',{'action':'Ajouter','amenities_rows':get_amenities_rows(),'include_options':INCLUDE_OPTIONS})
        try:
            op = request.POST.get('original_price','').strip()
            room=Room(name=name,category=request.POST.get('category','standard'),
                status=request.POST.get('status','available'),description=description,price=price,
                capacity=int(request.POST.get('capacity',2)),size=int(request.POST.get('size',25)),
                room_count=int(request.POST.get('room_count',1) or 1),
                original_price=float(op) if op else None,
                bed_config=request.POST.get('bed_config',''),
                has_wifi='has_wifi' in request.POST,has_ac='has_ac' in request.POST,
                has_balcony='has_balcony' in request.POST,has_sea_view='has_sea_view' in request.POST,
                has_tv='has_tv' in request.POST,has_minibar='has_minibar' in request.POST,
                has_safe='has_safe' in request.POST,has_bathtub='has_bathtub' in request.POST,
                has_garden_view='has_garden_view' in request.POST,
                has_pool_view='has_pool_view' in request.POST,
                has_terrace='has_terrace' in request.POST,
                has_soundproofing='has_soundproofing' in request.POST,
                has_private_bathroom='has_private_bathroom' in request.POST,
                includes_breakfast='includes_breakfast' in request.POST,
                includes_parking='includes_parking' in request.POST,
                free_cancellation='free_cancellation' in request.POST,
                no_prepayment='no_prepayment' in request.POST)
            if request.FILES.get('image'): room.image=request.FILES['image']
            room.save()
            messages.success(request,f'Chambre "{room.name}" créée !')
            return redirect('dashboard_room_edit',room_id=room.id)
        except Exception as e:
            messages.error(request,f'Erreur : {e}')
    return render(request,'dashboard/room_form.html',{'action':'Ajouter','amenities_rows':get_amenities_rows(),'include_options':INCLUDE_OPTIONS})

@dashboard_login_required
@role_required('admin')
def dashboard_room_edit(request,room_id):
    room=get_object_or_404(Room,id=room_id)
    if request.method=='POST':
        try:
            room.name=request.POST.get('name',room.name).strip()
            room.category=request.POST.get('category',room.category)
            room.status=request.POST.get('status',room.status)
            room.description=request.POST.get('description',room.description).strip()
            room.price=request.POST.get('price',room.price)
            room.capacity=int(request.POST.get('capacity',room.capacity))
            room.size=int(request.POST.get('size',room.size))
            room.has_wifi='has_wifi' in request.POST; room.has_ac='has_ac' in request.POST
            room.has_balcony='has_balcony' in request.POST; room.has_sea_view='has_sea_view' in request.POST
            room.has_tv='has_tv' in request.POST; room.has_minibar='has_minibar' in request.POST
            room.has_safe='has_safe' in request.POST; room.has_bathtub='has_bathtub' in request.POST
            room.has_garden_view='has_garden_view' in request.POST
            room.has_pool_view='has_pool_view' in request.POST
            room.has_terrace='has_terrace' in request.POST
            room.has_soundproofing='has_soundproofing' in request.POST
            room.has_private_bathroom='has_private_bathroom' in request.POST
            room.includes_breakfast='includes_breakfast' in request.POST
            room.includes_parking='includes_parking' in request.POST
            room.free_cancellation='free_cancellation' in request.POST
            room.no_prepayment='no_prepayment' in request.POST
            op=request.POST.get('original_price','').strip()
            room.original_price=float(op) if op else None
            room.bed_config=request.POST.get('bed_config', room.bed_config)
            room.room_count=int(request.POST.get('room_count', room.room_count) or room.room_count)
            if request.FILES.get('image'): room.image=request.FILES['image']
            room.save()
            messages.success(request,f'Chambre "{room.name}" mise à jour !')
        except Exception as e: messages.error(request,f'Erreur : {e}')
        return redirect('dashboard_room_edit',room_id=room.id)
    return render(request,'dashboard/room_form.html',{'action':'Modifier','room':room,'images':room.images.all(),'amenities_rows':get_amenities_rows(room),'include_options':INCLUDE_OPTIONS})

@dashboard_login_required
@role_required('admin')
def dashboard_room_delete(request,room_id):
    room=get_object_or_404(Room,id=room_id)
    if request.method=='POST':
        name=room.name; room.delete(); messages.success(request,f'Chambre "{name}" supprimée.')
    return redirect('dashboard_rooms')

@dashboard_login_required
@role_required('admin')
def dashboard_room_toggle(request,room_id):
    room=get_object_or_404(Room,id=room_id)
    room.status='available' if room.status!='available' else 'occupied'; room.save()
    return JsonResponse({'available':room.status=='available','status':room.status,'status_label':room.get_status_display()})

@dashboard_login_required
def dashboard_room_status(request,room_id):
    room=get_object_or_404(Room,id=room_id)
    if request.method=='POST':
        ns=request.POST.get('status')
        if ns in dict(Room.STATUS_CHOICES): room.status=ns; room.save()
    return redirect('dashboard_rooms')

@dashboard_login_required
@role_required('admin')
def dashboard_room_image_add(request,room_id):
    room=get_object_or_404(Room,id=room_id)
    if request.method=='POST':
        url=request.POST.get('image_url','').strip(); caption=request.POST.get('caption','').strip()
        is_360='is_360' in request.POST; is_primary='is_primary' in request.POST
        image_file=request.FILES.get('image_file')
        if url or image_file:
            if is_primary: room.images.update(is_primary=False)
            img=RoomImage(room=room,caption=caption,is_360=is_360,is_primary=is_primary,order=room.images.count())
            if image_file: img.image_file=image_file
            else: img.image_url=url
            img.save(); messages.success(request,'Photo ajoutée !')
        else: messages.error(request,'Fournissez une URL ou uploadez un fichier.')
    return redirect('dashboard_room_edit',room_id=room_id)

@dashboard_login_required
@role_required('admin')
def dashboard_room_image_delete(request,image_id):
    img=get_object_or_404(RoomImage,id=image_id); room_id=img.room_id
    if request.method=='POST': img.delete(); messages.success(request,'Photo supprimée.')
    return redirect('dashboard_room_edit',room_id=room_id)

# ── BOOKINGS ──────────────────────────────────────────
@dashboard_login_required
def dashboard_bookings(request):
    qs=Booking.objects.select_related('room').order_by('-created_at')
    sf=request.GET.get('status',''); q=request.GET.get('q','')
    df=request.GET.get('date_from',''); dt=request.GET.get('date_to','')
    if sf: qs=qs.filter(status=sf)
    if q: qs=qs.filter(Q(name__icontains=q)|Q(email__icontains=q)|Q(room__name__icontains=q)|Q(phone__icontains=q))
    if df: qs=qs.filter(check_in__gte=df)
    if dt: qs=qs.filter(check_out__lte=dt)
    page=Paginator(qs,15).get_page(request.GET.get('page',1))
    return render(request,'dashboard/bookings.html',{'bookings':page,'status_filter':sf,'search':q,'date_from':df,'date_to':dt,'status_choices':Booking.STATUS_CHOICES,'total_count':qs.count()})

@dashboard_login_required
def dashboard_booking_status(request,booking_id):
    booking=get_object_or_404(Booking,id=booking_id)
    if request.method=='POST':
        ns=request.POST.get('status')
        if ns in dict(Booking.STATUS_CHOICES):
            old=booking.status; booking.status=ns; booking.save()
            messages.success(request,f'Réservation #{booking.id} → {booking.get_status_display()}')
            if old!=ns and ns in ('confirmed','cancelled'):
                from bookings.email_service import send_booking_status_update_to_client
                send_booking_status_update_to_client(booking)
    return redirect(request.META.get('HTTP_REFERER','dashboard_bookings'))

@dashboard_login_required
@role_required('admin')
def dashboard_booking_delete(request,booking_id):
    b=get_object_or_404(Booking,id=booking_id)
    if request.method=='POST': b.delete(); messages.success(request,'Réservation supprimée.')
    return redirect('dashboard_bookings')

@dashboard_login_required
def dashboard_booking_notes(request,booking_id):
    b=get_object_or_404(Booking,id=booking_id)
    if request.method=='POST': b.admin_notes=request.POST.get('admin_notes',''); b.save(); messages.success(request,'Notes enregistrées.')
    return redirect(request.META.get('HTTP_REFERER','dashboard_bookings'))

# ── CMS ───────────────────────────────────────────────
@dashboard_login_required
@role_required('admin')
def dashboard_hero(request):
    hero=HeroSection.objects.first() or HeroSection.objects.create()
    if request.method=='POST':
        for f in ['title_line1','title_line2','title_line3','subtitle','badge_text','bg_image_url','btn_primary_text','btn_secondary_text']:
            setattr(hero,f,request.POST.get(f,getattr(hero,f)))
        if request.FILES.get('bg_image_file'): hero.bg_image_file=request.FILES['bg_image_file']
        hero.save(); messages.success(request,'Section hero mise à jour !')
        return redirect('dashboard_hero')
    return render(request,'dashboard/cms_hero.html',{'hero':hero})

@dashboard_login_required
@role_required('admin')
def dashboard_hotel_info(request):
    info = HotelInfo.objects.first() or HotelInfo.objects.create()
    if request.method == 'POST':
        # All text fields
        text_fields = [
            'hotel_name','tagline','about_title','about_text1','about_text2',
            'about_image_url','about_image_accent_url',
            'founded_year','address','phone','email','checkin_time','checkout_time',
            'stars','total_rooms','satisfaction_rate',
            'facebook_url','instagram_url','whatsapp_number','google_maps_url',
            'feature_1_icon','feature_1_text','feature_2_icon','feature_2_text',
            'feature_3_icon','feature_3_text','feature_4_icon','feature_4_text',
            'hero_rooms_image_url','hero_detail_image_url',
            'hero_booking_image_url','cta_image_url',
        ]
        for f in text_fields:
            val = request.POST.get(f)
            if val is not None:
                setattr(info, f, val)
        # Champs entiers : convertir la chaîne vide en None
        integer_fields = ['years_excellence']
        for f in integer_fields:
            val = request.POST.get(f)
            if val is not None:
                setattr(info, f, int(val) if val.strip() != '' else None)
        # File uploads
        if request.FILES.get('about_image_file'):
            info.about_image_file = request.FILES['about_image_file']
        if request.FILES.get('about_image_accent_file'):
            info.about_image_accent_file = request.FILES['about_image_accent_file']
        info.save()
        messages.success(request, 'Informations hôtel mises à jour !')
        return redirect('dashboard_hotel_info')

    feature_items = [
        (1, info.feature_1_icon, info.feature_1_text),
        (2, info.feature_2_icon, info.feature_2_text),
        (3, info.feature_3_icon, info.feature_3_text),
        (4, info.feature_4_icon, info.feature_4_text),
    ]
    hero_images = [
        ("Image fond — Page Chambres",        'hero_rooms_image_url',   info.hero_rooms_image_url),
        ("Image fond — Page Détail chambre",   'hero_detail_image_url',  info.hero_detail_image_url),
        ("Image fond — Page Réservation",      'hero_booking_image_url', info.hero_booking_image_url),
        ("Image fond — Section CTA (accueil)", 'cta_image_url',          info.cta_image_url),
    ]
    import datetime as _dt
    _founded = info.founded_year or 1985
    _yrs = info.years_excellence if info.years_excellence else (_dt.date.today().year - int(_founded))
    return render(request, 'dashboard/cms_hotel_info.html', {
        'info': info,
        'feature_items': feature_items,
        'hero_images': hero_images,
        'years_excellence': _yrs,
    })

@dashboard_login_required
@role_required('admin')
def dashboard_services(request):
    return render(request,'dashboard/cms_services.html',{'services':Service.objects.all()})

@dashboard_login_required
@role_required('admin')
def dashboard_service_add(request):
    if request.method=='POST':
        name=request.POST.get('name','').strip()
        if not name: messages.error(request,'Le nom est obligatoire.'); return redirect('dashboard_services')
        svc=Service(name=name,description=request.POST.get('description',''),icon_class=request.POST.get('icon_class','fas fa-concierge-bell'),image_url=request.POST.get('image_url',''),is_featured='is_featured' in request.POST,order=int(request.POST.get('order',0) or 0))
        if request.FILES.get('image_file'): svc.image_file=request.FILES['image_file']
        svc.save(); messages.success(request,f'Service "{svc.name}" créé !')
    return redirect('dashboard_services')

@dashboard_login_required
@role_required('admin')
def dashboard_service_edit(request,service_id):
    svc=get_object_or_404(Service,id=service_id)
    if request.method=='POST':
        svc.name=request.POST.get('name',svc.name).strip(); svc.description=request.POST.get('description',svc.description)
        svc.icon_class=request.POST.get('icon_class',svc.icon_class); svc.image_url=request.POST.get('image_url',svc.image_url)
        svc.is_featured='is_featured' in request.POST; svc.order=int(request.POST.get('order',svc.order) or svc.order)
        if request.FILES.get('image_file'): svc.image_file=request.FILES['image_file']
        svc.save(); messages.success(request,f'Service "{svc.name}" mis à jour !'); return redirect('dashboard_services')
    return render(request,'dashboard/cms_service_form.html',{'action':'Modifier','svc':svc})

@dashboard_login_required
@role_required('admin')
def dashboard_service_delete(request,service_id):
    svc=get_object_or_404(Service,id=service_id)
    if request.method=='POST': name=svc.name; svc.delete(); messages.success(request,f'Service "{name}" supprimé.')
    return redirect('dashboard_services')

@dashboard_login_required
@role_required('admin')
def dashboard_service_toggle(request,service_id):
    svc=get_object_or_404(Service,id=service_id)
    if request.method=='POST': svc.is_featured=not svc.is_featured; svc.save()
    return JsonResponse({'is_featured':svc.is_featured})

@dashboard_login_required
@role_required('admin')
def dashboard_testimonials(request):
    return render(request,'dashboard/cms_testimonials.html',{'testimonials':Testimonial.objects.all()})

@dashboard_login_required
@role_required('admin')
def dashboard_testimonial_save(request,testimonial_id=None):
    t=get_object_or_404(Testimonial,id=testimonial_id) if testimonial_id else Testimonial()
    if request.method=='POST':
        t.name=request.POST.get('name','').strip(); t.origin=request.POST.get('origin','').strip()
        t.text=request.POST.get('text','').strip(); t.rating=int(request.POST.get('rating',5) or 5)
        t.is_featured='is_featured' in request.POST; t.order=int(request.POST.get('order',0) or 0)
        if t.name and t.text: t.save(); messages.success(request,f'Témoignage de "{t.name}" enregistré !')
        else: messages.error(request,'Nom et témoignage obligatoires.')
    return redirect('dashboard_testimonials')

@dashboard_login_required
@role_required('admin')
def dashboard_testimonial_delete(request,testimonial_id):
    t=get_object_or_404(Testimonial,id=testimonial_id)
    if request.method=='POST': t.delete(); messages.success(request,'Témoignage supprimé.')
    return redirect('dashboard_testimonials')

# ── PROMOTIONS ────────────────────────────────────────
@dashboard_login_required
@role_required('admin')
def dashboard_promotions(request):
    from content.models import Promotion
    return render(request,'dashboard/promotions.html',{'promotions':Promotion.objects.select_related('room').all(),'rooms':Room.objects.filter(status='available'),'badge_choices':Promotion.BADGE_CHOICES})

@dashboard_login_required
@role_required('admin')
def dashboard_promotion_add(request):
    from content.models import Promotion
    if request.method=='POST':
        title=request.POST.get('title','').strip()
        if not title: messages.error(request,'Titre obligatoire.'); return redirect('dashboard_promotions')
        p=Promotion(title=title,subtitle=request.POST.get('subtitle',''),description=request.POST.get('description',''),badge=request.POST.get('badge','limited'),discount_pct=int(request.POST.get('discount_pct',0) or 0),discount_label=request.POST.get('discount_label',''),image_url=request.POST.get('image_url',''),cta_text=request.POST.get('cta_text','En profiter'),is_active='is_active' in request.POST,is_featured='is_featured' in request.POST,order=int(request.POST.get('order',0) or 0))
        rid=request.POST.get('room')
        if rid: p.room_id=int(rid)
        vf=request.POST.get('valid_from'); vu=request.POST.get('valid_until')
        if vf: p.valid_from=vf
        if vu: p.valid_until=vu
        if request.FILES.get('image_file'): p.image_file=request.FILES['image_file']
        p.save(); messages.success(request,f'Promotion "{p.title}" créée !')
    return redirect('dashboard_promotions')

@dashboard_login_required
@role_required('admin')
def dashboard_promotion_edit(request,promo_id):
    from content.models import Promotion
    p=get_object_or_404(Promotion,id=promo_id)
    if request.method=='POST':
        p.title=request.POST.get('title',p.title).strip(); p.subtitle=request.POST.get('subtitle',p.subtitle)
        p.description=request.POST.get('description',p.description); p.badge=request.POST.get('badge',p.badge)
        p.discount_pct=int(request.POST.get('discount_pct',p.discount_pct) or 0); p.discount_label=request.POST.get('discount_label',p.discount_label)
        p.image_url=request.POST.get('image_url',p.image_url); p.cta_text=request.POST.get('cta_text',p.cta_text)
        p.is_active='is_active' in request.POST; p.is_featured='is_featured' in request.POST
        p.order=int(request.POST.get('order',p.order) or p.order)
        rid=request.POST.get('room'); p.room_id=int(rid) if rid else None
        vf=request.POST.get('valid_from'); vu=request.POST.get('valid_until')
        p.valid_from=vf if vf else None; p.valid_until=vu if vu else None
        if request.FILES.get('image_file'): p.image_file=request.FILES['image_file']
        p.save(); messages.success(request,f'Promotion "{p.title}" mise à jour !')
    return redirect('dashboard_promotions')

@dashboard_login_required
@role_required('admin')
def dashboard_promotion_delete(request,promo_id):
    from content.models import Promotion
    p=get_object_or_404(Promotion,id=promo_id)
    if request.method=='POST': title=p.title; p.delete(); messages.success(request,f'Promotion "{title}" supprimée.')
    return redirect('dashboard_promotions')

@dashboard_login_required
@role_required('admin')
def dashboard_promotion_toggle(request,promo_id):
    from content.models import Promotion
    p=get_object_or_404(Promotion,id=promo_id)
    if request.method=='POST': p.is_active=not p.is_active; p.save()
    return JsonResponse({'is_active':p.is_active})

# ── MEDIA ─────────────────────────────────────────────
@dashboard_login_required
@role_required('admin')
def dashboard_media(request):
    return render(request,'dashboard/media.html',{'rooms':Room.objects.prefetch_related('images').all(),'hero':HeroSection.objects.first(),'hotel_info':HotelInfo.objects.first(),'services':Service.objects.all()})

# ── EMAILS ────────────────────────────────────────────
@dashboard_login_required
@role_required('admin')
def dashboard_email_settings(request):
    from django.conf import settings as ds
    backend=ds.EMAIL_BACKEND
    is_console='console' in backend; is_smtp='smtp' in backend
    if is_console: sc,sb,si,st,sd,sl='#F59E0B','#FEF3C7','🖥️','Mode Console (développement)',"Les emails s'affichent dans le terminal.",'Console'
    elif is_smtp:  sc,sb,si,st,sd,sl='#10B981','#D1FAE5','✅','SMTP actif',f"Serveur : {ds.EMAIL_HOST}",'SMTP'
    else:          sc,sb,si,st,sd,sl='#EF4444','#FEE2E2','❌','Backend inconnu',backend,'Inconnu'
    email_types=[{'key':'confirmation','icon':'✅','bg':'#D1FAE5','title':'Confirmation (client)','desc':'Envoyé après chaque réservation'},{'key':'notification','icon':'🔔','bg':'#EDE9FE','title':'Notification (admin)','desc':'Envoyé à l\'admin à chaque réservation'},{'key':'cancellation','icon':'❌','bg':'#FEE2E2','title':'Annulation (client)','desc':'Envoyé quand statut = Annulée'}]
    return render(request,'dashboard/email_settings.html',{'status_color':sc,'status_bg':sb,'status_icon':si,'status_title':st,'status_desc':sd,'status_label':sl,'email_types':email_types})

@dashboard_login_required
@role_required('admin')
def dashboard_email_test(request):
    if request.method=='POST':
        test_email=request.POST.get('test_email','').strip()
        if not test_email: messages.error(request,'Email requis.'); return redirect('dashboard_email_settings')
        room=Room.objects.first()
        if not room: messages.error(request,'Aucune chambre pour le test.'); return redirect('dashboard_email_settings')
        from bookings.email_service import _send_email,_build_context
        import types,datetime as dt
        fake=types.SimpleNamespace(id=99999,name="Test (AL Andalus)",email=test_email,phone="",room=room,check_in=timezone.now().date()+dt.timedelta(days=7),check_out=timezone.now().date()+dt.timedelta(days=10),guests=2,total_price=room.price*3,status='confirmed',special_requests="Email de test.",created_at=timezone.now(),nights=3,get_status_display=lambda:"Confirmée")
        ok=_send_email(f"[TEST] Confirmation — Al Andalus",test_email,'emails/booking_confirmation_client.html',_build_context(fake))
        if ok: messages.success(request,f'Email de test envoyé à {test_email} !')
        else:  messages.error(request,'Échec envoi. Vérifiez la configuration SMTP.')
    return redirect('dashboard_email_settings')

@dashboard_login_required
@role_required('admin')
def dashboard_email_preview(request,email_type):
    from bookings.email_service import _build_context
    from django.template.loader import render_to_string
    from django.http import HttpResponse
    import types,datetime as dt
    room=Room.objects.first()
    if not room: return HttpResponse("Aucune chambre disponible.")
    fake=types.SimpleNamespace(id=12345,name="Sophie Martin",email="sophie@example.com",phone="+33612345678",room=room,check_in=timezone.now().date()+dt.timedelta(days=14),check_out=timezone.now().date()+dt.timedelta(days=17),guests=2,total_price=room.price*3,status='confirmed',special_requests="Vue sur mer si possible.",created_at=timezone.now(),nights=3,get_status_display=lambda:"Confirmée")
    tpl={'confirmation':'emails/booking_confirmation_client.html','notification':'emails/booking_notification_admin.html','cancellation':'emails/booking_cancellation_client.html'}.get(email_type,'emails/booking_confirmation_client.html')
    return HttpResponse(render_to_string(tpl,_build_context(fake)))

# ── PAYMENTS ──────────────────────────────────────────
@dashboard_login_required
@role_required('admin')
def dashboard_payments(request):
    from payments.models import Payment
    qs=Payment.objects.select_related('booking__room').order_by('-created_at')
    sf=request.GET.get('status','')
    if sf: qs=qs.filter(status=sf)
    total=Payment.objects.filter(status='approved').aggregate(t=Sum('amount'))['t'] or 0
    pending=Payment.objects.filter(status='pending').count()
    return render(request,'dashboard/payments.html',{'payments':qs,'status_filter':sf,'total_approved':total,'total_pending':pending,'status_choices':Payment.STATUS_CHOICES})


# ── HOTEL RULES ───────────────────────────────────────
@dashboard_login_required
@role_required('admin')
def dashboard_rules(request):
    from content.models import HotelRules
    r = HotelRules.get_instance()
    if request.method == 'POST':
        # Times
        r.checkin_from   = request.POST.get('checkin_from',  '14:00')
        r.checkin_until  = request.POST.get('checkin_until', '23:00')
        r.checkout_from  = request.POST.get('checkout_from', '06:00')
        r.checkout_until = request.POST.get('checkout_until','12:00')
        # Policies
        r.cancellation_policy = request.POST.get('cancellation_policy', r.cancellation_policy)
        r.prepayment_policy   = request.POST.get('prepayment_policy',   r.prepayment_policy)
        # Children
        r.children_allowed    = 'children_allowed'    in request.POST
        r.children_policy     = request.POST.get('children_policy',     r.children_policy)
        r.baby_cot_available  = 'baby_cot_available'  in request.POST
        r.baby_cot_age_range  = request.POST.get('baby_cot_age_range',  r.baby_cot_age_range)
        r.baby_cot_price      = request.POST.get('baby_cot_price',      r.baby_cot_price)
        r.extra_bed_available = 'extra_bed_available' in request.POST
        r.extra_bed_price     = request.POST.get('extra_bed_price',     r.extra_bed_price)
        # Age
        r.age_restriction       = 'age_restriction' in request.POST
        r.age_minimum           = int(request.POST.get('age_minimum', 18) or 18)
        r.age_restriction_notes = request.POST.get('age_restriction_notes', r.age_restriction_notes)
        # Others
        r.pets_allowed     = 'pets_allowed'     in request.POST
        r.pets_policy      = request.POST.get('pets_policy',      r.pets_policy)
        r.smoking_allowed  = 'smoking_allowed'  in request.POST
        r.smoking_notes    = request.POST.get('smoking_notes',    r.smoking_notes)
        r.parties_allowed  = 'parties_allowed'  in request.POST
        r.parties_notes    = request.POST.get('parties_notes',    r.parties_notes)
        r.groups_policy    = request.POST.get('groups_policy',    r.groups_policy)
        r.additional_rules = request.POST.get('additional_rules', r.additional_rules)
        # Payments
        r.accepts_visa          = 'accepts_visa'          in request.POST
        r.accepts_mastercard    = 'accepts_mastercard'    in request.POST
        r.accepts_amex          = 'accepts_amex'          in request.POST
        r.accepts_cash          = 'accepts_cash'          in request.POST
        r.accepts_cmi           = 'accepts_cmi'           in request.POST
        r.accepts_bank_transfer = 'accepts_bank_transfer' in request.POST
        r.save()
        messages.success(request, '✅ Règles de la maison mises à jour !')
        return redirect('dashboard_rules')
    return render(request, 'dashboard/cms_rules.html', {'r': r})


# ── FAQ ───────────────────────────────────────────────
@dashboard_login_required
@role_required('admin')
def dashboard_faq(request):
    from content.models import FAQ
    return render(request, 'dashboard/cms_faq.html', {
        'faqs': FAQ.objects.all(),
        'categories': FAQ.CATEGORY_CHOICES,
    })

@dashboard_login_required
@role_required('admin')
def dashboard_faq_add(request):
    from content.models import FAQ
    if request.method == 'POST':
        q = request.POST.get('question','').strip()
        a = request.POST.get('answer','').strip()
        if q and a:
            FAQ.objects.create(
                question    = q,
                answer      = a,
                answer_items= request.POST.get('answer_items',''),
                category    = request.POST.get('category','general'),
                order       = int(request.POST.get('order', 0) or 0),
                is_active   = 'is_active'   in request.POST,
                is_featured = 'is_featured' in request.POST,
            )
            messages.success(request, f'✅ Question ajoutée !')
        else:
            messages.error(request, 'Question et réponse obligatoires.')
    return redirect('dashboard_faq')

@dashboard_login_required
@role_required('admin')
def dashboard_faq_edit(request, faq_id):
    from content.models import FAQ
    faq = get_object_or_404(FAQ, id=faq_id)
    if request.method == 'POST':
        faq.question     = request.POST.get('question', faq.question).strip()
        faq.answer       = request.POST.get('answer',   faq.answer).strip()
        faq.answer_items = request.POST.get('answer_items', faq.answer_items)
        faq.category     = request.POST.get('category', faq.category)
        faq.order        = int(request.POST.get('order', faq.order) or faq.order)
        faq.is_active    = 'is_active'   in request.POST
        faq.is_featured  = 'is_featured' in request.POST
        faq.save()
        messages.success(request, '✅ Question mise à jour !')
    return redirect('dashboard_faq')

@dashboard_login_required
@role_required('admin')
def dashboard_faq_delete(request, faq_id):
    from content.models import FAQ
    faq = get_object_or_404(FAQ, id=faq_id)
    if request.method == 'POST':
        faq.delete()
        messages.success(request, '✅ Question supprimée.')
    return redirect('dashboard_faq')

@dashboard_login_required
@role_required('admin')
def dashboard_faq_toggle(request, faq_id):
    from content.models import FAQ
    faq = get_object_or_404(FAQ, id=faq_id)
    if request.method == 'POST':
        faq.is_active = not faq.is_active
        faq.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard_faq'))

@dashboard_login_required
@role_required('admin')
def dashboard_faq_toggle_featured(request, faq_id):
    from content.models import FAQ
    faq = get_object_or_404(FAQ, id=faq_id)
    if request.method == 'POST':
        faq.is_featured = not faq.is_featured
        faq.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard_faq'))


# ── MENU CARD ─────────────────────────────────────────
@dashboard_login_required
@role_required('admin')
def dashboard_menu_card(request):
    from content.models import MenuCard
    return render(request, 'dashboard/menu_card.html', {
        'cards': MenuCard.objects.all()
    })

@dashboard_login_required
@role_required('admin')
def dashboard_menu_card_add(request):
    from content.models import MenuCard
    if request.method == 'POST':
        title = request.POST.get('title','').strip()
        if not title:
            messages.error(request, 'Le titre est obligatoire.')
            return redirect('dashboard_menu_card')
        card = MenuCard(
            title       = title,
            description = request.POST.get('description',''),
            image_url   = request.POST.get('image_url',''),
            order       = int(request.POST.get('order', 0) or 0),
            is_active   = 'is_active' in request.POST,
        )
        if request.FILES.get('image_file'):
            card.image_file = request.FILES['image_file']
        card.save()
        messages.success(request, f'Image "{card.title}" ajoutée !')
    return redirect('dashboard_menu_card')

@dashboard_login_required
@role_required('admin')
def dashboard_menu_card_edit(request, card_id):
    from content.models import MenuCard
    card = get_object_or_404(MenuCard, id=card_id)
    if request.method == 'POST':
        card.title       = request.POST.get('title', card.title).strip()
        card.description = request.POST.get('description', card.description)
        card.image_url   = request.POST.get('image_url', card.image_url)
        card.order       = int(request.POST.get('order', card.order) or card.order)
        card.is_active   = 'is_active' in request.POST
        if request.FILES.get('image_file'):
            card.image_file = request.FILES['image_file']
        card.save()
        messages.success(request, f'Image "{card.title}" mise à jour !')
    return redirect('dashboard_menu_card')

@dashboard_login_required
@role_required('admin')
def dashboard_menu_card_delete(request, card_id):
    from content.models import MenuCard
    card = get_object_or_404(MenuCard, id=card_id)
    if request.method == 'POST':
        title = card.title
        card.delete()
        messages.success(request, f'Image "{title}" supprimée.')
    return redirect('dashboard_menu_card')

@dashboard_login_required
@role_required('admin')
def dashboard_menu_card_toggle(request, card_id):
    from content.models import MenuCard
    card = get_object_or_404(MenuCard, id=card_id)
    if request.method == 'POST':
        card.is_active = not card.is_active
        card.save()
        messages.success(request, f'{"Visible" if card.is_active else "Masqué"} : {card.title}')
    return redirect('dashboard_menu_card')

# ── ACTIVITIES & DESTINATIONS ─────────────────────────
@dashboard_login_required
@role_required('admin')
def dashboard_activities(request):
    from content.models import Activity
    return render(request, 'dashboard/cms_activities.html', {
        'activities': Activity.objects.all(),
    })

@dashboard_login_required
@role_required('admin')
def dashboard_activity_add(request):
    from content.models import Activity
    if request.method == 'POST':
        a = Activity(
            name=request.POST.get('name', ''),
            description=request.POST.get('description', ''),
            image_url=request.POST.get('image_url', ''),
            is_active='is_active' in request.POST,
            order=int(request.POST.get('order', 0) or 0),
        )
        if request.FILES.get('image_file'):
            a.image_file = request.FILES['image_file']
        a.save()
        messages.success(request, f'Activité « {a.name} » ajoutée.')
    return redirect('dashboard_activities')

@dashboard_login_required
@role_required('admin')
def dashboard_activity_edit(request, activity_id):
    from content.models import Activity
    a = get_object_or_404(Activity, id=activity_id)
    if request.method == 'POST':
        a.name = request.POST.get('name', a.name)
        a.description = request.POST.get('description', a.description)
        a.image_url = request.POST.get('image_url', a.image_url)
        a.is_active = 'is_active' in request.POST
        a.order = int(request.POST.get('order', a.order) or a.order)
        if request.FILES.get('image_file'):
            a.image_file = request.FILES['image_file']
        a.save()
        messages.success(request, f'Activité « {a.name} » modifiée.')
    return redirect('dashboard_activities')

@dashboard_login_required
@role_required('admin')
def dashboard_activity_delete(request, activity_id):
    from content.models import Activity
    a = get_object_or_404(Activity, id=activity_id)
    if request.method == 'POST':
        name = a.name
        a.delete()
        messages.success(request, f'Activité « {name} » supprimée.')
    return redirect('dashboard_activities')

@dashboard_login_required
@role_required('admin')
def dashboard_activity_toggle(request, activity_id):
    from content.models import Activity
    a = get_object_or_404(Activity, id=activity_id)
    if request.method == 'POST':
        a.is_active = not a.is_active
        a.save()
        messages.success(request, f'{"Visible" if a.is_active else "Masqué"} : {a.name}')
    return redirect('dashboard_activities')


# ─── CONTACT MESSAGES ────────────────────────────────────────────────────────

@dashboard_login_required
def dashboard_contact_messages(request):
    from content.models import ContactMessage
    status_filter = request.GET.get('status', '')
    qs = ContactMessage.objects.all()
    if status_filter:
        qs = qs.filter(status=status_filter)
    # Mark 'new' messages as 'read' when admin opens the list
    ContactMessage.objects.filter(status='new').update(status='read')
    unread_count = 0  # already marked read above
    return render(request, 'dashboard/contact_messages.html', {
        'msgs': qs,
        'status_filter': status_filter,
        'total': ContactMessage.objects.count(),
        'new_count': ContactMessage.objects.filter(status='new').count(),
    })


@dashboard_login_required
def dashboard_contact_status(request, msg_id):
    from content.models import ContactMessage
    msg = get_object_or_404(ContactMessage, id=msg_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ContactMessage.STATUS_CHOICES):
            msg.status = new_status
            msg.save()
    return redirect('dashboard_contact_messages')


@dashboard_login_required
@role_required('admin')
def dashboard_contact_delete(request, msg_id):
    from content.models import ContactMessage
    msg = get_object_or_404(ContactMessage, id=msg_id)
    if request.method == 'POST':
        msg.delete()
        messages.success(request, 'Message supprimé.')
    return redirect('dashboard_contact_messages')

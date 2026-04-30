from django import template
from content.models import HotelInfo, Service, HeroSection, Activity

register = template.Library()

@register.simple_tag
def get_hotel_info():
    return HotelInfo.objects.first()

@register.simple_tag
def get_services():
    return Service.objects.filter(is_featured=True)[:6]

@register.simple_tag
def get_hero():
    return HeroSection.objects.filter(is_active=True).first()

@register.simple_tag
def get_pending_count():
    from bookings.models import Booking
    return Booking.objects.filter(status='pending').count()

@register.simple_tag
def get_activities():
    return Activity.objects.filter(is_active=True)

@register.simple_tag
def get_new_contact_count():
    from content.models import ContactMessage
    return ContactMessage.objects.filter(status='new').count()

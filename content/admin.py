from django.contrib import admin
from .models import HeroSection, HotelInfo, Service, ServiceGalleryImage, Testimonial, ContactMessage


@admin.register(HeroSection)
class HeroAdmin(admin.ModelAdmin):
    list_display = ['title_line2', 'is_active']


@admin.register(HotelInfo)
class HotelInfoAdmin(admin.ModelAdmin):
    list_display = ['hotel_name', 'phone', 'email']


class ServiceGalleryInline(admin.TabularInline):
    model = ServiceGalleryImage
    extra = 3
    fields = ['image_file', 'image_url', 'caption', 'order']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug', 'icon_class', 'is_featured', 'order']
    list_editable = ['order', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServiceGalleryInline]
    fieldsets = [
        ('Informations principales', {
            'fields': ('name', 'slug', 'icon_class', 'is_featured', 'order')
        }),
        ('Descriptions', {
            'fields': ('description', 'long_description')
        }),
        ('Image principale', {
            'fields': ('image_file', 'image_url')
        }),
    ]


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display  = ['name', 'origin', 'rating', 'is_featured', 'order']
    list_editable = ['order', 'is_featured']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter   = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'ip_address', 'created_at']
    list_editable = ['status']

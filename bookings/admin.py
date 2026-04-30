from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'room', 'check_in', 'check_out', 'nights', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'room', 'check_in']
    list_editable = ['status']
    search_fields = ['name', 'email', 'room__name']
    readonly_fields = ['total_price', 'created_at']
    date_hierarchy = 'check_in'
    fieldsets = (
        ('Client', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Réservation', {
            'fields': ('room', 'check_in', 'check_out', 'guests', 'total_price', 'status')
        }),
        ('Détails', {
            'fields': ('special_requests', 'created_at'),
            'classes': ('collapse',)
        }),
    )

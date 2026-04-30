from django.contrib import admin
from .models import Room, RoomImage

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 2
    fields = ['image_url', 'image_file', 'caption', 'is_360', 'is_primary', 'order']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'capacity', 'size', 'is_available']
    list_filter = ['category', 'is_available', 'has_sea_view', 'has_balcony']
    list_editable = ['price', 'is_available']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [RoomImageInline]
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'category', 'description', 'price', 'capacity', 'size')
        }),
        ('Image principale (optionnel)', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Disponibilité & Équipements', {
            'fields': ('is_available', 'has_wifi', 'has_ac', 'has_balcony', 'has_sea_view'),
        }),
    )

@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ['room', 'caption', 'is_360', 'is_primary', 'order']
    list_filter = ['room', 'is_360', 'is_primary']

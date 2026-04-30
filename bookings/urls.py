from django.urls import path
from . import views

urlpatterns = [
    path('chambre/<int:room_id>/', views.book_room, name='book_room'),
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('disponibilite/<int:room_id>/', views.check_availability, name='check_availability'),
    path('calendrier/<int:room_id>/', views.room_calendar_data, name='room_calendar_data'),
    path('pdf/<int:booking_id>/', views.booking_pdf, name='booking_pdf'),
    # Tracking / Suivi de réservation
    path('suivi/', views.tracking_search, name='tracking_search'),
    path('suivi/<int:booking_id>/', views.tracking_detail, name='tracking_detail'),
    path('suivi/<int:booking_id>/modifier/', views.tracking_edit, name='tracking_edit'),
    path('suivi/<int:booking_id>/annuler/', views.tracking_cancel, name='tracking_cancel'),
]

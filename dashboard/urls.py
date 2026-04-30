from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('login/', views.dashboard_login, name='dashboard_login'),
    path('logout/', views.dashboard_logout, name='dashboard_logout'),
    # Rooms
    path('chambres/', views.dashboard_rooms, name='dashboard_rooms'),
    path('chambres/ajouter/', views.dashboard_room_add, name='dashboard_room_add'),
    path('chambres/<int:room_id>/modifier/', views.dashboard_room_edit, name='dashboard_room_edit'),
    path('chambres/<int:room_id>/supprimer/', views.dashboard_room_delete, name='dashboard_room_delete'),
    path('chambres/<int:room_id>/toggle/', views.dashboard_room_toggle, name='dashboard_room_toggle'),
    path('chambres/<int:room_id>/statut/', views.dashboard_room_status, name='dashboard_room_status'),
    path('chambres/<int:room_id>/image/', views.dashboard_room_image_add, name='dashboard_room_image_add'),
    path('images/<int:image_id>/supprimer/', views.dashboard_room_image_delete, name='dashboard_room_image_delete'),
    # Bookings
    path('reservations/', views.dashboard_bookings, name='dashboard_bookings'),
    path('reservations/<int:booking_id>/statut/', views.dashboard_booking_status, name='dashboard_booking_status'),
    path('reservations/<int:booking_id>/supprimer/', views.dashboard_booking_delete, name='dashboard_booking_delete'),
    path('reservations/<int:booking_id>/notes/', views.dashboard_booking_notes, name='dashboard_booking_notes'),
    # Promotions
    path('promotions/', views.dashboard_promotions, name='dashboard_promotions'),
    path('promotions/ajouter/', views.dashboard_promotion_add, name='dashboard_promotion_add'),
    path('promotions/<int:promo_id>/modifier/', views.dashboard_promotion_edit, name='dashboard_promotion_edit'),
    path('promotions/<int:promo_id>/supprimer/', views.dashboard_promotion_delete, name='dashboard_promotion_delete'),
    path('promotions/<int:promo_id>/toggle/', views.dashboard_promotion_toggle, name='dashboard_promotion_toggle'),
    # CMS
    path('contenu/hero/', views.dashboard_hero, name='dashboard_hero'),
    path('contenu/hotel/', views.dashboard_hotel_info, name='dashboard_hotel_info'),
    path('contenu/services/', views.dashboard_services, name='dashboard_services'),
    path('contenu/services/ajouter/', views.dashboard_service_add, name='dashboard_service_add'),
    path('contenu/services/<int:service_id>/modifier/', views.dashboard_service_edit, name='dashboard_service_edit'),
    path('contenu/services/<int:service_id>/supprimer/', views.dashboard_service_delete, name='dashboard_service_delete'),
    path('contenu/services/<int:service_id>/toggle/', views.dashboard_service_toggle, name='dashboard_service_toggle'),
    path('contenu/temoignages/', views.dashboard_testimonials, name='dashboard_testimonials'),
    path('contenu/temoignages/ajouter/', views.dashboard_testimonial_save, name='dashboard_testimonial_add'),
    path('contenu/temoignages/<int:testimonial_id>/modifier/', views.dashboard_testimonial_save, name='dashboard_testimonial_edit'),
    path('contenu/temoignages/<int:testimonial_id>/supprimer/', views.dashboard_testimonial_delete, name='dashboard_testimonial_delete'),
    # Media
    path('medias/', views.dashboard_media, name='dashboard_media'),
    path('contenu/regles/', views.dashboard_rules, name='dashboard_rules'),
    path('notre-carte/', views.dashboard_menu_card, name='dashboard_menu_card'),
    path('notre-carte/ajouter/', views.dashboard_menu_card_add, name='dashboard_menu_card_add'),
    path('notre-carte/<int:card_id>/modifier/', views.dashboard_menu_card_edit, name='dashboard_menu_card_edit'),
    path('notre-carte/<int:card_id>/supprimer/', views.dashboard_menu_card_delete, name='dashboard_menu_card_delete'),
    path('notre-carte/<int:card_id>/toggle/', views.dashboard_menu_card_toggle, name='dashboard_menu_card_toggle'),
    path('contenu/faq/', views.dashboard_faq, name='dashboard_faq'),
    path('contenu/faq/ajouter/', views.dashboard_faq_add, name='dashboard_faq_add'),
    path('contenu/faq/<int:faq_id>/modifier/', views.dashboard_faq_edit, name='dashboard_faq_edit'),
    path('contenu/faq/<int:faq_id>/supprimer/', views.dashboard_faq_delete, name='dashboard_faq_delete'),
    path('contenu/faq/<int:faq_id>/toggle/', views.dashboard_faq_toggle, name='dashboard_faq_toggle'),
    path('contenu/faq/<int:faq_id>/star/', views.dashboard_faq_toggle_featured, name='dashboard_faq_toggle_featured'),
    path('reception/', views.dashboard_reception, name='dashboard_reception'),
    path('reception/<int:room_id>/statut/', views.dashboard_room_quick_status, name='dashboard_room_quick_status'),
    path('paiements/', views.dashboard_payments, name='dashboard_payments'),
    # Emails
    path('emails/', views.dashboard_email_settings, name='dashboard_email_settings'),
    path('emails/test/', views.dashboard_email_test, name='dashboard_email_test'),
    path('emails/apercu/<str:email_type>/', views.dashboard_email_preview, name='dashboard_email_preview'),
    # Contact messages
    path('contact/', views.dashboard_contact_messages, name='dashboard_contact_messages'),
    path('contact/<int:msg_id>/statut/', views.dashboard_contact_status, name='dashboard_contact_status'),
    path('contact/<int:msg_id>/supprimer/', views.dashboard_contact_delete, name='dashboard_contact_delete'),
    # Activities & Destinations
    path('contenu/activites/', views.dashboard_activities, name='dashboard_activities'),
    path('contenu/activites/ajouter/', views.dashboard_activity_add, name='dashboard_activity_add'),
    path('contenu/activites/<int:activity_id>/modifier/', views.dashboard_activity_edit, name='dashboard_activity_edit'),
    path('contenu/activites/<int:activity_id>/supprimer/', views.dashboard_activity_delete, name='dashboard_activity_delete'),
    path('contenu/activites/<int:activity_id>/toggle/', views.dashboard_activity_toggle, name='dashboard_activity_toggle'),
]

# Already there — just add reception

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chambres/', views.room_list, name='room_list'),
    path('chambres/<slug:slug>/', views.room_detail, name='room_detail'),
    path('promotions/', views.promotions_page, name='promotions_page'),
    path('regles/', views.hotel_rules_page, name='hotel_rules'),
    path('faq/', views.faq_page, name='faq_page'),
    path('notre-carte/', views.menu_card_page, name='menu_card_page'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('contact/', views.contact_submit, name='contact_submit'),
]

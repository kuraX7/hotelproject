from django.urls import path
from . import views

urlpatterns = [
    path('reservation/<int:booking_id>/', views.payment_initiate,   name='payment_initiate'),
    path('callback/',                     views.payment_callback,    name='payment_callback'),
    path('retour/succes/',                views.payment_success,     name='payment_success'),
    path('retour/echec/',                 views.payment_failure,     name='payment_failure'),
    path('simulation/<str:order_id>/',    views.payment_simulation,  name='payment_simulation'),
    path('succes/<int:booking_id>/',         views.payment_success_with_pdf, name='payment_success_with_pdf'),
]

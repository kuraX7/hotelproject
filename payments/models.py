from django.db import models
from bookings.models import Booking


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending',   'En attente'),
        ('approved',  'Approuvé'),
        ('declined',  'Refusé'),
        ('error',     'Erreur'),
        ('cancelled', 'Annulé'),
        ('refunded',  'Remboursé'),
    ]
    METHOD_CHOICES = [
        ('cmi',        'CMI (Carte bancaire marocaine)'),
        ('visa',       'Visa'),
        ('mastercard', 'Mastercard'),
        ('simulation', 'Test / Simulation'),
    ]

    booking        = models.OneToOneField(Booking, on_delete=models.CASCADE,
                                          related_name='payment', verbose_name="Réservation")
    order_id       = models.CharField(max_length=100, unique=True, verbose_name="Référence commande")
    amount         = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant (MAD)")
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                      default='pending', verbose_name="Statut")
    method         = models.CharField(max_length=20, choices=METHOD_CHOICES,
                                      default='cmi', verbose_name="Méthode")
    # CMI response fields
    transaction_id = models.CharField(max_length=200, blank=True, verbose_name="ID Transaction CMI")
    auth_code      = models.CharField(max_length=50,  blank=True, verbose_name="Code autorisation")
    response_code  = models.CharField(max_length=10,  blank=True, verbose_name="Code réponse CMI")
    response_message = models.TextField(blank=True,   verbose_name="Message réponse")
    card_last4     = models.CharField(max_length=4,   blank=True, verbose_name="4 derniers chiffres carte")
    card_brand     = models.CharField(max_length=20,  blank=True, verbose_name="Type carte")
    # Raw CMI response (JSON)
    raw_response   = models.TextField(blank=True,     verbose_name="Réponse brute CMI")
    # Timestamps
    created_at     = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at     = models.DateTimeField(auto_now=True,     verbose_name="Mis à jour le")
    paid_at        = models.DateTimeField(null=True, blank=True, verbose_name="Payé le")

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.order_id} — {self.get_status_display()} — {self.amount} MAD"

    @property
    def is_paid(self):
        return self.status == 'approved'

    @property
    def status_color(self):
        return {
            'pending':   '#F59E0B',
            'approved':  '#10B981',
            'declined':  '#EF4444',
            'error':     '#EF4444',
            'cancelled': '#6B7280',
            'refunded':  '#8B5CF6',
        }.get(self.status, '#6B7280')

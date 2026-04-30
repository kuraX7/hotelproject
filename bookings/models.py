from django.db import models
from rooms.models import Room
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
        ('completed', 'Terminée'),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', verbose_name="Chambre")
    name = models.CharField(max_length=200, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    check_in = models.DateField(verbose_name="Date d'arrivée")
    check_out = models.DateField(verbose_name="Date de départ")
    guests = models.IntegerField(default=1, verbose_name="Nombre de personnes")
    special_requests = models.TextField(blank=True, verbose_name="Message / Demandes spéciales")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix total (MAD)")
    admin_notes = models.TextField(blank=True, verbose_name="Notes internes admin")
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="Annulée le")
    refund_requested = models.BooleanField(default=False, verbose_name="Remboursement demandé")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mise à jour le")

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} — {self.name} · {self.room.name} ({self.check_in}→{self.check_out})"

    def clean(self):
        if self.check_in and self.check_out:
            if self.check_in >= self.check_out:
                raise ValidationError("La date de départ doit être après la date d'arrivée.")
            if self.check_in < timezone.now().date() and not self.pk:
                raise ValidationError("La date d'arrivée ne peut pas être dans le passé.")
            try:
                room = self.room
            except Exception:
                room = None
            if room:
                # ── INVENTORY CHECK: count ALL bookings for this room type ──
                from rooms.availability import get_availability
                avail = get_availability(room, self.check_in, self.check_out, exclude_booking_id=self.pk)
                if not avail['available']:
                    raise ValidationError(
                        f"Complet — toutes les {avail['rooms_total']} chambres de type "
                        f"«{room.name}» sont réservées pour ces dates."
                    )

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out and self.room:
            nights = (self.check_out - self.check_in).days
            self.total_price = self.room.price * nights
        super().save(*args, **kwargs)

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    @property
    def reference(self):
        return f"AL{self.id:05d}"

    @property
    def can_be_modified(self):
        if self.status in ('cancelled', 'completed'):
            return False
        return self.check_in > timezone.now().date()

    @property
    def can_be_cancelled(self):
        return self.can_be_modified

    @property
    def hours_until_checkin(self):
        checkin_dt = datetime.datetime.combine(self.check_in, datetime.time(14, 0))
        if timezone.is_aware(timezone.now()):
            checkin_dt = timezone.make_aware(checkin_dt)
        delta = checkin_dt - timezone.now()
        return delta.total_seconds() / 3600

    @property
    def free_cancellation_available(self):
        return self.hours_until_checkin > 48

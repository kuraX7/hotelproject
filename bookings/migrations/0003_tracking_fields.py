from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_booking_admin_notes_booking_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Annulée le'),
        ),
        migrations.AddField(
            model_name='booking',
            name='refund_requested',
            field=models.BooleanField(default=False, verbose_name='Remboursement demandé'),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0011_populate_service_slugs'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotelinfo',
            name='google_maps_url',
            field=models.URLField(blank=True, verbose_name='Google Maps URL',
                                  help_text="Lien Google Maps vers la localisation de l'hôtel."),
        ),
    ]

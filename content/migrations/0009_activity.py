from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0008_hotelinfo_years_excellence'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name="Nom de l'activité / lieu")),
                ('description', models.TextField(verbose_name='Description')),
                ('image_url', models.URLField(blank=True, max_length=500, verbose_name='URL image')),
                ('image_file', models.ImageField(blank=True, null=True, upload_to='activities/', verbose_name='Upload image')),
                ('is_active', models.BooleanField(default=True, verbose_name='Afficher sur le site')),
                ('order', models.IntegerField(default=0, verbose_name="Ordre d'affichage")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Activité / Destination',
                'verbose_name_plural': 'Activités & Destinations',
                'ordering': ['order', 'created_at'],
            },
        ),
    ]

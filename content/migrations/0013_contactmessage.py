from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_hotelinfo_google_maps_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name',       models.CharField(max_length=200, verbose_name='Nom complet')),
                ('email',      models.EmailField(verbose_name='Email')),
                ('phone',      models.CharField(blank=True, max_length=30, verbose_name='Téléphone')),
                ('subject',    models.CharField(max_length=300, verbose_name='Sujet')),
                ('message',    models.TextField(verbose_name='Message')),
                ('status',     models.CharField(
                    choices=[('new','Nouveau'),('read','Lu'),('replied','Répondu'),('archived','Archivé')],
                    default='new', max_length=20, verbose_name='Statut')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='Adresse IP')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Reçu le')),
            ],
            options={
                'verbose_name': 'Message de contact',
                'verbose_name_plural': 'Messages de contact',
                'ordering': ['-created_at'],
            },
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0004_room_bed_config_room_free_cancellation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='category',
            field=models.CharField(
                choices=[
                    ('jardin',    'Vue sur jardin'),
                    ('piscine',   'Vue sur piscine'),
                    ('familiale', 'Familiale'),
                    ('suite',     'Suite'),
                ],
                default='jardin',
                max_length=20,
                verbose_name='Catégorie',
            ),
        ),
    ]

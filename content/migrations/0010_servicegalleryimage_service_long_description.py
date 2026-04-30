from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0009_activity'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='long_description',
            field=models.TextField(blank=True, verbose_name='Description longue (page dédiée)', help_text='Texte détaillé affiché sur la page du service.'),
        ),
        migrations.AddField(
            model_name='service',
            name='slug',
            field=models.SlugField(blank=True, max_length=200, verbose_name='Slug URL', help_text='Laissez vide pour auto-générer depuis le nom.'),
        ),
        migrations.CreateModel(
            name='ServiceGalleryImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(blank=True, max_length=200, verbose_name='Légende')),
                ('image_url', models.URLField(blank=True, max_length=500, verbose_name='URL image')),
                ('image_file', models.ImageField(blank=True, null=True, upload_to='services/gallery/', verbose_name='Upload image')),
                ('order', models.IntegerField(default=0, verbose_name="Ordre d'affichage")),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery_images', to='content.service', verbose_name='Service')),
            ],
            options={
                'verbose_name': 'Image galerie service',
                'verbose_name_plural': 'Images galerie services',
                'ordering': ['order'],
            },
        ),
    ]

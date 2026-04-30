from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Service = apps.get_model('content', 'Service')
    for service in Service.objects.all():
        if not service.slug:
            base_slug = slugify(service.name)
            slug = base_slug
            n = 1
            while Service.objects.filter(slug=slug).exclude(pk=service.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            service.slug = slug
            service.save()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_servicegalleryimage_service_long_description'),
    ]

    operations = [
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
    ]

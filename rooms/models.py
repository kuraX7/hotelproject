from django.db import models

class Room(models.Model):
    CATEGORY_CHOICES = [
        ('jardin',    'Vue sur jardin'),
        ('piscine',   'Vue sur piscine'),
        ('familiale', 'Familiale'),
        ('suite',     'Suite'),
    ]
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('occupied', 'Occupée'),
        ('maintenance', 'En maintenance'),
    ]
    name = models.CharField(max_length=200, verbose_name="Nom de la chambre")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix par nuit (MAD)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='jardin', verbose_name="Catégorie")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Statut")
    capacity = models.IntegerField(default=2, verbose_name="Capacité (personnes)")
    size = models.IntegerField(default=25, verbose_name="Superficie (m²)")
    image = models.ImageField(upload_to='rooms/', blank=True, null=True, verbose_name="Image principale (upload)")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    has_wifi = models.BooleanField(default=True, verbose_name="WiFi")
    has_ac = models.BooleanField(default=True, verbose_name="Climatisation")
    has_balcony = models.BooleanField(default=False, verbose_name="Balcon")
    has_sea_view = models.BooleanField(default=False, verbose_name="Vue mer")
    has_tv = models.BooleanField(default=True, verbose_name="TV")
    has_minibar = models.BooleanField(default=False, verbose_name="Mini-bar")
    has_safe = models.BooleanField(default=True, verbose_name="Coffre-fort")
    has_bathtub        = models.BooleanField(default=False, verbose_name="Baignoire")
    has_garden_view    = models.BooleanField(default=False, verbose_name="Vue sur jardin")
    has_pool_view      = models.BooleanField(default=False, verbose_name="Vue sur piscine")
    has_terrace        = models.BooleanField(default=False, verbose_name="Terrasse")
    has_soundproofing  = models.BooleanField(default=False, verbose_name="Insonorisation")
    has_private_bathroom = models.BooleanField(default=True,  verbose_name="Salle de bains privative")
    # Room inventory & pricing
    room_count         = models.IntegerField(default=1,    verbose_name="Nombre de chambres de ce type")
    original_price     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix barré (avant réduction)")
    bed_config         = models.CharField(max_length=300, blank=True, verbose_name="Configuration des lits", help_text="Ex: 1 lit double ou 2 lits simples")
    # Inclusions
    includes_breakfast = models.BooleanField(default=True,  verbose_name="Petit-déjeuner inclus")
    includes_parking   = models.BooleanField(default=True,  verbose_name="Parking inclus")
    free_cancellation  = models.BooleanField(default=True,  verbose_name="Annulation gratuite")
    no_prepayment      = models.BooleanField(default=True,  verbose_name="Aucun prépaiement requis")
    created_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chambre"
        verbose_name_plural = "Chambres"
        ordering = ['price']

    @property
    def bed_options(self):
        """Returns list if multiple options (contains ' ou '), else empty list."""
        if self.bed_config and ' ou ' in self.bed_config and 'réserve' in self.bed_config:
            return [o.strip() for o in self.bed_config.split(' ou ')]
        return []

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        # sync is_available with status
        self.is_available = (self.status == 'available')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('room_detail', kwargs={'slug': self.slug})

    def get_primary_image(self):
        img = self.images.filter(is_primary=True).first()
        if img:
            return img.get_image_src()
        img = self.images.first()
        if img:
            return img.get_image_src()
        if self.image:
            return self.image.url
        return None

    def get_all_images(self):
        return self.images.all()


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images', verbose_name="Chambre")
    image_url = models.URLField(max_length=500, blank=True, verbose_name="URL image externe")
    image_file = models.ImageField(upload_to='rooms/gallery/', blank=True, null=True, verbose_name="Upload image")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Légende")
    is_360 = models.BooleanField(default=False, verbose_name="Image 360°")
    is_primary = models.BooleanField(default=False, verbose_name="Image principale")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Image de chambre"
        verbose_name_plural = "Images de chambre"
        ordering = ['order']

    def __str__(self):
        return f"{self.room.name} — {'360°' if self.is_360 else 'Photo'} #{self.order}"

    def get_image_src(self):
        if self.image_file:
            return self.image_file.url
        return self.image_url or ''

from django.db import models

class HeroSection(models.Model):
    """Contenu de la section hero de la page d'accueil"""
    title_line1 = models.CharField(max_length=200, default="L'Art de", verbose_name="Titre ligne 1")
    title_line2 = models.CharField(max_length=200, default="l'Hospitalité", verbose_name="Titre ligne 2 (grande)")
    title_line3 = models.CharField(max_length=200, default="Marocaine", verbose_name="Titre ligne 3")
    subtitle = models.TextField(default="Découvrez une oasis de raffinement au cœur de Casablanca.", verbose_name="Sous-titre")
    badge_text = models.CharField(max_length=200, default="★★★★★ · Casablanca · Depuis 1985", verbose_name="Badge texte")
    bg_image_url = models.URLField(max_length=500, blank=True, verbose_name="URL image de fond")
    bg_image_file = models.ImageField(upload_to='hero/', blank=True, null=True, verbose_name="Upload image de fond")
    btn_primary_text = models.CharField(max_length=100, default="Découvrir nos Suites", verbose_name="Bouton principal texte")
    btn_secondary_text = models.CharField(max_length=100, default="Réserver", verbose_name="Bouton secondaire texte")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Section Hero"
        verbose_name_plural = "Sections Hero"

    def __str__(self):
        return f"Hero — {self.title_line2}"

    def get_bg_image(self):
        if self.bg_image_file:
            return self.bg_image_file.url
        return self.bg_image_url or 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=1920&q=80'


class HotelInfo(models.Model):
    """Informations générales de l'hôtel"""
    hotel_name = models.CharField(max_length=200, default="Al Andalus", verbose_name="Nom de l'hôtel")
    tagline = models.CharField(max_length=300, default="HOTEL & SPA · CASABLANCA", verbose_name="Slogan")
    about_title = models.CharField(max_length=200, default="Un Héritage d'Excellence au Cœur du Maroc", verbose_name="Titre section À propos")
    about_text1 = models.TextField(verbose_name="Texte à propos paragraphe 1", default="Fondé en 1985 sur les rives de l'Atlantique, l'Hôtel Al Andalus s'est imposé comme le symbole du raffinement marocain.")
    about_text2 = models.TextField(verbose_name="Texte à propos paragraphe 2", blank=True)
    about_image_url = models.URLField(max_length=500, blank=True, verbose_name="URL image à propos principale")
    about_image_file = models.ImageField(upload_to='about/', blank=True, null=True, verbose_name="Upload image à propos")
    founded_year = models.IntegerField(default=1985, verbose_name="Année de fondation")
    address = models.TextField(default="Boulevard de la Corniche, Casablanca 20000", verbose_name="Adresse")
    phone = models.CharField(max_length=50, default="+212 5 22 XX XX XX", verbose_name="Téléphone")
    email = models.EmailField(default="contact@hotel-alandalus.ma", verbose_name="Email")
    checkin_time = models.CharField(max_length=10, default="14h00", verbose_name="Heure check-in")
    checkout_time = models.CharField(max_length=10, default="12h00", verbose_name="Heure check-out")
    stars = models.IntegerField(default=5, verbose_name="Nombre d'étoiles")
    total_rooms = models.IntegerField(default=38, verbose_name="Nombre total de chambres")
    satisfaction_rate = models.IntegerField(default=98, verbose_name="Taux de satisfaction (%)")
    # About accent image (small overlay image)
    about_image_accent_url  = models.URLField(max_length=500, blank=True, verbose_name="Petite image accent (À Propos)")
    about_image_accent_file = models.ImageField(upload_to='hotel/', blank=True, null=True, verbose_name="Upload petite image accent")
    # 4 feature items in About section
    feature_1_icon = models.CharField(max_length=50, default='fas fa-leaf',          verbose_name="Feature 1 — Icône")
    feature_1_text = models.CharField(max_length=100, default='Cuisine marocaine authentique', verbose_name="Feature 1 — Texte")
    feature_2_icon = models.CharField(max_length=50, default='fas fa-spa',           verbose_name="Feature 2 — Icône")
    feature_2_text = models.CharField(max_length=100, default='Spa & Hammam traditionnel',    verbose_name="Feature 2 — Texte")
    feature_3_icon = models.CharField(max_length=50, default='fas fa-swimming-pool', verbose_name="Feature 3 — Icône")
    feature_3_text = models.CharField(max_length=100, default='Piscine Olympic & Terrasse',   verbose_name="Feature 3 — Texte")
    feature_4_icon = models.CharField(max_length=50, default='fas fa-concierge-bell',verbose_name="Feature 4 — Icône")
    feature_4_text = models.CharField(max_length=100, default='Conciergerie 24h/24',          verbose_name="Feature 4 — Texte")
    # Page hero backgrounds (sub-pages)
    hero_rooms_image_url   = models.URLField(max_length=500, blank=True, default='https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=1920&q=80', verbose_name="Image hero — Page Chambres")
    hero_detail_image_url  = models.URLField(max_length=500, blank=True, default='https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=1920&q=80', verbose_name="Image hero — Page Détail Chambre")
    hero_booking_image_url = models.URLField(max_length=500, blank=True, default='https://images.unsplash.com/photo-1496417263034-38ec4f0b665a?w=1920&q=80', verbose_name="Image hero — Page Réservation")
    cta_image_url          = models.URLField(max_length=500, blank=True, default='https://images.unsplash.com/photo-1582719508461-905c673771fd?w=1920&q=80',  verbose_name="Image CTA (section accueil)")
    years_excellence = models.IntegerField(null=True, blank=True,
        verbose_name="Ans d'excellence (optionnel)",
        help_text="Laissez vide pour calculer automatiquement depuis l'année de fondation")
    facebook_url = models.URLField(blank=True, verbose_name="Facebook URL")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram URL")
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp")
    google_maps_url = models.URLField(blank=True, verbose_name="Google Maps URL",
                                      help_text="Lien Google Maps vers la localisation de l'hôtel. Ex: https://maps.google.com/?q=...")

    class Meta:
        verbose_name = "Informations Hôtel"
        verbose_name_plural = "Informations Hôtel"

    def __str__(self):
        return self.hotel_name

    def get_about_image(self):
        if self.about_image_file:
            return self.about_image_file.url
        return self.about_image_url or 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&q=80'

    def get_about_accent_image(self):
        if self.about_image_accent_file:
            return self.about_image_accent_file.url

    class Meta:
        verbose_name = "Informations Hôtel"
        verbose_name_plural = "Informations Hôtel"

    def __str__(self):
        return self.hotel_name

    def get_about_image(self):
        if self.about_image_file:
            return self.about_image_file.url
        return self.about_image_url or 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&q=80'

    def get_about_accent_image(self):
        if self.about_image_accent_file:
            return self.about_image_accent_file.url
        return self.about_image_accent_url or 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=300&q=80'


class Service(models.Model):
    """Services proposés par l'hôtel"""
    name = models.CharField(max_length=200, verbose_name="Nom du service")
    slug = models.SlugField(max_length=200, blank=True, unique=True, verbose_name="Slug URL",
                            help_text="Laissez vide pour auto-générer depuis le nom.")
    description = models.TextField(verbose_name="Description courte (accueil)")
    long_description = models.TextField(blank=True, verbose_name="Description longue (page dédiée)",
                                        help_text="Texte détaillé affiché sur la page du service.")
    icon_class = models.CharField(max_length=100, default="fas fa-concierge-bell", verbose_name="Classe icône FontAwesome",
                                  help_text="Ex: fas fa-spa, fas fa-utensils, fas fa-swimming-pool")
    image_url = models.URLField(max_length=500, blank=True, verbose_name="URL image")
    image_file = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name="Upload image")
    is_featured = models.BooleanField(default=True, verbose_name="Afficher sur l'accueil")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1
            while Service.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_image(self):
        if self.image_file:
            return self.image_file.url
        return self.image_url or None

    def get_detail_url(self):
        from django.urls import reverse
        if self.slug:
            return reverse('service_detail', kwargs={'slug': self.slug})
        return None


class ServiceGalleryImage(models.Model):
    """Images de la galerie d'un service"""
    service    = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='gallery_images',
                                   verbose_name="Service")
    caption    = models.CharField(max_length=200, blank=True, verbose_name="Légende")
    image_url  = models.URLField(max_length=500, blank=True, verbose_name="URL image")
    image_file = models.ImageField(upload_to='services/gallery/', blank=True, null=True,
                                   verbose_name="Upload image")
    order      = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Image galerie service"
        verbose_name_plural = "Images galerie services"
        ordering = ['order']

    def __str__(self):
        return f"{self.service.name} — image {self.order}"

    def get_image(self):
        if self.image_file:
            return self.image_file.url
        return self.image_url or ''


class Testimonial(models.Model):
    """Témoignages clients"""
    name = models.CharField(max_length=200, verbose_name="Nom du client")
    origin = models.CharField(max_length=200, verbose_name="Ville / Pays", default="France")
    text = models.TextField(verbose_name="Témoignage")
    rating = models.IntegerField(default=5, verbose_name="Note /5")
    is_featured = models.BooleanField(default=True, verbose_name="Afficher sur l'accueil")
    order = models.IntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Témoignage"
        verbose_name_plural = "Témoignages"
        ordering = ['order']

    def __str__(self):
        return f"{self.name} — {self.rating}★"

    @property
    def initials(self):
        parts = self.name.split()
        return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()

    @property
    def stars_display(self):
        return '★' * self.rating


class Promotion(models.Model):
    BADGE_CHOICES = [
        ('flash',     'Flash Sale'),
        ('limited',   'Offre Limitée'),
        ('exclusive', 'Exclusif'),
        ('seasonal',  'Saisonnier'),
        ('lastminute','Dernière Minute'),
        ('honeymoon', 'Lune de Miel'),
        ('business',  'Business'),
    ]
    title        = models.CharField(max_length=200, verbose_name="Titre de la promotion")
    subtitle     = models.CharField(max_length=300, blank=True, verbose_name="Sous-titre")
    description  = models.TextField(verbose_name="Description")
    badge        = models.CharField(max_length=20, choices=BADGE_CHOICES, default='limited', verbose_name="Badge")
    discount_pct = models.IntegerField(default=0, verbose_name="Réduction (%)", help_text="0 = pas de %, laissez vide")
    discount_label = models.CharField(max_length=100, blank=True, verbose_name="Label réduction", help_text="Ex: '-20%', 'Petit-déj offert', '3ème nuit gratuite'")
    image_url    = models.URLField(max_length=500, blank=True, verbose_name="URL image")
    image_file   = models.ImageField(upload_to='promotions/', blank=True, null=True, verbose_name="Upload image")
    room         = models.ForeignKey('rooms.Room', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='promotions', verbose_name="Chambre liée (optionnel)")
    cta_text     = models.CharField(max_length=100, default="En profiter", verbose_name="Texte bouton")
    valid_from   = models.DateField(null=True, blank=True, verbose_name="Valable du")
    valid_until  = models.DateField(null=True, blank=True, verbose_name="Valable jusqu'au")
    is_active    = models.BooleanField(default=True, verbose_name="Active")
    is_featured  = models.BooleanField(default=True, verbose_name="Afficher sur l'accueil")
    order        = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def get_image(self):
        if self.image_file:
            return self.image_file.url
        return self.image_url or ''

    @property
    def is_valid_now(self):
        from django.utils import timezone
        today = timezone.now().date()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        return self.is_active

    @property
    def days_remaining(self):
        if not self.valid_until:
            return None
        from django.utils import timezone
        delta = self.valid_until - timezone.now().date()
        return max(0, delta.days)

    def get_badge_display_color(self):
        colors = {
            'flash':      ('#FF4444', '#fff'),
            'limited':    ('#C9A96E', '#fff'),
            'exclusive':  ('#1A1A1A', '#C9A96E'),
            'seasonal':   ('#10B981', '#fff'),
            'lastminute': ('#F97316', '#fff'),
            'honeymoon':  ('#EC4899', '#fff'),
            'business':   ('#3B82F6', '#fff'),
        }
        return colors.get(self.badge, ('#C9A96E', '#fff'))


class HotelRules(models.Model):
    """Règles de la maison — modifiable depuis le dashboard."""

    # ── Horaires ──────────────────────────────────────
    checkin_from   = models.TimeField(default='14:00', verbose_name="Check-in à partir de")
    checkin_until  = models.TimeField(default='23:00', verbose_name="Check-in jusqu'à")
    checkout_from  = models.TimeField(default='06:00', verbose_name="Check-out à partir de")
    checkout_until = models.TimeField(default='12:00', verbose_name="Check-out jusqu'à")

    # ── Annulation / Prépaiement ──────────────────────
    cancellation_policy = models.TextField(
        verbose_name="Politique d'annulation",
        default="Annulation gratuite jusqu'à 48 heures avant l'arrivée. "
                "Au-delà, la première nuit sera facturée.",
    )
    prepayment_policy = models.TextField(
        verbose_name="Politique de prépaiement",
        default="Un acompte de 30% sera prélevé à la réservation. "
                "Le solde est réglé à l'arrivée.",
        blank=True,
    )

    # ── Enfants ───────────────────────────────────────
    children_allowed      = models.BooleanField(default=True,  verbose_name="Enfants acceptés")
    children_policy       = models.TextField(
        verbose_name="Conditions enfants",
        default="Tous les enfants sont les bienvenus. "
                "Les enfants de moins de 7 ans séjournent gratuitement. "
                "Les enfants de plus de 7 ans sont facturés au tarif adulte.",
        blank=True,
    )
    baby_cot_available    = models.BooleanField(default=True,  verbose_name="Lit bébé disponible")
    baby_cot_price        = models.CharField(max_length=50, default="Gratuit", verbose_name="Prix lit bébé", blank=True)
    baby_cot_age_range    = models.CharField(max_length=20, default="0 – 3 ans", verbose_name="Tranche d'âge lit bébé", blank=True)
    extra_bed_available   = models.BooleanField(default=False, verbose_name="Lit d'appoint disponible")
    extra_bed_price       = models.CharField(max_length=50, blank=True, verbose_name="Prix lit d'appoint")

    # ── Âge minimum ──────────────────────────────────
    age_restriction       = models.BooleanField(default=False, verbose_name="Restriction d'âge à l'enregistrement")
    age_minimum           = models.IntegerField(default=18,    verbose_name="Âge minimum requis", null=True, blank=True)
    age_restriction_notes = models.TextField(blank=True, verbose_name="Notes restriction d'âge",
        default="Aucune restriction relative à l'âge ne s'applique pour l'enregistrement.")

    # ── Animaux ───────────────────────────────────────
    pets_allowed  = models.BooleanField(default=False, verbose_name="Animaux domestiques acceptés")
    pets_policy   = models.TextField(
        verbose_name="Politique animaux",
        default="Les animaux de compagnie ne sont pas admis au sein de l'établissement.",
        blank=True,
    )

    # ── Groupes ───────────────────────────────────────
    groups_policy = models.TextField(
        verbose_name="Politique groupes",
        default="Toute réservation de plus de 10 chambres peut entraîner "
                "des conditions particulières et des frais supplémentaires. "
                "Contactez-nous pour un devis personnalisé.",
        blank=True,
    )

    # ── Fumeurs ───────────────────────────────────────
    smoking_allowed = models.BooleanField(default=False, verbose_name="Fumeurs autorisés")
    smoking_notes   = models.TextField(blank=True, verbose_name="Notes fumeurs",
        default="Il est strictement interdit de fumer dans toutes les chambres et espaces communs. "
                "Des espaces fumeurs sont disponibles à l'extérieur.")

    # ── Fêtes / Événements ────────────────────────────
    parties_allowed = models.BooleanField(default=False, verbose_name="Fêtes/événements autorisés")
    parties_notes   = models.TextField(blank=True, verbose_name="Notes fêtes/événements",
        default="Les fêtes et événements ne sont pas autorisés dans les chambres.")

    # ── Moyens de paiement ────────────────────────────
    accepts_visa        = models.BooleanField(default=True,  verbose_name="Visa")
    accepts_mastercard  = models.BooleanField(default=True,  verbose_name="Mastercard")
    accepts_amex        = models.BooleanField(default=False, verbose_name="American Express")
    accepts_cash        = models.BooleanField(default=True,  verbose_name="Espèces")
    accepts_cmi         = models.BooleanField(default=True,  verbose_name="CMI (cartes marocaines)")
    accepts_bank_transfer = models.BooleanField(default=False, verbose_name="Virement bancaire")

    # ── Divers ────────────────────────────────────────
    additional_rules = models.TextField(blank=True, verbose_name="Règles supplémentaires")

    class Meta:
        verbose_name = "Règles de la maison"
        verbose_name_plural = "Règles de la maison"

    def __str__(self):
        return "Règles de la maison"

    @classmethod
    def get_instance(cls):
        """Always returns the single instance, creating it if needed."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('general',    'Général'),
        ('checkin',    'Arrivée & Départ'),
        ('rooms',      'Chambres & Hébergement'),
        ('services',   'Services & Activités'),
        ('restaurant', 'Restaurant & Petit-déjeuner'),
        ('pricing',    'Tarifs & Paiement'),
        ('location',   'Localisation'),
        ('family',     'Familles'),
        ('policies',   'Politiques'),
    ]

    question    = models.CharField(max_length=500, verbose_name="Question")
    answer      = models.TextField(verbose_name="Réponse")
    # answer_items: JSON-like list stored as text, one item per line starting with "- "
    answer_items= models.TextField(
        blank=True,
        verbose_name="Liste à puces (une entrée par ligne)",
        help_text="Optionnel : une entrée par ligne. Ex:\n- Continental\n- Buffet"
    )
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES,
                                   default='general', verbose_name="Catégorie")
    is_active   = models.BooleanField(default=True, verbose_name="Afficher sur le site")
    is_featured = models.BooleanField(default=True, verbose_name="Afficher sur l'accueil")
    order       = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.question[:80]

    def get_answer_items_list(self):
        """Returns answer_items as a Python list."""
        if not self.answer_items:
            return []
        lines = [l.strip() for l in self.answer_items.splitlines()]
        items = []
        for line in lines:
            if line.startswith('- '):
                items.append(line[2:])
            elif line.startswith('* '):
                items.append(line[2:])
            elif line:
                items.append(line)
        return items


class MenuCard(models.Model):
    title      = models.CharField(max_length=200, verbose_name="Titre", default="Notre Carte")
    description= models.CharField(max_length=300, blank=True, verbose_name="Description courte")
    image_url  = models.URLField(max_length=500, blank=True, verbose_name="URL image")
    image_file = models.ImageField(upload_to='menu/', blank=True, null=True, verbose_name="Upload image")
    order      = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active  = models.BooleanField(default=True, verbose_name="Afficher sur le site")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Carte du restaurant"
        verbose_name_plural = "Cartes du restaurant"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title

    def get_image(self):
        if self.image_file:
            return self.image_file.url
        return self.image_url or ''


class Activity(models.Model):
    """Activités et destinations autour de l'hôtel"""
    name = models.CharField(max_length=200, verbose_name="Nom de l'activité / lieu")
    description = models.TextField(verbose_name="Description")
    image_url = models.URLField(max_length=500, blank=True, verbose_name="URL image")
    image_file = models.ImageField(upload_to='activities/', blank=True, null=True, verbose_name="Upload image")
    is_active = models.BooleanField(default=True, verbose_name="Afficher sur le site")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activité / Destination"
        verbose_name_plural = "Activités & Destinations"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.name

    def get_image(self):
        if self.image_file:
            return self.image_file.url
        return self.image_url or ''


class ContactMessage(models.Model):
    """Messages envoyés via le formulaire de contact du site"""
    STATUS_CHOICES = [
        ('new',      'Nouveau'),
        ('read',     'Lu'),
        ('replied',  'Répondu'),
        ('archived', 'Archivé'),
    ]
    name       = models.CharField(max_length=200, verbose_name="Nom complet")
    email      = models.EmailField(verbose_name="Email")
    phone      = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    subject    = models.CharField(max_length=300, verbose_name="Sujet")
    message    = models.TextField(verbose_name="Message")
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Statut")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Reçu le")

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject} ({self.created_at.strftime('%d/%m/%Y')})"

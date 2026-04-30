# 🏨 Hôtel Al Andalus — Site Web Complet Django

> Site web hôtelier 5 étoiles avec système de réservation, galerie 360°, et dashboard admin.

## 🚀 Démarrage Rapide

```bash
# 1. Cloner / télécharger le projet
cd hotel_project

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Créer un superuser admin
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

Accéder au site : http://127.0.0.1:8000
Admin Django  : http://127.0.0.1:8000/admin

**Identifiants admin par défaut :** `admin` / `admin1234`

---

## 📁 Structure du Projet

```
hotel_project/
├── hotel_project/          # Config principale
│   ├── settings.py         # Paramètres (BDD, static, sécurité)
│   ├── urls.py             # URLs racine
│   └── wsgi.py             # Point d'entrée WSGI
│
├── rooms/                  # App gestion des chambres
│   ├── models.py           # Room + RoomImage
│   ├── views.py            # home, room_list, room_detail
│   ├── admin.py            # Interface admin chambres
│   └── urls.py             # /chambres/
│
├── bookings/               # App réservations
│   ├── models.py           # Booking avec validation
│   ├── views.py            # book_room, confirmation, check_availability
│   ├── forms.py            # BookingForm avec validation
│   ├── admin.py            # Interface admin réservations
│   └── urls.py             # /reservations/
│
├── templates/              # Templates HTML
│   ├── base.html           # Template de base (navbar + footer)
│   ├── home.html           # Page d'accueil
│   ├── rooms/
│   │   ├── room_list.html  # Liste des chambres
│   │   └── room_detail.html # Détail + galerie 360°
│   └── bookings/
│       ├── book_room.html  # Formulaire réservation
│       └── confirmation.html # Page confirmation
│
├── static/
│   ├── css/main.css        # Styles premium complets
│   └── js/main.js          # JavaScript interactions
│
├── requirements.txt        # Dépendances Python
├── render.yaml             # Config déploiement Render
└── manage.py
```

---

## 🌐 Pages & URLs

| URL | Vue | Description |
|-----|-----|-------------|
| `/` | `home` | Accueil avec hero, rooms en vedette, stats |
| `/chambres/` | `room_list` | Grille de toutes les chambres + filtres |
| `/chambres/<slug>/` | `room_detail` | Détail + galerie + visite 360° + widget réservation |
| `/reservations/chambre/<id>/` | `book_room` | Formulaire de réservation |
| `/reservations/confirmation/<id>/` | `booking_confirmation` | Confirmation |
| `/reservations/disponibilite/<id>/` | `check_availability` | API JSON vérification dispo |
| `/admin/` | Django Admin | Dashboard complet |

---

## 🧩 Modèles

### Room
```python
name, slug, description, price, category
capacity, size, image
is_available, has_wifi, has_ac, has_balcony, has_sea_view
```

### RoomImage
```python
room (FK), image_url (URL externe), image_file (upload)
caption, is_360, is_primary, order
```

### Booking
```python
room (FK), name, email, phone
check_in, check_out, guests, special_requests
status, total_price, created_at
```

---

## ⚙️ Admin Django

Accès : `/admin/` — Fonctionnalités :
- **Chambres** : Ajouter/modifier/supprimer, changer prix en ligne, toggle disponibilité
- **Images** : Inline dans la fiche chambre, support URL externe + upload fichier, flag 360°
- **Réservations** : Vue tableau avec filtre par date/statut, changer statut en ligne

---

## 📸 Galerie 360°

Utilise **Photo Sphere Viewer v5** (CDN).

Pour ajouter une image 360° :
1. Admin → Chambres → choisir une chambre
2. Ajouter une image avec `is_360 = True`
3. Mettre l'URL d'une image équirectangulaire dans `image_url`

Sources d'images 360° gratuites : [polyhaven.com](https://polyhaven.com), [flickr 360](https://flickr.com/groups/equirectangular/)

---

## 🔒 Sécurité

- ✅ Protection CSRF sur tous les formulaires
- ✅ Validation côté serveur (dates, conflits de réservations)
- ✅ Validation côté client (JS + HTML5)
- ✅ `clean()` sur le modèle Booking
- ✅ WhiteNoise pour les fichiers statiques
- ✅ Headers de sécurité en production (DEBUG=False)

---

## 🚀 Déploiement sur Render (Gratuit)

### Étape 1 — Préparer GitHub
```bash
git init
git add .
git commit -m "Initial commit — Hôtel Al Andalus"
git remote add origin https://github.com/VOTRE_USER/hotel-al-andalus.git
git push -u origin main
```

### Étape 2 — Créer le service sur Render
1. Aller sur [render.com](https://render.com) → **New → Web Service**
2. Connecter votre repo GitHub
3. Configurer :
   - **Build Command** : `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command** : `gunicorn hotel_project.wsgi:application`
   - **Python Version** : `3.11`

### Étape 3 — Variables d'environnement sur Render
Dans l'onglet **Environment** de Render, ajouter :

| Clé | Valeur |
|-----|--------|
| `SECRET_KEY` | (générer une clé aléatoire longue) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `votre-app.onrender.com` |

### Étape 4 — Créer l'admin en production
Dans la console Render (Shell) :
```bash
python manage.py createsuperuser
```

### Générer une SECRET_KEY sécurisée :
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🎨 Personnalisation

### Changer le nom de l'hôtel
Chercher `Al Andalus` dans tous les fichiers et remplacer.

### Changer les couleurs
Dans `static/css/main.css`, modifier les variables CSS :
```css
:root {
    --gold: #C9A96E;       /* Couleur principale dorée */
    --gold-dark: #A8854A;  /* Variante foncée */
    --dark: #1A1A1A;       /* Fond sombre */
}
```

### Changer l'image hero
Dans `static/css/main.css`, modifier :
```css
.hero-bg::before {
    background-image: url('VOTRE_URL_IMAGE');
}
```

---

## 📧 Ajouter l'envoi d'email de confirmation (Bonus)

Dans `bookings/views.py`, après `booking.save()` :
```python
from django.core.mail import send_mail
send_mail(
    subject=f'Confirmation réservation #{booking.id} — Hôtel Al Andalus',
    message=f'Bonjour {booking.name}, votre réservation est confirmée...',
    from_email='noreply@hotel-al-andalus.ma',
    recipient_list=[booking.email],
)
```

Dans `settings.py` (avec Gmail) :
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```

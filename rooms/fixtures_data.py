"""Script to populate sample data"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_project.settings')
django.setup()

from rooms.models import Room, RoomImage

rooms_data = [
    {
        'name': 'Chambre Supérieure Atlantique',
        'slug': 'chambre-superieure-atlantique',
        'category': 'standard',
        'description': 'Nichée au cœur de notre établissement, cette chambre supérieure offre un havre de paix avec vue sur les jardins andalous. Décorée avec soin par nos artisans locaux, elle marie zelliges traditionnels et confort contemporain. Parfaite pour les voyageurs en quête d\'authenticité marocaine dans un cadre raffiné.',
        'price': 1200,
        'capacity': 2,
        'size': 32,
        'is_available': True,
        'has_wifi': True,
        'has_ac': True,
        'has_balcony': False,
        'has_sea_view': False,
    },
    {
        'name': 'Suite Deluxe Corniche',
        'slug': 'suite-deluxe-corniche',
        'category': 'deluxe',
        'description': 'Surplombant la majestueuse Corniche de Casablanca, cette suite deluxe vous offre un panorama époustouflant sur l\'Océan Atlantique. Son grand salon séparé, sa salle de bain en marbre et ses finitions haut de gamme en font le choix idéal pour un séjour d\'exception. Le balcon privé vous invite à contempler le coucher de soleil sur l\'Atlantique.',
        'price': 2200,
        'capacity': 2,
        'size': 55,
        'is_available': True,
        'has_wifi': True,
        'has_ac': True,
        'has_balcony': True,
        'has_sea_view': True,
    },
    {
        'name': 'Suite Royale Al Andalus',
        'slug': 'suite-royale-al-andalus',
        'category': 'suite',
        'description': 'Le summum du luxe marocain. Cette suite royale est une véritable œuvre d\'art vivante, habillée de stuc ciselé à la main, de boiseries en cèdre de l\'Atlas et de soieries importées d\'Andalousie. Deux chambres spacieuses, un salon de réception, une salle à manger privée et un hammam personnel composent cet appartement d\'exception. Réservé à ceux qui ne font aucun compromis sur l\'excellence.',
        'price': 4500,
        'capacity': 4,
        'size': 120,
        'is_available': True,
        'has_wifi': True,
        'has_ac': True,
        'has_balcony': True,
        'has_sea_view': True,
    },
    {
        'name': 'Suite Prestige Panoramique',
        'slug': 'suite-prestige-panoramique',
        'category': 'prestige',
        'description': 'Au dernier étage de notre palais, la Suite Prestige offre une expérience unique au Maroc. Avec ses 180m² de pure élégance, sa piscine privée sur la terrasse et sa vue à 270° sur l\'Atlantique, Casablanca et l\'horizon, elle représente l\'apogée de notre art de recevoir. Un majordome personnel, un chef cuisinier à la demande et un service de limousine complètent cette offre incomparable.',
        'price': 8500,
        'capacity': 6,
        'size': 180,
        'is_available': True,
        'has_wifi': True,
        'has_ac': True,
        'has_balcony': True,
        'has_sea_view': True,
    },
]

image_urls = {
    'chambre-superieure-atlantique': [
        ('https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=900&q=80', 'Chambre principale', False, True),
        ('https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?w=900&q=80', 'Salle de bain', False, False),
        ('https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=900&q=80', 'Salon', False, False),
    ],
    'suite-deluxe-corniche': [
        ('https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=900&q=80', 'Vue principale', False, True),
        ('https://images.unsplash.com/photo-1549638441-b787d2e11f14?w=900&q=80', 'Salle de bain deluxe', False, False),
        ('https://images.unsplash.com/photo-1582719508461-905c673771fd?w=900&q=80', 'Vue mer depuis le balcon', False, False),
    ],
    'suite-royale-al-andalus': [
        ('https://images.unsplash.com/photo-1566073771259-6a8506099945?w=900&q=80', 'Suite royale', False, True),
        ('https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=900&q=80', 'Salon privé', False, False),
        ('https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=900&q=80', 'Hammam privatif', False, False),
    ],
    'suite-prestige-panoramique': [
        ('https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=900&q=80', 'Vue panoramique', False, True),
        ('https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=900&q=80', 'Piscine privée', False, False),
        ('https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=900&q=80', 'Terrasse prestige', False, False),
    ],
}

created = 0
for data in rooms_data:
    slug = data['slug']
    room, created_flag = Room.objects.get_or_create(slug=slug, defaults=data)
    if created_flag:
        created += 1
        print(f"✓ Créé: {room.name}")
        # Add images
        for i, (url, caption, is_360, is_primary) in enumerate(image_urls.get(slug, [])):
            RoomImage.objects.create(
                room=room,
                image_url=url,
                caption=caption,
                is_360=is_360,
                is_primary=is_primary,
                order=i,
            )
    else:
        print(f"→ Existe déjà: {room.name}")

print(f"\n✅ {created} chambre(s) créée(s)")

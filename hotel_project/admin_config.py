from django.contrib.admin import AdminSite

class HotelAdminSite(AdminSite):
    site_header = "🏨 Hôtel Al Andalus — Administration"
    site_title = "Al Andalus Admin"
    index_title = "Tableau de bord"

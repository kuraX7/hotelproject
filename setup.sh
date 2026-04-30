#!/bin/bash
echo "🏨 Installation Hôtel Al Andalus..."
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python -c "
import django, os, sys
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'hotel_project.settings'
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@hotel.ma', 'admin1234')
    print('✅ Admin créé: admin / admin1234')
"
echo "✅ Installation terminée!"
echo "👉 Lancer avec: python manage.py runserver"
echo "👉 Admin: http://127.0.0.1:8000/admin (admin / admin1234)"

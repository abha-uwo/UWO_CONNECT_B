import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User

u = User.objects.get(email='abha@uwo24.com')
print(f"User Email: {u.email}")
print(f"Client ID: {u.client.id if u.client else 'None'}")
print(f"Client Name: {u.client.business_name if u.client else 'None'}")

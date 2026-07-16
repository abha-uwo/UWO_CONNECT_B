import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User, Client

print("\n=== USERS IN DATABASE ===")
for u in User.objects.all():
    print(f"Email: {u.email} | Role: {u.role} | ID: {u.id}")

print("\n=== CLIENT BUSINESSES IN DATABASE ===")
for c in Client.objects.all():
    print(f"Business Name: {c.business_name} | ID: {c.id}")

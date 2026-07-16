import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User, Client

# Find abha
abha = User.objects.filter(email='abha@uwo24.com').first()
if abha:
    abha.role = 'CLIENT'
    
    # Create a client record if not exists
    if not abha.client:
        client_obj, _ = Client.objects.get_or_create(business_name="Abha's Business")
        abha.client = client_obj
        
    abha.save()
    print("Successfully updated abha@uwo24.com to CLIENT role!")
else:
    print("User abha@uwo24.com not found!")

print('\n--- ADMINS ---')
for x in User.objects.filter(role='ADMIN'):
    print(f'- {x.email} (Status: {x.status})')

print('\n--- CLIENTS ---')
for x in User.objects.filter(role='CLIENT'):
    client_name = x.client.business_name if getattr(x, 'client', None) else 'None'
    print(f'- {x.email} (Status: {x.status}, Business: {client_name})')

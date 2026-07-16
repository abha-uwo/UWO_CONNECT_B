import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User, Client

u, created = User.objects.get_or_create(
    email='admin@uwo24.com', 
    defaults={
        'username': 'admin@uwo24.com', 
        'role': 'ADMIN', 
        'status': 'APPROVED'
    }
)
u.set_password('admin123')
u.role = 'ADMIN'
u.status = 'APPROVED'
u.save()

print('\n--- ADMIN CREATED ---')
print('Email: admin@uwo24.com | Password: admin123\n')

print('--- ADMINS ---')
for x in User.objects.filter(role='ADMIN'):
    print(f'- {x.email} (Status: {x.status})')

print('\n--- CLIENTS ---')
for x in User.objects.filter(role='CLIENT'):
    client_name = x.client.business_name if getattr(x, 'client', None) else 'None'
    print(f'- {x.email} (Status: {x.status}, Business: {client_name})')

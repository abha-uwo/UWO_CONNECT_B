import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User, Client

print('\n--- ALL BUSINESS IDs ---')
for c in Client.objects.all():
    print(f"{c.business_name}: {c.id}")

# Link abha to uwo
abha = User.objects.filter(email='abha@uwo24.com').first()
uwo_client = Client.objects.filter(business_name='uwo').first()

if abha and uwo_client:
    abha.client = uwo_client
    abha.save()
    print(f"\nSUCCESS: abha@uwo24.com is now linked to business '{uwo_client.business_name}'!")
else:
    print("\nERROR: Could not find user or client to link.")

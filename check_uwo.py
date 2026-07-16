import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Client

c = Client.objects.get(business_name='uwo')
print(f"Business: {c.business_name}")
print(f"Phone: {getattr(c, 'phone', getattr(c, 'phone_number', 'None'))}")
print(f"WABA ID: {c.whatsapp_waba_id}")
print(f"Phone ID: {c.whatsapp_phone_number_id}")
token_len = len(c.whatsapp_access_token) if c.whatsapp_access_token else 0
print(f"Token length: {token_len}")

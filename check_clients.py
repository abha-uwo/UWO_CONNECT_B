import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import Client; clients = Client.objects.filter(whatsapp_phone_number_id='1125247290680369'); 
for c in clients:
    print(c.business_name, c.user.email if hasattr(c, 'user') else 'no user', c.automation_enabled)

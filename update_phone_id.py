import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import Client; 
for c in Client.objects.all():
    c.whatsapp_phone_number_id = '1125247290680369'
    c.save()
print('Phone Number ID updated for all clients!')

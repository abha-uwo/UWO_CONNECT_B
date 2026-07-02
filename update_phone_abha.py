import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import Client, User; 
for c in Client.objects.all():
    c.whatsapp_phone_number_id = ''
    c.save()
try:
    user = User.objects.get(email='abha@uwo24.com')
    if user.client:
        user.client.whatsapp_phone_number_id = '1125247290680369'
        user.client.save()
        print('Updated successfully for abha@uwo24.com')
    else:
        print('User abha@uwo24.com does not have a client associated.')
except Exception as e:
    print(f'Error: {e}')

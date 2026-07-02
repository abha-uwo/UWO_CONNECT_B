import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import User; 
try:
    user = User.objects.get(email='abha@uwo24.com')
    if user.client:
        user.client.whatsapp_waba_id = '767962373041368'
        user.client.save()
        print('WABA updated successfully for abha@uwo24.com')
    else:
        print('User abha@uwo24.com does not have a client associated.')
except Exception as e:
    print(f'Error: {e}')

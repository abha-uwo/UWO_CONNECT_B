import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import User; 
try:
    user = User.objects.get(email='abha@uwo24.com')
    if user.client:
        user.client.phone_number = '+1(555)651-6125'
        user.client.save()
        print('Phone number updated successfully for abha@uwo24.com')
    else:
        print('User abha@uwo24.com does not have a client associated.')
except Exception as e:
    print(f'Error: {e}')

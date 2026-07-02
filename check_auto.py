import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import User; 
try:
    user = User.objects.get(email='abha@uwo24.com')
    print(f'Automation Enabled: {user.client.automation_enabled}')
except Exception as e:
    print(f'Error: {e}')

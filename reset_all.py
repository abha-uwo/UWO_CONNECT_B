import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import User; 
for u in User.objects.all():
    u.set_password('admin123')
    u.is_active = True
    u.save()
print('All passwords reset to admin123')

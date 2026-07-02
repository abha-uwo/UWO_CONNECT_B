import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import Message; msgs = Message.objects.all().order_by('-created_at')[:3]; 
for m in msgs:
    print(f'Msg: {m.body}, To Contact: {m.contact.phone_number if m.contact else None}')

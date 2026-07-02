import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import Message; msgs = Message.objects.all().order_by('-created_at')[:5]; 
for m in msgs:
    print(m.message_type, m.body, m.status, m.created_at)

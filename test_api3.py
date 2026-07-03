import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import Message; msgs = Message.objects.filter(body='Testing 123').order_by('-created_at')[:1]; 
for m in msgs:
    print(f'Found msg: {m.id}, Client: {m.client.id if m.client else None}, To: {m.contact.phone_number if m.contact else None}')

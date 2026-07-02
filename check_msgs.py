import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import Message; msgs = Message.objects.all().order_by('-created_at')[:5]; 
for m in msgs:
    print(f'Msg: {m.body}, From: {m.from_number}, To: {m.client.whatsapp_phone_number_id if m.client else None}, Is_Out: {m.is_outgoing}')

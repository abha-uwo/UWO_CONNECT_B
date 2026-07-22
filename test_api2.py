import os, django, sys; sys.stdout.reconfigure(encoding='utf-8'); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import Message, Contact; msgs = Message.objects.all().order_by('-created_at')[:3]; 
for m in msgs:
    contact = Contact.objects.filter(client=m.client, platform_id=m.to_address if m.message_type == 'OUTGOING' else m.from_address).first()
    print(f'Msg: {m.body}, To Contact: {contact.phone_number if contact else None}')

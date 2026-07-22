import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup()
from api.models import Client
from api.services.meta_webhook_service import MetaWebhookService

client = Client.objects.first()
if client:
    res = MetaWebhookService.send_whatsapp_message(
        client=client,
        to_number='917694045090',
        text_body='Hello from test script',
        phone_number_id=client.whatsapp_phone_number_id or '15556516125'
    )
    print('Result:', res)
else:
    print('No client found to test send')

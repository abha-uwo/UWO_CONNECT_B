import os, django, requests; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.whatsapp import send_whatsapp_message; 
try:
    res = send_whatsapp_message('15556516125', '1125247290680369', '917694045090', 'Hello from test script')
    print('Result:', res)
except Exception as e:
    print('Error:', e)

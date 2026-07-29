import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Client

clients = Client.objects.all()
print(f"\nTotal clients: {clients.count()}\n")

for client in clients:
    print(f"Client: {client.business_name}")
    print(f"  instagram_enabled : {client.instagram_enabled}")
    ig = client.instagram_config or {}
    print(f"  instagram_config  : {ig}")
    if ig:
        token = ig.get('access_token', '')
        ig_id = ig.get('instagram_business_id', '')
        print(f"  access_token      : {'✅ SET (' + token[:20] + '...)' if token else '❌ MISSING'}")
        print(f"  instagram_id      : {ig_id if ig_id else '❌ MISSING'}")
    else:
        print(f"  instagram_config  : ❌ EMPTY — nothing stored")
    print()

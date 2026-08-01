import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from api.models import User
from api.views import ClientViewSet

user = User.objects.get(email="abha@uwo24.com")
client_id = str(user.client.id)

factory = APIRequestFactory()
request = factory.get(f"/api/clients/{client_id}/")
force_authenticate(request, user=user)

view = ClientViewSet.as_view({'get': 'retrieve'})
try:
    response = view(request, pk=client_id)
    print("STATUS CODE:", response.status_code)
    if response.status_code != 200:
        print("RESPONSE DATA:", response.data if hasattr(response, 'data') else response.content)
except Exception as e:
    import traceback
    print("EXCEPTION OCCURRED:")
    traceback.print_exc()

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from api.views import KnowledgeBaseView
from api.models import User

factory = APIRequestFactory()
view = KnowledgeBaseView.as_view()

# Find an AGENT user
user = User.objects.filter(role='AGENT').first()
if not user:
    user = User.objects.first()

print(f"Testing with User: {user.username}, Role: {user.role}")

request = factory.get('/api/knowledge/')
force_authenticate(request, user=user)

try:
    response = view(request)
    print("API Response status code:", response.status_code)
    print("API Response data:", response.data)
except Exception as e:
    print("API Execution error:", str(e))

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User

try:
    user = User.objects.get(email='aditi@uwo24.com')
    user.set_password('admin123')
    user.is_active = True  # Ensure active
    user.status = 'APPROVED' # Ensure approved
    user.save()
    print("SUCCESS: Password for aditi@uwo24.com has been set to 'admin123' and status set to 'APPROVED'")
except User.DoesNotExist:
    print("ERROR: User aditi@uwo24.com does not exist in the database")
except Exception as e:
    print(f"ERROR: {e}")

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Client, User

# --- FILL THESE IN WITH THE VALUES FROM META DASHBOARD ---
INSTAGRAM_ACCESS_TOKEN = "PASTE_YOUR_GENERATED_TOKEN_HERE"
INSTAGRAM_BUSINESS_ID = "17841443390895451" # Defaulted to efv.framework2.o based on screenshot
# ---------------------------------------------------------

try:
    # Find the user by their username or email (usually username is the email)
    user = User.objects.get(username="abha@uwo24.com")
    
    if user.client:
        c = user.client
        c.instagram_enabled = True
        c.instagram_config = {
            "access_token": INSTAGRAM_ACCESS_TOKEN,
            "instagram_business_id": INSTAGRAM_BUSINESS_ID
        }
        c.save()
        print(f"✅ Successfully updated Instagram config specifically for client: {c.business_name}")
    else:
        print("❌ The user abha@uwo24.com exists, but they are not linked to any Client account.")
        
except User.DoesNotExist:
    print("❌ Could not find a user with the email/username 'abha@uwo24.com'.")

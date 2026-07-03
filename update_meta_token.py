import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import Client; 
for c in Client.objects.all():
    c.whatsapp_access_token = 'EAAOFcZAhTdBUBR20hkaLpOZByGzyaORLOhN6Otz7FmsgLwAOznZAAy3cq5AoEZAUsZCmiBotuaxAlvIpbQJjLUChDMz8ZA1kOYUNS9RMFGO5XZB9I2N2HEsoSeluO6ApDF2tCFDW6gkdfZCkYkhce3GwM27FI1HfxMBweAq7qJ46iGq2Cu9rYkgvDzym4Ng6suPeJrWYWhiZC3NhvXTVMLlptZBBbKb5EXhbmVN7xjLv0JuFs0yKYtHSOdB0YkwJ3Tb1AZCGowtEzpjO0n22WOp0nzmkaf7'
    c.save()
print('Token updated for all clients!')

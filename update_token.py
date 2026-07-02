import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import User; 
try:
    user = User.objects.get(email='abha@uwo24.com')
    user.client.whatsapp_access_token = 'EAAOFcZAhTdBUBRZBqmHXbnloQdu70z3pomH5zZAVIobaRjOQXn54ZCUaxpuAd18aJYEHd1nLoQV2fWKOoF9aEZB8w3OnSTFSQEAHtv54sC1eQdrcFMpZAp5fN0XW9eAvZCuQa7PtVPf5vu1XhMakf2dqlUOmLUNKUs4ZA07VppQnd2UrM3sOxUUZBf40qyZAWv22WNMtk4pR4NQqVkdhpUHx6bcHZBAQize2FxZADg0VdcsV2K6ZAYdAhtRTtiP8ZB9vuBZBmsNRtRPBatiXCiTpCZBT3acS9cmlKQZDZD'
    user.client.save()
    print('Success')
except Exception as e:
    print(f'Error: {e}')

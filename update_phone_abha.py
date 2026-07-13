import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); django.setup(); from api.models import Client, User; 
try:
    user = User.objects.get(email='abha@uwo24.com')
    if user.client:
        user.client.whatsapp_phone_number_id = '1144355915438778'
        user.client.whatsapp_waba_id = '947532301669617'
        user.client.phone_number = '+918358990909'
        user.client.whatsapp_access_token = 'EAAOFcZAhTdBUBR6ZCurFTxLGsXX5OZArXnyRytzrXwUoTjnm02sCmwlkeh53PA0QvQ060fXtD57MeYIbNEQX5R9GWMvOwaZCudOcO8vajRe2iuOfgqlDQScyanDfuzbh9w0esx4I6IOiFo2IKRbfETZACcxhJEL5dShBP21ZBO81xHbvoHQ9S1EsP1IReGRxC7ngZDZD'
        user.client.whatsapp_verify_token = 'aisaconnect_secure_token'
        user.client.save()
        print('Updated successfully for abha@uwo24.com')
    else:
        print('User abha@uwo24.com does not have a client associated.')
except Exception as e:
    print(f'Error: {e}')

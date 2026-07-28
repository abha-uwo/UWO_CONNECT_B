import firebase_admin
from firebase_admin import auth

class FirebaseIntegration:
    @staticmethod
    def verify_id_token(token):
        return auth.verify_id_token(token)

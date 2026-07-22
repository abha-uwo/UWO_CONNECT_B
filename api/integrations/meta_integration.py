import requests

class MetaIntegration:
    @staticmethod
    def send_whatsapp_message(phone_number_id, token, payload):
        url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        return requests.post(url, headers=headers, json=payload)

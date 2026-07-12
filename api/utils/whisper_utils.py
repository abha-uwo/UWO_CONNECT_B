import os
import requests
from django.conf import settings

def transcribe_audio_with_whisper(audio_file_url, access_token):
    """
    Downloads audio file using Meta credentials, then calls OpenAI Whisper API
    to transcribe the voice note back into text.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return ""
        
    try:
        # Step 1: Download binary from WhatsApp Cloud API URL
        headers = {"Authorization": f"Bearer {access_token}"}
        audio_response = requests.get(audio_file_url, headers=headers, timeout=15)
        
        if audio_response.status_code != 200:
            return ""
            
        audio_content = audio_response.content
        
        # Step 2: Upload to OpenAI Whisper API
        url = "https://api.openai.com/v1/audio/transcriptions"
        whisper_headers = {
            "Authorization": f"Bearer {openai_api_key}"
        }
        
        # Whisper expects multipart/form-data with file object
        files = {
            'file': ('voice_note.ogg', audio_content, 'audio/ogg')
        }
        data = {
            'model': 'whisper-1'
        }
        
        response = requests.post(url, headers=whisper_headers, files=files, data=data, timeout=20)
        if response.status_code == 200:
            return response.json().get('text', '')
        return ""
        
    except Exception as e:
        print(f"[Whisper Transcription Error] {str(e)}")
        return ""

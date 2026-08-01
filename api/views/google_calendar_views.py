import os
import google_auth_oauthlib.flow
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.http import HttpResponseRedirect
from api.models import Client

# Allow HTTP traffic for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# We request the full Calendar scope to read and write events
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_client_config():
    # We will reuse the GMAIL credentials since they are for the same Google Cloud Project
    return {
        "web": {
            "client_id": os.environ.get("GMAIL_CLIENT_ID", ""),
            "client_secret": os.environ.get("GMAIL_CLIENT_SECRET", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

class GoogleCalendarConnectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = request.user.client
        if not client:
            return Response({"error": "User does not have an associated client."}, status=400)
            
        client_config = get_client_config()
        if not client_config['web']['client_id'] or not client_config['web']['client_secret']:
            return Response({"error": "Google API credentials not configured on backend."}, status=500)
        
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config,
            scopes=SCOPES
        )
        
        redirect_uri = os.environ.get("GOOGLE_CALENDAR_REDIRECT_URI", "http://localhost:8080/api/auth/google-calendar/callback")
        flow.redirect_uri = redirect_uri
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent' # Force consent to ensure we get a refresh token
        )
        
        # Save mapping from state to client_id in cache for 1 hour
        cache.set(f'calendar_state_{state}', client.id, timeout=3600)
        # Save the PKCE code_verifier
        if hasattr(flow, 'code_verifier'):
            cache.set(f'calendar_verifier_{state}', flow.code_verifier, timeout=3600)
        
        return Response({"url": authorization_url})

class GoogleCalendarCallbackView(APIView):
    # This endpoint is called by Google, so no auth classes
    permission_classes = []
    authentication_classes = []
    
    def get(self, request):
        state = request.GET.get('state')
        error = request.GET.get('error')
        
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        
        if error:
            return HttpResponseRedirect(f"{frontend_url}/client/channels?google_calendar_error={error}")
            
        client_id = cache.get(f'calendar_state_{state}')
        if not client_id:
            return HttpResponseRedirect(f"{frontend_url}/client/channels?google_calendar_error=invalid_state")
            
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return HttpResponseRedirect(f"{frontend_url}/client/channels?google_calendar_error=client_not_found")
            
        client_config = get_client_config()
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            state=state
        )
        flow.redirect_uri = os.environ.get("GOOGLE_CALENDAR_REDIRECT_URI", "http://localhost:8080/api/auth/google-calendar/callback")
        
        authorization_response = request.build_absolute_uri()
        # Fix http to https if behind a proxy
        if 'https' not in authorization_response and 'localhost' not in authorization_response:
             authorization_response = authorization_response.replace('http:', 'https:')
             
        # Add the code_verifier back to the flow for PKCE
        code_verifier = cache.get(f'calendar_verifier_{state}')
        if code_verifier:
            flow.code_verifier = code_verifier
             
        try:
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials
            
            # Save the tokens in the client model
            client.google_calendar_enabled = True
            client.google_calendar_config = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            client.save()
            
            return HttpResponseRedirect(f"{frontend_url}/client/channels?google_calendar_connected=true")
            
        except Exception as e:
            print(f"Error fetching Google Calendar token: {str(e)}")
            return HttpResponseRedirect(f"{frontend_url}/client/channels?google_calendar_error=token_fetch_failed: {str(e)}")

from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Client
from api.services.google_calendar_service import GoogleCalendarService

class PublicCalendarSlotsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({"error": "Business not found"}, status=404)
            
        if not client.google_calendar_enabled:
            return Response({"error": "Business has not connected Google Calendar"}, status=400)
            
        target_date = request.query_params.get("date")
        if not target_date:
            return Response({"error": "date parameter is required (YYYY-MM-DD)"}, status=400)
            
        # check_availability returns a text summary, but for public UI we might want structured data.
        # However, for simplicity we can just return the summary text, 
        # or we could modify GoogleCalendarService to return JSON slots.
        # Given current implementation, we will use the same service and frontend will display it.
        # Actually, let's just return the text response and frontend can render it, 
        # or we can parse it. For now, returning the text summary is fine.
        
        availability_text = GoogleCalendarService.check_availability(client, target_date)
        return Response({"availability": availability_text, "business_name": client.business_name})

class PublicCalendarBookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({"error": "Business not found"}, status=404)
            
        if not client.google_calendar_enabled:
            return Response({"error": "Business has not connected Google Calendar"}, status=400)
            
        target_date = request.data.get("date")
        target_time = request.data.get("time")
        customer_name = request.data.get("customer_name")
        
        if not all([target_date, target_time, customer_name]):
            return Response({"error": "date, time, and customer_name are required"}, status=400)
            
        booking_result = GoogleCalendarService.book_appointment(client, target_date, target_time, customer_name)
        
        if "Error" in booking_result:
            return Response({"error": booking_result}, status=400)
            
        return Response({"success": True, "message": booking_result})

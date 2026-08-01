import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pytz

class GoogleCalendarService:
    @staticmethod
    def _get_credentials(client):
        """Builds Google Credentials object from client's DB config."""
        config = client.google_calendar_config
        if not config:
            return None
        
        return Credentials(
            token=config.get('token'),
            refresh_token=config.get('refresh_token'),
            token_uri=config.get('token_uri'),
            client_id=config.get('client_id'),
            client_secret=config.get('client_secret'),
            scopes=config.get('scopes')
        )

    @staticmethod
    def check_availability(client, target_date_str):
        """
        Fetches free/busy information for a given date string (YYYY-MM-DD).
        Returns a summary string of available slots to feed to the AI.
        """
        creds = GoogleCalendarService._get_credentials(client)
        if not creds:
            return "Error: Client does not have Google Calendar connected."
            
        try:
            service = build('calendar', 'v3', credentials=creds)
            
            # Use Asia/Kolkata timezone or default to UTC
            tz = pytz.timezone('Asia/Kolkata')
            
            # Parse date and set start/end bounds for the working day (e.g. 9 AM to 6 PM)
            target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d").date()
            start_dt = tz.localize(datetime.datetime.combine(target_date, datetime.time(9, 0, 0)))
            end_dt = tz.localize(datetime.datetime.combine(target_date, datetime.time(18, 0, 0)))
            
            time_min = start_dt.isoformat()
            time_max = end_dt.isoformat()
            
            # Call FreeBusy API
            body = {
                "timeMin": time_min,
                "timeMax": time_max,
                "timeZone": 'Asia/Kolkata',
                "items": [{"id": "primary"}]
            }
            eventsResult = service.freebusy().query(body=body).execute()
            calendars = eventsResult.get('calendars', {})
            primary = calendars.get('primary', {})
            busy_slots = primary.get('busy', [])
            
            if not busy_slots:
                return f"The entire day ({target_date_str}) from 9:00 AM to 6:00 PM is free."
            
            # Format busy slots to human readable text
            busy_text = []
            for slot in busy_slots:
                start_time = datetime.datetime.fromisoformat(slot['start']).strftime('%I:%M %p')
                end_time = datetime.datetime.fromisoformat(slot['end']).strftime('%I:%M %p')
                busy_text.append(f"{start_time} to {end_time}")
                
            response = f"On {target_date_str}, the calendar is BUSY during these times:\n"
            response += "\n".join(busy_text)
            response += "\nAll other times between 9:00 AM and 6:00 PM are FREE. You can offer any free 30-minute slot."
            
            return response
            
        except Exception as e:
            print(f"Error checking calendar availability: {str(e)}")
            return "Error: Could not fetch calendar data."

    @staticmethod
    def book_appointment(client, date_str, time_str, customer_name):
        """
        Books a 30 minute slot.
        date_str: YYYY-MM-DD
        time_str: HH:MM (24-hour format)
        """
        creds = GoogleCalendarService._get_credentials(client)
        if not creds:
            return "Error: Client does not have Google Calendar connected."
            
        try:
            service = build('calendar', 'v3', credentials=creds)
            tz = pytz.timezone('Asia/Kolkata')
            
            start_dt_naive = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            start_dt = tz.localize(start_dt_naive)
            end_dt = start_dt + datetime.timedelta(minutes=30)
            
            event = {
                'summary': f'Meeting with {customer_name}',
                'description': 'Booked automatically by UwoConnect AI.',
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
            }
            
            event_result = service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created: {event_result.get('htmlLink')}")
            return f"Successfully booked appointment on {date_str} at {time_str} for {customer_name}."
            
        except Exception as e:
            print(f"Error booking appointment: {str(e)}")
            return f"Error: Could not book the appointment due to an internal error."

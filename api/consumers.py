import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
import jwt
from django.conf import settings
from asgiref.sync import sync_to_async
from .models import User

class InboxConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if not token:
            await self.close()
            return

        try:
            # Decode the JWT token
            decoded_data = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
            user_id = decoded_data.get(settings.SIMPLE_JWT['USER_ID_CLAIM'])
            
            user = await self.get_user(user_id)
            if not user or not user.client_id:
                await self.close()
                return
                
            self.client_id = str(user.client_id)
            self.room_group_name = f'inbox_{self.client_id}'

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            
            # Send initial connection success message
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Connected to inbox successfully'
            }))

        except Exception as e:
            await self.close()

    @sync_to_async
    def get_user(self, user_id):
        try:
            return UserRepository.get_user(id=user_id)
        except User.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket (if frontend sends anything, mostly for debugging or manual testing)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

    # Receive message from room group
    async def new_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': message
        }))

class TeamChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if not token:
            await self.close()
            return

        try:
            decoded_data = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
            user_id = decoded_data.get(settings.SIMPLE_JWT['USER_ID_CLAIM'])
            
            user = await self.get_user(user_id)
            if not user or not user.client_id:
                await self.close()
                return
                
            self.client_id = str(user.client_id)
            self.room_group_name = f'teamchat_{self.client_id}'

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

        except Exception as e:
            await self.close()

    @sync_to_async
    def get_user(self, user_id):
        try:
            return UserRepository.get_user(id=user_id)
        except User.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def new_team_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'new_team_message',
            'message': message
        }))

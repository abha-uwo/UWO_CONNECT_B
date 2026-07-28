import secrets
import datetime
from django.utils import timezone
from ..models import TeamInvite, TeamMessage
from ..serializers import TeamInviteSerializer, TeamMessageSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..repositories.team_invite_repository import TeamInviteRepository
from ..repositories.team_message_repository import TeamMessageRepository

class TeamService:
    @staticmethod
    def create_invite(client, email):
        token = secrets.token_urlsafe(32)
        invite = TeamInviteRepository.create_teaminvite(
            client=client,
            email=email,
            token=token,
            expires_at=timezone.now() + datetime.timedelta(days=7)
        )
        serializer = TeamInviteSerializer(invite)
        return serializer.data

    @staticmethod
    def delete_invite(client, invite_id):
        try:
            invite = TeamInviteRepository.get_teaminvite(id=invite_id, client=client)
            invite.delete()
            return True
        except TeamInvite.DoesNotExist:
            return False

    @staticmethod
    def send_chat_message(client, user, body):
        msg = TeamMessageRepository.create_teammessage(
            client=client,
            sender=user,
            body=body
        )
        
        serializer = TeamMessageSerializer(msg)
        
        # Broadcast via WebSockets
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'teamchat_{client.id}',
            {
                'type': 'new_team_message',
                'message': serializer.data
            }
        )
        
        return serializer.data

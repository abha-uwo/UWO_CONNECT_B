from ..repositories.team_invite_repository import TeamInviteRepository
from ..repositories.team_message_repository import TeamMessageRepository
from ..repositories.user_repository import UserRepository
from ..repositories.client_repository import ClientRepository
from ..permissions.custom_permissions import IsApprovedUser
from rest_framework import status, views, viewsets, serializers
from rest_framework.response import Response
from firebase_admin import auth as firebase_auth
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ..serializers import RegisterSerializer, UserSerializer, ClientSerializer, AutomationSerializer, WorkflowSerializer, ContactSerializer, TemplateSerializer, CampaignSerializer, SupportMessageSerializer, AuditLogSerializer, TeamInviteSerializer, ProductSerializer, OrderSerializer
from ..models import User, Client, Automation, Message, Workflow, KnowledgeDocument, KnowledgeChunk, Contact, Template, Campaign, SupportMessage, AuditLog, TeamInvite, Product, Order
import requests
import os
import json
from ..services.ai_service import get_ai_response, get_platform_assistance, get_rag_response, get_embedding, chunk_text, find_relevant_chunks
from rest_framework.permissions import BasePermission

def get_tenant_client(request):
    if not request.user or not request.user.is_authenticated:
        return None
    if request.user.role == 'ADMIN':
        client_id = request.query_params.get('client_id') or request.data.get('client_id')
        if client_id:
            try:
                return ClientRepository.get_client(id=client_id)
            except (Client.DoesNotExist, ValueError):
                pass
        return None
    return request.user.client

class TeamMemberViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'client', None):
            return UserRepository.filter_users(client=user.client)
        return User.objects.none()

    def perform_destroy(self, instance):
        if instance == self.request.user:
            raise serializers.ValidationError("Cannot remove yourself from the team.")
        instance.delete()


class TeamInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not getattr(request.user, 'client', None):
            return Response([], status=status.HTTP_200_OK)
        invites = TeamInviteRepository.filter_teaminvites(client=request.user.client)
        serializer = TeamInviteSerializer(invites, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not getattr(request.user, "client", None):
            return Response({"error": "No client associated"}, status=status.HTTP_400_BAD_REQUEST)
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        from ..services.team_service import TeamService
        result = TeamService.create_invite(request.user.client, email)
        return Response(result, status=status.HTTP_201_CREATED)

    def delete(self, request):
        if not getattr(request.user, "client", None):
            return Response({"error": "No client associated"}, status=status.HTTP_400_BAD_REQUEST)
        invite_id = request.query_params.get("id")
        if not invite_id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        from ..services.team_service import TeamService
        success = TeamService.delete_invite(request.user.client, invite_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Invite not found"}, status=status.HTTP_404_NOT_FOUND)

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..models import TeamMessage
from ..serializers import TeamMessageSerializer


class TeamChatView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not getattr(request.user, 'client', None):
            return Response({"error": "No client associated"}, status=status.HTTP_400_BAD_REQUEST)
            
        messages = TeamMessageRepository.filter_teammessages(client=request.user.client).order_by('-created_at')[:50]
        # Return in chronological order
        serializer = TeamMessageSerializer(reversed(messages), many=True)
        return Response(serializer.data)

    def post(self, request):
        if not getattr(request.user, "client", None):
            return Response({"error": "No client associated"}, status=status.HTTP_400_BAD_REQUEST)
        body = request.data.get("body")
        if not body:
            return Response({"error": "Body is required"}, status=status.HTTP_400_BAD_REQUEST)
        from ..services.team_service import TeamService
        result = TeamService.send_chat_message(request.user.client, request.user, body)
        return Response(result, status=status.HTTP_201_CREATED)




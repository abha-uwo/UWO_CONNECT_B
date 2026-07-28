from ..permissions.custom_permissions import IsApprovedUser
from rest_framework import status, views, viewsets
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
from ..repositories.client_repository import ClientRepository
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

class RegisterView(views.APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, req):
        serializer = RegisterSerializer(data=req.data)
        if serializer.is_valid():
            from ..services.auth_service import AuthService
            result = AuthService.register_user(serializer)
            if result.get("status") == "APPROVED":
                return Response({
                    "user": result["user"],
                    "token": result["token"]
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "message": result["message"],
                    "userId": result["userId"]
                }, status=status.HTTP_201_CREATED)
            
        first_error = next(iter(serializer.errors.values()))[0]
        return Response({"message": str(first_error)}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')


class LoginView(views.APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, req):
        email = req.data.get('email', '').strip().lower()
        password = req.data.get('password', '')

        from ..services.auth_service import AuthService
        result = AuthService.login_user(email, password)
        
        if "error" in result:
            return Response({"message": result["error"]}, status=result["status_code"])

        return Response({
            "user": result["user"],
            "token": result["token"]
        })

@method_decorator(csrf_exempt, name='dispatch')


class GoogleLoginView(views.APIView):
    """Legacy Google login — kept for backward compatibility."""
    permission_classes = []
    authentication_classes = []

    def post(self, req):
        return Response({"message": "Please use Firebase authentication. This endpoint is deprecated."}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')


class GoogleClientIdView(views.APIView):
    """Legacy Google Client ID endpoint — kept for backward compatibility."""
    permission_classes = []
    authentication_classes = []

    def get(self, req):
        return Response({"client_id": ""})

@method_decorator(csrf_exempt, name='dispatch')


class FirebaseLoginView(views.APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, req):
        id_token = req.data.get('id_token', '').strip()
        name = req.data.get('name', '').strip()
        invite_token = req.data.get('invite_token', '').strip()
        business_name = req.data.get('business_name', '').strip()

        from ..services.auth_service import AuthService
        result = AuthService.process_firebase_login(id_token, name, invite_token, business_name)

        if "error" in result:
            return Response({"message": result["error"]}, status=result["status_code"])

        if result.get("is_created"):
            if result.get("status") == "PENDING":
                return Response({
                    "message": result["message"],
                    "userId": result["userId"]
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "user": result["user"],
                    "token": result["token"]
                }, status=status.HTTP_201_CREATED)

        return Response({
            "user": result["user"],
            "token": result["token"]
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.client:
            return Response({"message": "No client associated"}, status=404)
        serializer = ClientSerializer(request.user.client)
        return Response({
            "client": serializer.data,
            "user": {
                "name": f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                "email": request.user.email,
            }
        })

    def patch(self, request):
        if not request.user.client:
            return Response({"message": "No client associated"}, status=404)
        
        # Update User fields if provided
        user = request.user
        if 'name' in request.data:
            name_parts = request.data['name'].split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.save()

        # Update Client fields
        serializer = ClientSerializer(request.user.client, data=request.data, partial=True)
        if serializer.is_valid():
            client_instance = serializer.save()
            
            # --- Programmatic Webhook Auto-Subscription to Meta App ---
            import requests
            
            # 1. Handle Facebook Page Subscription
            facebook_config = request.data.get('facebook_config')
            if facebook_config and isinstance(facebook_config, dict):
                page_id = facebook_config.get('page_id')
                access_token = facebook_config.get('access_token')
                if page_id and access_token:
                     try:
                         sub_url = f"https://graph.facebook.com/v20.0/{page_id}/subscribed_apps"
                         sub_payload = {
                             "subscribed_fields": "messages,messaging_postbacks,messaging_optins,message_deliveries",
                             "access_token": access_token
                         }
                         res = requests.post(sub_url, data=sub_payload, timeout=10)
                         print(f"\nfrom ..repositories.campaign_repository import TemplateRepository\nfrom ..repositories.campaign_repository import CampaignRepository\nfrom ..repositories.system_repository import SystemRepository\nfrom ..repositories.message_repository import SupportMessageRepository\nfrom ..repositories.client_repository import ClientRepository\nfrom ..repositories.user_repository import TeamInviteRepository\nfrom ..repositories.user_repository import UserRepository\nfrom ..repositories.automation_repository import WorkflowRepository\nfrom ..repositories.message_repository import TeamMessageRepository\nfrom ..repositories.message_repository import MessageRepository\nfrom ..repositories.knowledge_repository import KnowledgeRepository\nfrom ..repositories.automation_repository import AutomationRepository\nfrom ..repositories.contact_repository import ContactRepository\n\n[Meta API] Facebook Page {page_id} Webhook Subscription Response: {res.status_code} {res.text}\n")
                     except Exception as e:
                         print(f"Error subscribing Facebook page {page_id}: {str(e)}")
            
            # 2. Handle Instagram Page Subscription
            instagram_config = request.data.get('instagram_config')
            if instagram_config and isinstance(instagram_config, dict):
                access_token = instagram_config.get('access_token')
                if access_token:
                    try:
                        # Find Page ID associated with the Instagram access token / Page Access Token
                        me_res = requests.get(f"https://graph.facebook.com/v20.0/me?fields=id,name&access_token={access_token}", timeout=10)
                        if me_res.status_code == 200:
                            page_id = me_res.json().get('id')
                            if page_id:
                                sub_url = f"https://graph.facebook.com/v20.0/{page_id}/subscribed_apps"
                                sub_payload = {
                                    "subscribed_fields": "messages,messaging_postbacks,messaging_optins,message_deliveries",
                                    "access_token": access_token
                                }
                                res = requests.post(sub_url, data=sub_payload, timeout=10)
                                print(f"\n[Meta API] Instagram linked Facebook Page {page_id} Webhook Subscription Response: {res.status_code} {res.text}\n")
                    except Exception as e:
                         print(f"Error subscribing Instagram linked page: {str(e)}")
                         
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

from ..models import User, Client, Automation, Workflow, GlobalSetting
from ..serializers import RegisterSerializer, UserSerializer, ClientSerializer, AutomationSerializer, WorkflowSerializer, GlobalSettingSerializer


class ForgotPasswordSendOTPView(views.APIView):
    permission_classes = []

    def post(self, req):
        email = req.data.get('email', '').lower().strip()
        from ..services.auth_service import AuthService
        result = AuthService.forgot_password_send_otp(email)
        return Response({"message": result.get("message")}, status=result.get("status_code", 200))

@method_decorator(csrf_exempt, name='dispatch')


class ForgotPasswordVerifyOTPView(views.APIView):
    permission_classes = []

    def post(self, req):
        email = req.data.get('email', '').lower().strip()
        otp = req.data.get('otp', '').strip()
        
        from ..services.auth_service import AuthService
        result = AuthService.forgot_password_verify_otp(email, otp)
        return Response({"message": result.get("message")}, status=result.get("status_code", 200))

@method_decorator(csrf_exempt, name='dispatch')


class ForgotPasswordResetView(views.APIView):
    permission_classes = []

    def post(self, req):
        email = req.data.get('email', '').lower().strip()
        password = req.data.get('password', '')
        
        from ..services.auth_service import AuthService
        result = AuthService.forgot_password_reset(email, password)
        return Response({"message": result.get("message")}, status=result.get("status_code", 200))



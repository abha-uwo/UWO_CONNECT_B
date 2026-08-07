from ..services.admin_service import AdminService
import threading
from ..repositories.template_repository import TemplateRepository
from ..repositories.campaign_repository import CampaignRepository
from ..repositories.client_repository import ClientRepository
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

class TemplateViewSet(viewsets.ModelViewSet):
    serializer_class = TemplateSerializer
    permission_classes = [IsApprovedUser]

    def get_queryset(self):
        client = get_tenant_client(self.request)
        if self.request.user.role == 'ADMIN' and not client:
            return Template.objects.none()
        return TemplateRepository.filter_templates(client=client)

    def perform_create(self, serializer):
        client = get_tenant_client(self.request)
        instance = serializer.save(client=client)
        AdminService.log_admin_action(self.request, instance, 'Templates', 'CREATE', after_value=str(serializer.data))

    def perform_update(self, serializer):
        before_instance = self.get_object()
        before_data = str(self.get_serializer(before_instance).data)
        instance = serializer.save()
        AdminService.log_admin_action(self.request, instance, 'Templates', 'UPDATE', before_value=before_data, after_value=str(serializer.data))

    def perform_destroy(self, instance):
        before_data = str(self.get_serializer(instance).data)
        AdminService.log_admin_action(self.request, instance, 'Templates', 'DELETE', before_value=before_data)
        instance.delete()

    @action(detail=False, methods=['post'])
    def sync_from_meta(self, request):
        client = request.user.client
        token = client.whatsapp_access_token
        if not client.whatsapp_waba_id or not token:
            return Response({"message": "WhatsApp WABA ID or Access Token is missing in client settings."}, status=400)
        
        url = f"https://graph.facebook.com/v19.0/{client.whatsapp_waba_id}/message_templates"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        try:
            res = requests.get(url, headers=headers)
            data = res.json()
            if 'data' in data:
                synced_count = 0
                for tmpl in data['data']:
                    Template.objects.update_or_create(
                        client=client,
                        name=tmpl.get('name'),
                        language=tmpl.get('language'),
                        defaults={
                            'category': tmpl.get('category'),
                            'status': tmpl.get('status'),
                            'components': tmpl.get('components', [])
                        }
                    )
                    synced_count += 1
                return Response({"message": f"Successfully synced {synced_count} templates."})
            return Response({"message": "Failed to fetch templates from Meta.", "details": data}, status=400)
        except Exception as e:
            return Response({"message": str(e)}, status=500)


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [IsApprovedUser]

    def get_queryset(self):
        client = get_tenant_client(self.request)
        if self.request.user.role == 'ADMIN' and not client:
            return Campaign.objects.none()
        return CampaignRepository.filter_campaigns(client=client).order_by('-created_at')

    def perform_create(self, serializer):
        from django.utils import timezone
        client = get_tenant_client(self.request)
        
        scheduled_at = serializer.validated_data.get('scheduled_at')
        if scheduled_at and scheduled_at > timezone.now():
            campaign = serializer.save(client=client, status='SCHEDULED')
        else:
            campaign = serializer.save(client=client, status='SENDING')

        delay_hours = self.request.data.get('followup_delay_hours')
        followup_template_id = self.request.data.get('followup_template_id')
        if delay_hours and followup_template_id:
            from ..models import CampaignFollowUp, Template
            template = Template.objects.filter(id=followup_template_id, client=client).first()
            if template:
                CampaignFollowUp.objects.create(
                    campaign=campaign,
                    delay_hours=int(delay_hours),
                    followup_template=template
                )

        AdminService.log_admin_action(self.request, campaign, 'Campaigns', 'CREATE', after_value=str(serializer.data))
        if campaign.status == 'SENDING':
            thread = threading.Thread(target=self.process_campaign, args=(campaign.id,))
            thread.start()

    def perform_update(self, serializer):
        before_instance = self.get_object()
        before_data = str(self.get_serializer(before_instance).data)
        instance = serializer.save()
        AdminService.log_admin_action(self.request, instance, 'Campaigns', 'UPDATE', before_value=before_data, after_value=str(serializer.data))

    def perform_destroy(self, instance):
        before_data = str(self.get_serializer(instance).data)
        AdminService.log_admin_action(self.request, instance, 'Campaigns', 'DELETE', before_value=before_data)
        instance.delete()

    def process_campaign(self, campaign_id):
        from ..services.campaign_service import CampaignService
        CampaignService.process_campaign(campaign_id)


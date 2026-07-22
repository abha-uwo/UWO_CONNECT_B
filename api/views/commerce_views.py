from ..services.admin_service import AdminService
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


from ..repositories.product_repository import ProductRepository
from ..repositories.order_repository import OrderRepository

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsApprovedUser]

    def get_queryset(self):
        client = get_tenant_client(self.request)
        if client:
            return ProductRepository.filter_products(client=client)
        return ProductRepository.get_all()

    def perform_create(self, serializer):
        client = get_tenant_client(self.request)
        instance = serializer.save(client=client)
        AdminService.log_admin_action(self.request, instance, 'Products', 'CREATE', after_value=str(serializer.data))

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsApprovedUser]

    def get_queryset(self):
        client = get_tenant_client(self.request)
        if client:
            return OrderRepository.filter_orders(client=client)
        return OrderRepository.get_all()

    def perform_create(self, serializer):
        client = get_tenant_client(self.request)
        instance = serializer.save(client=client)
        AdminService.log_admin_action(self.request, instance, 'Orders', 'CREATE', after_value=str(serializer.data))

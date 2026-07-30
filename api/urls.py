from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, GoogleLoginView, GoogleClientIdView, FirebaseLoginView, ClientViewSet, AutomationViewSet, WorkflowViewSet, 
    ContactViewSet, AdminStatsView, ClientStatsView, AdminAutomationsView, AdminMessagesView, 
    WhatsAppWebhookView, FacebookInstagramWebhookView, AdminUsersView, ProfileView, ClientMessagesView, 
    GlobalSettingsView, PlatformAssistantView, KnowledgeBaseView, TemplateViewSet, 
    CampaignViewSet, ForgotPasswordSendOTPView, ForgotPasswordVerifyOTPView, ForgotPasswordResetView,
    SupportMessageViewSet, AdminImpersonateView, AuditLogViewSet,
    SuggestDraftView, TeamMemberViewSet, TeamInviteView, TeamChatView, ProductViewSet, OrderViewSet,
    CreatePaymentOrderView, VerifyPaymentView, PaymentHistoryView, CashfreeWebhookView, RazorpayWebhookView,
    WhatsAppEmbeddedSignupView
)

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'automations', AutomationViewSet, basename='automation')
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'templates', TemplateViewSet, basename='template')
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'support/messages', SupportMessageViewSet, basename='support-message')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'team/members', TeamMemberViewSet, basename='team-member')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('team/invites/', TeamInviteView.as_view(), name='team-invites'),
    path('team/chat/', TeamChatView.as_view(), name='team-chat'),
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/google-login', GoogleLoginView.as_view(), name='google-login'),
    path('auth/google-client-id', GoogleClientIdView.as_view(), name='google-client-id'),
    path('auth/firebase-login', FirebaseLoginView.as_view(), name='firebase-login'),
    path('auth/forgot-password/send-otp', ForgotPasswordSendOTPView.as_view(), name='forgot-password-send-otp'),
    path('auth/forgot-password/verify-otp', ForgotPasswordVerifyOTPView.as_view(), name='forgot-password-verify-otp'),
    path('auth/forgot-password/reset', ForgotPasswordResetView.as_view(), name='forgot-password-reset'),
    path('auth/whatsapp/embedded-signup', WhatsAppEmbeddedSignupView.as_view(), name='whatsapp-embedded-signup'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('messages/', ClientMessagesView.as_view(), name='client-messages'),
    path('messages/suggest_draft/', SuggestDraftView.as_view(), name='suggest-draft'),
    path('client/stats', ClientStatsView.as_view(), name='client-stats'),
    path('admin/stats', AdminStatsView.as_view(), name='admin-stats'),
    path('admin/automations', AdminAutomationsView.as_view(), name='admin-automations'),
    path('admin/messages', AdminMessagesView.as_view(), name='admin-messages'),
    path('admin/users', AdminUsersView.as_view(), name='admin-users'),
    path('admin/users/<str:pk>', AdminUsersView.as_view(), name='admin-user-detail'),
    path('platform-assistant/', PlatformAssistantView.as_view(), name='platform-assistant'),
    path('admin/settings/global', GlobalSettingsView.as_view(), name='global-settings'),
    path('webhook/whatsapp', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
    path('webhook/whatsapp/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook-slash'),
    path('webhooks/whatsapp', WhatsAppWebhookView.as_view(), name='whatsapp-webhooks'),
    path('webhooks/whatsapp/', WhatsAppWebhookView.as_view(), name='whatsapp-webhooks-slash'),
    path('webhook/facebook-instagram', FacebookInstagramWebhookView.as_view(), name='facebook-instagram-webhook'),
    path('webhook/facebook-instagram/', FacebookInstagramWebhookView.as_view(), name='facebook-instagram-webhook-slash'),
    path('webhooks/facebook', FacebookInstagramWebhookView.as_view(), name='facebook-webhooks'),
    path('webhooks/facebook/', FacebookInstagramWebhookView.as_view(), name='facebook-webhooks-slash'),
    # RAG Knowledge Base
    path('knowledge/', KnowledgeBaseView.as_view(), name='knowledge-base'),
    path('knowledge/<str:pk>/', KnowledgeBaseView.as_view(), name='knowledge-base-detail'),
    path('admin/impersonate', AdminImpersonateView.as_view(), name='admin-impersonate'),
    # Razorpay / Cashfree Payments
    path('payments/create-order', CreatePaymentOrderView.as_view(), name='payment-create-order'),
    path('payments/verify-order', VerifyPaymentView.as_view(), name='payment-verify-order'),
    path('payments/history', PaymentHistoryView.as_view(), name='payment-history'),
    path('payments/webhook', RazorpayWebhookView.as_view(), name='payment-webhook'),
]


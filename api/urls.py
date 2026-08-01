from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, GoogleLoginView, GoogleClientIdView, FirebaseLoginView, ClientViewSet, AutomationViewSet, WorkflowViewSet, 
    ContactViewSet, AdminStatsView, ClientStatsView, AdminAutomationsView, AdminMessagesView, 
    WhatsAppWebhookView, FacebookInstagramWebhookView, AdminUsersView, ProfileView, ClientMessagesView, MediaProxyView,
    GlobalSettingsView, PlatformAssistantView, KnowledgeBaseView, TemplateViewSet, 
    CampaignViewSet, ForgotPasswordSendOTPView, ForgotPasswordVerifyOTPView, ForgotPasswordResetView,
    SupportMessageViewSet, AdminImpersonateView, AuditLogViewSet,
    SuggestDraftView, TeamMemberViewSet, TeamInviteView, TeamChatView, ProductViewSet, OrderViewSet,
    CreatePaymentOrderView, VerifyPaymentView, PaymentHistoryView, CashfreeWebhookView, RazorpayWebhookView,
    WhatsAppEmbeddedSignupView, GmailConnectView, GmailCallbackView, GmailSyncView,
    InstagramEmbeddedSignupView, FacebookEmbeddedSignupView, InstagramOAuthCallbackView,
    ProjectViewSet, TaskViewSet, WorkReportView, WorkApprovalView, TeamChannelView,
    TeamChatMessageView, TeamAnalyticsView, TeamAICopilotView, AttendanceViewSet, LeaveRequestViewSet,
    OneDriveConnectView, OneDriveCallbackView, OneDriveStatusView, OneDriveSyncView, OneDriveDisconnectView,
    GoogleCalendarConnectView, GoogleCalendarCallbackView, GoogleCalendarStatusView, GoogleCalendarSyncView, GoogleCalendarCreateEventView, GoogleCalendarDisconnectView,
    GoogleSheetsConnectView, GoogleSheetsCallbackView, GoogleSheetsStatusView, GoogleSheetsSyncView, GoogleSheetsAppendRowView, GoogleSheetsDisconnectView,
    GoogleDocsConnectView, GoogleDocsCallbackView, GoogleDocsStatusView, GoogleDocsSyncView, GoogleDocsCreateDocView, GoogleDocsDisconnectView,
    GoogleSlidesConnectView, GoogleSlidesCallbackView, GoogleSlidesStatusView, GoogleSlidesSyncView, GoogleSlidesCreatePresentationView, GoogleSlidesDisconnectView,
    PublicCalendarSlotsView, PublicCalendarBookView
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
router.register(r'team/projects', ProjectViewSet, basename='team-project')
router.register(r'team/tasks', TaskViewSet, basename='team-task')
router.register(r'team/attendance', AttendanceViewSet, basename='team-attendance')
router.register(r'team/leaves', LeaveRequestViewSet, basename='team-leave')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('team/invites/', TeamInviteView.as_view(), name='team-invites'),
    path('team/chat/', TeamChatView.as_view(), name='team-chat'),
    path('team/reports/', WorkReportView.as_view(), name='team-reports'),
    path('team/approvals/', WorkApprovalView.as_view(), name='team-approvals'),
    path('team/channels/', TeamChannelView.as_view(), name='team-channels'),
    path('team/channel-messages/', TeamChatMessageView.as_view(), name='team-channel-messages'),
    path('team/analytics/', TeamAnalyticsView.as_view(), name='team-analytics'),
    path('team/ai-copilot/', TeamAICopilotView.as_view(), name='team-ai-copilot'),
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/google-login', GoogleLoginView.as_view(), name='google-login'),
    path('auth/google-client-id', GoogleClientIdView.as_view(), name='google-client-id'),
    path('auth/gmail/connect', GmailConnectView.as_view(), name='gmail-connect'),
    path('auth/gmail/callback', GmailCallbackView.as_view(), name='gmail-callback'),
    path('auth/google-calendar/connect', GoogleCalendarConnectView.as_view(), name='google-calendar-connect'),
    path('auth/google-calendar/callback', GoogleCalendarCallbackView.as_view(), name='google-calendar-callback'),
    path('auth/gmail/sync', GmailSyncView.as_view(), name='gmail-sync'),
    path('auth/firebase-login', FirebaseLoginView.as_view(), name='firebase-login'),
    path('auth/forgot-password/send-otp', ForgotPasswordSendOTPView.as_view(), name='forgot-password-send-otp'),
    path('auth/forgot-password/verify-otp', ForgotPasswordVerifyOTPView.as_view(), name='forgot-password-verify-otp'),
    path('auth/forgot-password/reset', ForgotPasswordResetView.as_view(), name='forgot-password-reset'),
    path('auth/whatsapp/embedded-signup', WhatsAppEmbeddedSignupView.as_view(), name='whatsapp-embedded-signup'),
    path('auth/instagram/embedded-signup', InstagramEmbeddedSignupView.as_view(), name='instagram-embedded-signup'),
    path('auth/facebook/embedded-signup', FacebookEmbeddedSignupView.as_view(), name='facebook-embedded-signup'),
    path('auth/instagram/oauth-callback', InstagramOAuthCallbackView.as_view(), name='instagram-oauth-callback'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('profile/', ProfileView.as_view()),
    path('media-proxy/', MediaProxyView.as_view(), name='media-proxy'),
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
    path('webhook/facebook-instagram', FacebookInstagramWebhookView.as_view(), name='facebook-instagram-webhook'),
    # RAG Knowledge Base
    path('knowledge/', KnowledgeBaseView.as_view(), name='knowledge-base'),
    path('knowledge/<str:pk>/', KnowledgeBaseView.as_view(), name='knowledge-base-detail'),
    path('admin/impersonate', AdminImpersonateView.as_view(), name='admin-impersonate'),
    # Razorpay / Cashfree Payments
    path('payments/create-order', CreatePaymentOrderView.as_view(), name='payment-create-order'),
    path('payments/verify-order', VerifyPaymentView.as_view(), name='payment-verify-order'),
    path('payments/history', PaymentHistoryView.as_view(), name='payment-history'),
    path('payments/webhook', RazorpayWebhookView.as_view(), name='payment-webhook'),
<<<<<<< HEAD
    # OneDrive Integration
    path('onedrive/connect', OneDriveConnectView.as_view(), name='onedrive-connect'),
    path('onedrive/connect/', OneDriveConnectView.as_view()),
    path('onedrive/callback', OneDriveCallbackView.as_view(), name='onedrive-callback'),
    path('onedrive/callback/', OneDriveCallbackView.as_view()),
    path('onedrive/status', OneDriveStatusView.as_view(), name='onedrive-status'),
    path('onedrive/status/', OneDriveStatusView.as_view()),
    path('onedrive/sync', OneDriveSyncView.as_view(), name='onedrive-sync'),
    path('onedrive/sync/', OneDriveSyncView.as_view()),
    path('onedrive/disconnect', OneDriveDisconnectView.as_view(), name='onedrive-disconnect'),
    path('onedrive/disconnect/', OneDriveDisconnectView.as_view()),
    # Google Calendar Integration
    path('google-calendar/connect', GoogleCalendarConnectView.as_view(), name='gcal-connect'),
    path('google-calendar/connect/', GoogleCalendarConnectView.as_view()),
    path('google-calendar/callback', GoogleCalendarCallbackView.as_view(), name='gcal-callback'),
    path('google-calendar/callback/', GoogleCalendarCallbackView.as_view()),
    path('google-calendar/status', GoogleCalendarStatusView.as_view(), name='gcal-status'),
    path('google-calendar/status/', GoogleCalendarStatusView.as_view()),
    path('google-calendar/sync', GoogleCalendarSyncView.as_view(), name='gcal-sync'),
    path('google-calendar/sync/', GoogleCalendarSyncView.as_view()),
    path('google-calendar/create-event', GoogleCalendarCreateEventView.as_view(), name='gcal-create-event'),
    path('google-calendar/create-event/', GoogleCalendarCreateEventView.as_view()),
    path('google-calendar/disconnect', GoogleCalendarDisconnectView.as_view(), name='gcal-disconnect'),
    path('google-calendar/disconnect/', GoogleCalendarDisconnectView.as_view()),
    # Google Sheets Integration
    path('google-sheets/connect', GoogleSheetsConnectView.as_view(), name='gsheets-connect'),
    path('google-sheets/connect/', GoogleSheetsConnectView.as_view()),
    path('google-sheets/callback', GoogleSheetsCallbackView.as_view(), name='gsheets-callback'),
    path('google-sheets/callback/', GoogleSheetsCallbackView.as_view()),
    path('google-sheets/status', GoogleSheetsStatusView.as_view(), name='gsheets-status'),
    path('google-sheets/status/', GoogleSheetsStatusView.as_view()),
    path('google-sheets/sync', GoogleSheetsSyncView.as_view(), name='gsheets-sync'),
    path('google-sheets/sync/', GoogleSheetsSyncView.as_view()),
    path('google-sheets/append-row', GoogleSheetsAppendRowView.as_view(), name='gsheets-append-row'),
    path('google-sheets/append-row/', GoogleSheetsAppendRowView.as_view()),
    path('google-sheets/disconnect', GoogleSheetsDisconnectView.as_view(), name='gsheets-disconnect'),
    path('google-sheets/disconnect/', GoogleSheetsDisconnectView.as_view()),
    # Google Docs Integration
    path('google-docs/connect', GoogleDocsConnectView.as_view(), name='gdocs-connect'),
    path('google-docs/connect/', GoogleDocsConnectView.as_view()),
    path('google-docs/callback', GoogleDocsCallbackView.as_view(), name='gdocs-callback'),
    path('google-docs/callback/', GoogleDocsCallbackView.as_view()),
    path('google-docs/status', GoogleDocsStatusView.as_view(), name='gdocs-status'),
    path('google-docs/status/', GoogleDocsStatusView.as_view()),
    path('google-docs/sync', GoogleDocsSyncView.as_view(), name='gdocs-sync'),
    path('google-docs/sync/', GoogleDocsSyncView.as_view()),
    path('google-docs/create-doc', GoogleDocsCreateDocView.as_view(), name='gdocs-create-doc'),
    path('google-docs/create-doc/', GoogleDocsCreateDocView.as_view()),
    path('google-docs/disconnect', GoogleDocsDisconnectView.as_view(), name='gdocs-disconnect'),
    path('google-docs/disconnect/', GoogleDocsDisconnectView.as_view()),
    # Google Slides Integration
    path('google-slides/connect', GoogleSlidesConnectView.as_view(), name='gslides-connect'),
    path('google-slides/connect/', GoogleSlidesConnectView.as_view()),
    path('google-slides/callback', GoogleSlidesCallbackView.as_view(), name='gslides-callback'),
    path('google-slides/callback/', GoogleSlidesCallbackView.as_view()),
    path('google-slides/status', GoogleSlidesStatusView.as_view(), name='gslides-status'),
    path('google-slides/status/', GoogleSlidesStatusView.as_view()),
    path('google-slides/sync', GoogleSlidesSyncView.as_view(), name='gslides-sync'),
    path('google-slides/sync/', GoogleSlidesSyncView.as_view()),
    path('google-slides/create-presentation', GoogleSlidesCreatePresentationView.as_view(), name='gslides-create-presentation'),
    path('google-slides/create-presentation/', GoogleSlidesCreatePresentationView.as_view()),
    path('google-slides/disconnect', GoogleSlidesDisconnectView.as_view(), name='gslides-disconnect'),
    path('google-slides/disconnect/', GoogleSlidesDisconnectView.as_view()),
    
    # Public endpoints
    path('public/calendar/<str:client_id>/slots', PublicCalendarSlotsView.as_view(), name='public-calendar-slots'),
    path('public/calendar/<str:client_id>/book', PublicCalendarBookView.as_view(), name='public-calendar-book'),
]

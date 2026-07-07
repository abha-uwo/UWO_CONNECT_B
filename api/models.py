from django.db import models
from django.contrib.auth.models import AbstractUser

class Client(models.Model):
    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('GROWTH', 'Growth'),
        ('ENTERPRISE', 'Enterprise'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('TRIAL', 'Trial'),
    ]
    business_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    automation_enabled = models.BooleanField(default=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='FREE')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Enablement Flags
    facebook_enabled = models.BooleanField(default=False)
    instagram_enabled = models.BooleanField(default=False)
    
    # WhatsApp Config
    whatsapp_access_token = models.TextField(null=True, blank=True)
    whatsapp_phone_number_id = models.CharField(max_length=100, null=True, blank=True)
    whatsapp_waba_id = models.CharField(max_length=100, null=True, blank=True)
    whatsapp_verify_token = models.CharField(max_length=100, null=True, blank=True)
    
    # Global Greeting Message
    greeting_enabled = models.BooleanField(default=False)
    greeting_message = models.TextField(null=True, blank=True)
    greeting_buttons = models.JSONField(default=list, blank=True)
    
    # AI Assistant Config
    ai_enabled = models.BooleanField(default=False)
    ai_context = models.TextField(null=True, blank=True) # Description of business/platform for the AI
    
    # Config as JSON
    facebook_config = models.JSONField(default=dict, blank=True)
    instagram_config = models.JSONField(default=dict, blank=True)
    settings = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CLIENT', 'Client'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    def __str__(self):
        return f"{self.username} ({self.role})"

class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} - {self.otp}"

class Automation(models.Model):
    TRIGGER_CHOICES = [
        ('KEYWORD', 'Keyword'),
        ('START_CHAT', 'Start Chat'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='automations')
    name = models.CharField(max_length=255)
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='KEYWORD')
    keywords = models.JSONField(default=list, blank=True)
    response = models.TextField()
    buttons = models.JSONField(default=list, blank=True) # Optional buttons (max 3)
    channels = models.JSONField(default=list, blank=True)  # e.g., ["WHATSAPP"]
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Workflow(models.Model):
    TRIGGER_CHOICES = [
        ('KEYWORD', 'Keyword'),
        ('NEW_CHAT', 'New Chat'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='workflows')
    name = models.CharField(max_length=255)
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_CHOICES, default='KEYWORD')
    trigger_value = models.JSONField(default=list, blank=True)
    steps = models.JSONField(default=list)  # List of step dicts
    channels = models.JSONField(default=list, blank=True)  # e.g., ["WHATSAPP"]
    category = models.CharField(max_length=100, default='General')
    industry = models.CharField(max_length=100, default='None')
    version = models.CharField(max_length=20, default='1.0')
    is_shared = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WorkflowSession(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='workflow_sessions')
    phone_number = models.CharField(max_length=50) # The customer's WhatsApp number
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='sessions')
    current_node_id = models.CharField(max_length=255)
    variables = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    CHANNEL_CHOICES = [
        ('WHATSAPP', 'WhatsApp'),
        ('FACEBOOK', 'Facebook'),
        ('INSTAGRAM', 'Instagram'),
    ]
    TYPE_CHOICES = [
        ('INCOMING', 'Incoming'),
        ('OUTGOING', 'Outgoing'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('RECEIVED', 'Received'),
        ('FAILED', 'Failed'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='messages')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    from_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)
    body = models.TextField()
    message_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    whatsapp_message_id = models.CharField(max_length=255, null=True, blank=True)
    meta_message_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Log(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    action = models.CharField(max_length=255)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class GlobalSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    file = models.FileField(upload_to='legal/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key


def client_directory_path(instance, filename):
    return f'knowledge/client_{instance.client.id}/{filename}'

class KnowledgeDocument(models.Model):
    """
    RAG Knowledge Base — Client ke business documents store hote hain.
    AI sirf inhi documents ke basis pe jawab deta hai.
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='knowledge_docs')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=client_directory_path, null=True, blank=True)
    extracted_text = models.TextField(blank=True, default='')
    file_type = models.CharField(max_length=20, blank=True, default='')  # pdf, docx, txt
    file_size = models.IntegerField(default=0)  # bytes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.business_name} — {self.title}"


class KnowledgeChunk(models.Model):
    """
    Document ka ek chunk — embedding ke saath stored.
    Har document multiple chunks mein split hota hai for accurate RAG retrieval.
    """
    document = models.ForeignKey(KnowledgeDocument, on_delete=models.CASCADE, related_name='chunks')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='knowledge_chunks')
    chunk_text = models.TextField()  # 500-800 word chunk
    chunk_index = models.IntegerField(default=0)  # Order in the document
    embedding = models.JSONField(default=list, blank=True)  # OpenAI embedding vector (1536 dims)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['document', 'chunk_index']

    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.document.title}"

class Contact(models.Model):
    STAGE_CHOICES = [
        ('NEW', 'New Lead'),
        ('FOLLOWUP', 'Follow Up'),
        ('NEGOTIATION', 'Negotiation'),
        ('WON', 'Closed Won'),
        ('LOST', 'Closed Lost'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    platform_id = models.CharField(max_length=255, help_text="WhatsApp ID, IG SID, or FB PSID")
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='NEW')
    tags = models.JSONField(default=list, blank=True)
    notes = models.TextField(null=True, blank=True)
    bot_paused = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('client', 'platform_id')

    def __str__(self):
        return f"{self.name or self.platform_id} ({self.client.business_name})"

class Template(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=50, default='en_US')
    category = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, default='PENDING') # APPROVED, REJECTED, etc.
    components = models.JSONField(default=list) # The template structure
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.language})"

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENDING', 'Sending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=255)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True)
    audience_filter = models.CharField(max_length=50, default='ALL') # 'ALL', 'NEW', 'WON', etc.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total_sent = models.IntegerField(default=0)
    total_delivered = models.IntegerField(default=0)
    total_read = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

class SupportMessage(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='support_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Support Message from {self.sender.username} ({self.client.business_name}) at {self.created_at}"

class AuditLog(models.Model):
    admin_name = models.CharField(max_length=255)
    client_name = models.CharField(max_length=255)
    module = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    before_value = models.TextField(null=True, blank=True)
    after_value = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.created_at}] {self.admin_name} -> {self.client_name}: {self.action} on {self.module}"


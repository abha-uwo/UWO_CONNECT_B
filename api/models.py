from django.db import models
from django.contrib.auth.models import AbstractUser

class Client(models.Model):
    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('STARTER', 'Starter'),
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
    gmail_enabled = models.BooleanField(default=False)
    
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
    whatsapp_config = models.JSONField(default=dict, blank=True)
    gmail_config = models.JSONField(default=dict, blank=True)
    settings = models.JSONField(default=dict, blank=True)
    
    # Enterprise Features
    api_key = models.CharField(max_length=100, null=True, blank=True, unique=True)
    white_label_name = models.CharField(max_length=100, null=True, blank=True)
    white_label_domain = models.CharField(max_length=100, null=True, blank=True)
    white_label_logo = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CLIENT', 'Client'),
        ('AGENT', 'Agent'),
    ]
    ENTERPRISE_ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('ORG_ADMIN', 'Organization Admin'),
        ('HR', 'HR Manager'),
        ('MANAGER', 'Manager'),
        ('TEAM_LEAD', 'Team Lead'),
        ('EMPLOYEE', 'Employee'),
        ('INTERN', 'Intern'),
        ('GUEST', 'Guest'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUSPENDED', 'Suspended'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    enterprise_role = models.CharField(max_length=30, choices=ENTERPRISE_ROLE_CHOICES, default='EMPLOYEE')
    department = models.CharField(max_length=100, default='General', blank=True)
    designation = models.CharField(max_length=100, default='Team Member', blank=True)
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    permissions = models.JSONField(default=list, blank=True)
    is_online = models.BooleanField(default=False)
    last_active_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.enterprise_role or self.role})"

class TeamInvite(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='team_invites')
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    permissions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Invite for {self.email} to {self.client.business_name}"

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
        ('GMAIL', 'Gmail'),
    ]
    TYPE_CHOICES = [
        ('INCOMING', 'Incoming'),
        ('OUTGOING', 'Outgoing'),
        ('INTERNAL', 'Internal Note'),
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
    is_archived = models.BooleanField(default=False)
    snoozed_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('client', 'platform_id')

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            try:
                from .utils.sheets_utils import sync_lead_to_google_sheet
                sync_lead_to_google_sheet(self.client, self)
            except Exception as e:
                print(f"[Sheets Async Trigger Error] {str(e)}")

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

class TeamMessage(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='team_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_team_messages')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"From {self.sender.username}: {self.body[:20]}"


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


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('PHYSICAL', 'Physical Product'),
        ('DIGITAL', 'Digital Product'),
        ('BOOK', 'Book / E-Book'),
        ('SERVICE', 'Service'),
        ('OTHER', 'Other'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='PHYSICAL')
    description = models.TextField(null=True, blank=True)
    image_url = models.CharField(max_length=500, null=True, blank=True)
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='orders')
    items = models.JSONField(default=list)  # Jisme array of dicts ho: [{'product_id': '...', 'name': '...', 'price': 100, 'quantity': 1}]
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(choices=STATUS_CHOICES, default='PENDING', max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} for {self.contact.name or self.contact.phone_number}"


class PaymentOrder(models.Model):
    PLAN_CHOICES = [
        ('STARTER', 'Starter'),
        ('GROWTH', 'Growth'),
        ('ENTERPRISE', 'Enterprise'),
    ]
    CYCLE_CHOICES = [
        ('MONTHLY', 'Monthly'),
        ('ANNUAL', 'Annual'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payment_orders')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_orders')
    order_id = models.CharField(max_length=100, unique=True)
    payment_session_id = models.TextField(null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    billing_cycle = models.CharField(max_length=10, choices=CYCLE_CHOICES, default='MONTHLY')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    cf_payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PaymentOrder {self.order_id} - {self.client.business_name} ({self.status})"


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('UNDER_REVIEW', 'Under Review'),
        ('WAITING_APPROVAL', 'Waiting Approval'),
        ('BLOCKED', 'Blocked'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='NOT_STARTED')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    assigned_to = models.ManyToManyField(User, related_name='assigned_tasks', blank=True)
    department = models.CharField(max_length=100, default='General', blank=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.FloatField(default=0.0)
    spent_hours = models.FloatField(default=0.0)
    progress_percentage = models.IntegerField(default=0)
    milestone_name = models.CharField(max_length=100, blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    checklist = models.JSONField(default=list, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task #{self.id} - {self.title} [{self.status}]"


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_comments')
    text = models.TextField()
    attachments = models.JSONField(default=list, blank=True)
    mentions = models.JSONField(default=list, blank=True)
    parent_comment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    is_pinned = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Task #{self.task.id}"


class WorkReport(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='work_reports')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_reports')
    report_date = models.DateField()
    todays_work = models.TextField()
    completed_work = models.TextField(blank=True, null=True)
    remaining_work = models.TextField(blank=True, null=True)
    blockers = models.TextField(blank=True, null=True)
    need_help = models.BooleanField(default=False)
    next_steps = models.TextField(blank=True, null=True)
    hours_worked = models.FloatField(default=8.0)
    attachments = models.JSONField(default=list, blank=True)
    ai_summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.report_date} - {self.employee.username}"


class WorkApproval(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('CHANGES_REQUESTED', 'Changes Requested'),
        ('REJECTED', 'Rejected'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='approvals')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_approvals')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_approvals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    submission_notes = models.TextField(blank=True, null=True)
    feedback_notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Approval #{self.id} for Task #{self.task.id} - {self.status}"


class TeamChannel(models.Model):
    TYPE_CHOICES = [
        ('PUBLIC', 'Public Channel'),
        ('PRIVATE', 'Private Channel'),
        ('DIRECT', 'Direct Message'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='team_channels')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    channel_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='PUBLIC')
    members = models.ManyToManyField(User, related_name='team_channels', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_channels')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"#{self.name} ({self.channel_type})"


class TeamChatMessage(models.Model):
    channel = models.ForeignKey(TeamChannel, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_chat_messages')
    text = models.TextField()
    attachments = models.JSONField(default=list, blank=True)
    reactions = models.JSONField(default=dict, blank=True)
    mentions = models.JSONField(default=list, blank=True)
    is_pinned = models.BooleanField(default=False)
    is_announcement = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg in #{self.channel.name} by {self.sender.username}"




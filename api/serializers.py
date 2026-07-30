from rest_framework import serializers
from .models import User, Client, Automation, Workflow, GlobalSetting, Contact, Template, Campaign, SupportMessage, AuditLog, TeamInvite, KnowledgeDocument, TeamMessage, Product, Order, Task, TaskComment, WorkReport, WorkApproval, TeamChannel, TeamChatMessage
from .repositories.contact_repository import ContactRepository
from .repositories.workflow_repository import WorkflowRepository
from .repositories.automation_repository import AutomationRepository
from .repositories.user_repository import UserRepository
from .repositories.team_invite_repository import TeamInviteRepository
from .repositories.client_repository import ClientRepository

class ObjectIdField(serializers.Field):
    """
    Custom field that serializes MongoDB ObjectId to a plain string
    and deserializes a string back to an ObjectId-compatible value.
    """
    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        return data


class ClientSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    _id = serializers.SerializerMethodField()
    total_contacts = serializers.SerializerMethodField()
    total_workflows = serializers.SerializerMethodField()
    total_bots = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = '__all__'

    def get__id(self, obj):
        return str(obj.id)

    def get_total_contacts(self, obj):
        from .models import Contact
        return ContactRepository.filter_contacts(client=obj).count()

    def get_total_workflows(self, obj):
        from .models import Workflow
        return WorkflowRepository.filter_workflows(client=obj).count()

    def get_total_bots(self, obj):
        from .models import Automation
        return AutomationRepository.filter_automations(client=obj).count()


class UserSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)
    name = serializers.CharField(source='first_name', required=False)
    reporting_manager_name = serializers.ReadOnlyField(source='reporting_manager.username')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'first_name', 'role', 'enterprise_role', 'department', 'designation', 'reporting_manager', 'reporting_manager_name', 'status', 'client', 'permissions', 'is_online', 'last_active_at')
        extra_kwargs = {'password': {'write_only': True}}

class TeamInviteSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)

    class Meta:
        model = TeamInvite
        fields = '__all__'
        read_only_fields = ('client', 'token', 'created_at', 'is_used')


class AutomationSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)

    class Meta:
        model = Automation
        fields = '__all__'
        read_only_fields = ('client',)


class WorkflowSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)

    class Meta:
        model = Workflow
        fields = '__all__'
        read_only_fields = ('client',)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField()
    businessName = serializers.CharField(required=False, allow_blank=True)
    invite_token = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        email = value.lower().strip()
        if UserRepository.filter_users(email=email).exists() or UserRepository.filter_users(username=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def create(self, validated_data):
        email = validated_data['email'].lower().strip()
        business_name = validated_data.get('businessName', f"{validated_data['name']}'s Business")
        invite_token = validated_data.get('invite_token')

        if invite_token:
            from django.utils import timezone
            invite = TeamInviteRepository.filter_teaminvites(
                token=invite_token, 
                is_used=False, 
                expires_at__gt=timezone.now()
            ).first()
            
            if not invite:
                raise serializers.ValidationError({"invite_token": "Invalid or expired invite token."})
                
            user = User.objects.create_user(
                username=email,
                email=email,
                password=validated_data['password'],
                first_name=validated_data['name'],
                role='AGENT',
                status='APPROVED',
                client=invite.client,
                permissions=invite.permissions
            )
            
            invite.is_used = True
            invite.save()
            return user
        else:
            client = Client.objects.create(business_name=business_name)
    
            user = User.objects.create_user(
                username=email,
                email=email,
                password=validated_data['password'],
                first_name=validated_data['name'],
                role='CLIENT',
                status='PENDING',
                client=client
            )
            return user


class GlobalSettingSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)

    class Meta:
        model = GlobalSetting
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('client', 'created_at', 'updated_at')

class TemplateSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)

    class Meta:
        model = Template
        fields = '__all__'
        read_only_fields = ('client', 'created_at', 'updated_at')

class CampaignSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)
    template = ObjectIdField(read_only=True)

    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ('client', 'created_at', 'updated_at')

class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)
    
    class Meta:
        model = KnowledgeDocument
        fields = '__all__'
        read_only_fields = ('client', 'uploaded_at', 'status')

class SupportMessageSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)
    sender = ObjectIdField(read_only=True)
    sender_name = serializers.ReadOnlyField(source='sender.username')
    sender_role = serializers.ReadOnlyField(source='sender.role')

    class Meta:
        model = SupportMessage
        fields = '__all__'
        read_only_fields = ('sender', 'client')

class AuditLogSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'

class TeamMessageSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)
    sender = ObjectIdField(read_only=True)
    sender_name = serializers.ReadOnlyField(source='sender.username')
    sender_role = serializers.ReadOnlyField(source='sender.role')

    class Meta:
        model = TeamMessage
        fields = '__all__'
        read_only_fields = ('sender', 'client', 'created_at')


class ProductSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('client',)


class OrderSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)
    contact_name = serializers.ReadOnlyField(source='contact.name')
    contact_phone = serializers.ReadOnlyField(source='contact.phone_number')

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('client',)


class TaskCommentSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    author_name = serializers.ReadOnlyField(source='author.username')
    author_role = serializers.ReadOnlyField(source='author.enterprise_role')

    class Meta:
        model = TaskComment
        fields = '__all__'
        read_only_fields = ('author', 'created_at')


class TaskSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    comments = TaskCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('client', 'created_by', 'created_at', 'updated_at')


class WorkReportSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)
    employee_name = serializers.ReadOnlyField(source='employee.username')
    employee_department = serializers.ReadOnlyField(source='employee.department')

    class Meta:
        model = WorkReport
        fields = '__all__'
        read_only_fields = ('client', 'employee', 'created_at')


class WorkApprovalSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    task_title = serializers.ReadOnlyField(source='task.title')
    employee_name = serializers.ReadOnlyField(source='employee.username')
    reviewer_name = serializers.ReadOnlyField(source='reviewer.username')

    class Meta:
        model = WorkApproval
        fields = '__all__'
        read_only_fields = ('employee', 'submitted_at', 'reviewed_at')


class TeamChannelSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = TeamChannel
        fields = '__all__'
        read_only_fields = ('client', 'created_by', 'created_at')

    def get_member_count(self, obj):
        return obj.members.count()


class TeamChatMessageSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    sender_name = serializers.ReadOnlyField(source='sender.username')
    sender_role = serializers.ReadOnlyField(source='sender.enterprise_role')

    class Meta:
        model = TeamChatMessage
        fields = '__all__'
        read_only_fields = ('sender', 'created_at')


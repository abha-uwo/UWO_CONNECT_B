from rest_framework import serializers
from .models import User, Client, Automation, Workflow, GlobalSetting, Contact, Template, Campaign, SupportMessage, AuditLog


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
        return Contact.objects.filter(client=obj).count()

    def get_total_workflows(self, obj):
        from .models import Workflow
        return Workflow.objects.filter(client=obj).count()

    def get_total_bots(self, obj):
        from .models import Automation
        return Automation.objects.filter(client=obj).count()


class UserSerializer(serializers.ModelSerializer):
    id = ObjectIdField(read_only=True)
    client = ObjectIdField(read_only=True)
    name = serializers.CharField(source='first_name', required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'first_name', 'role', 'status', 'client')
        extra_kwargs = {'password': {'write_only': True}}


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
    businessName = serializers.CharField(required=False)

    def validate_email(self, value):
        email = value.lower().strip()
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def create(self, validated_data):
        email = validated_data['email'].lower().strip()
        business_name = validated_data.get('businessName', f"{validated_data['name']}'s Business")

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

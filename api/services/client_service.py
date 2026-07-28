from ..models import Client, User, Workflow
from ..repositories.user_repository import UserRepository
from ..repositories.workflow_repository import WorkflowRepository

class ClientService:
    @staticmethod
    def suspend_client(request, client_obj):
        from .admin_service import AdminService
        before_status = client_obj.status
        client_obj.status = 'SUSPENDED'
        client_obj.save()
        UserRepository.filter_users(client=client_obj).update(status='SUSPENDED')
        AdminService.log_admin_action(request, client_obj, 'Client Management', 'SUSPEND_CLIENT', before_value=before_status, after_value='SUSPENDED')
        return {"status": "suspended"}

    @staticmethod
    def reactivate_client(request, client_obj):
        from .admin_service import AdminService
        before_status = client_obj.status
        client_obj.status = 'ACTIVE'
        client_obj.save()
        UserRepository.filter_users(client=client_obj).update(status='APPROVED')
        AdminService.log_admin_action(request, client_obj, 'Client Management', 'REACTIVATE_CLIENT', before_value=before_status, after_value='ACTIVE')
        return {"status": "active"}

    @staticmethod
    def disconnect_meta(request, client_obj):
        from .admin_service import AdminService
        before_val = f"Token ID: {client_obj.whatsapp_phone_number_id}"
        client_obj.whatsapp_access_token = None
        client_obj.whatsapp_phone_number_id = None
        client_obj.whatsapp_waba_id = None
        client_obj.facebook_enabled = False
        client_obj.instagram_enabled = False
        client_obj.facebook_config = {}
        client_obj.instagram_config = {}
        client_obj.save()
        AdminService.log_admin_action(request, client_obj, 'Integrations', 'DISCONNECT_META', before_value=before_val, after_value="Disconnected")
        return {"status": "disconnected"}

    @staticmethod
    def reset_ai(request, client_obj):
        from .admin_service import AdminService
        before_val = f"AI Context: {client_obj.ai_context}"
        client_obj.ai_enabled = False
        client_obj.ai_context = None
        client_obj.save()
        AdminService.log_admin_action(request, client_obj, 'AI Settings', 'RESET_AI_SETTINGS', before_value=before_val, after_value="Reset")
        return {"status": "reset"}

    @staticmethod
    def reset_workflows(request, client_obj):
        from .admin_service import AdminService
        count = WorkflowRepository.filter_workflows(client=client_obj).count()
        WorkflowRepository.filter_workflows(client=client_obj).delete()
        AdminService.log_admin_action(request, client_obj, 'Workflows', 'RESET_WORKFLOWS', before_value=f"Total: {count}", after_value="0 Workflows")
        return {"status": "reset"}

    @staticmethod
    def toggle_feature(request, client_obj, feature):
        from .admin_service import AdminService
        if not feature:
            return {"error": "Feature name is required", "status_code": 400}
        
        if not isinstance(client_obj.settings, dict):
            client_obj.settings = {}
            
        before_val = client_obj.settings.get(feature, False)
        target_val = not before_val
        client_obj.settings[feature] = target_val
        client_obj.save()
        AdminService.log_admin_action(request, client_obj, 'Override Settings', f'TOGGLE_{feature.upper()}', before_value=str(before_val), after_value=str(target_val))
        return {"status": "toggled", "value": target_val, "status_code": 200}

from ..models import Log, AuditLog, GlobalSetting

class SystemRepository:
    @staticmethod
    def get_global_setting(key):
        return GlobalSetting.objects.filter(key=key).first()
        
    @staticmethod
    def create_audit_log(**kwargs):
        return AuditLog.objects.create(**kwargs)
        
    @staticmethod
    def filter_audit_logs(**kwargs):
        return AuditLog.objects.filter(**kwargs)

    @staticmethod
    def filter_globalsettings(**kwargs):
        return GlobalSetting.objects.filter(**kwargs)

    @staticmethod
    def get_all_globalsettings():
        return GlobalSetting.objects.all()

    @staticmethod
    def get_all():
        return GlobalSetting.objects.all()

    @staticmethod
    def get_all_auditlogs():
        return AuditLog.objects.all()

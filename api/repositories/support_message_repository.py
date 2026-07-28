from ..models import SupportMessage

class SupportMessageRepository:
    @staticmethod
    def get_supportmessage(id):
        return SupportMessage.objects.filter(id=id).first()

    @staticmethod
    def filter_supportmessages(**kwargs):
        return SupportMessage.objects.filter(**kwargs)

    @staticmethod
    def get_all_supportmessages():
        return SupportMessage.objects.all()

    @staticmethod
    def get_all():
        return SupportMessage.objects.all()

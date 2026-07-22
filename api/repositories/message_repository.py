from ..models import Message, SupportMessage, TeamMessage

class MessageRepository:
    @staticmethod
    def filter_messages(**kwargs):
        return Message.objects.filter(**kwargs)

    @staticmethod
    def get_message(id):
        return Message.objects.filter(id=id).first()
        
    @staticmethod
    def create_message(**kwargs):
        return Message.objects.create(**kwargs)

class SupportMessageRepository:
    @staticmethod
    def filter_messages(**kwargs):
        return SupportMessage.objects.filter(**kwargs)
        
    @staticmethod
    def create_message(**kwargs):
        return SupportMessage.objects.create(**kwargs)

class TeamMessageRepository:
    @staticmethod
    def filter_messages(**kwargs):
        return TeamMessage.objects.filter(**kwargs)
        
    @staticmethod
    def create_message(**kwargs):
        return TeamMessage.objects.create(**kwargs)

    @staticmethod
    def get_all_messages():
        return Message.objects.all()

    @staticmethod
    def get_all():
        return Message.objects.all()

from ..models import TeamMessage

class TeamMessageRepository:
    @staticmethod
    def get_teammessage(id):
        return TeamMessage.objects.filter(id=id).first()

    @staticmethod
    def create_teammessage(**kwargs):
        return TeamMessage.objects.create(**kwargs)

    @staticmethod
    def filter_teammessages(**kwargs):
        return TeamMessage.objects.filter(**kwargs)

    @staticmethod
    def get_all_teammessages():
        return TeamMessage.objects.all()

    @staticmethod
    def get_all():
        return TeamMessage.objects.all()

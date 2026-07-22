from ..models import TeamInvite

class TeamInviteRepository:
    @staticmethod
    def get_teaminvite(id, client=None):
        if client:
            return TeamInvite.objects.filter(id=id, client=client).first()
        return TeamInvite.objects.filter(id=id).first()

    @staticmethod
    def create_teaminvite(**kwargs):
        return TeamInvite.objects.create(**kwargs)

    @staticmethod
    def filter_teaminvites(**kwargs):
        return TeamInvite.objects.filter(**kwargs)

    @staticmethod
    def get_all_teaminvites():
        return TeamInvite.objects.all()

    @staticmethod
    def get_all():
        return TeamInvite.objects.all()

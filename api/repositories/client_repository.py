from ..models import Client

class ClientRepository:
    @staticmethod
    def get_client(id):
        return Client.objects.filter(id=id).first()

    @staticmethod
    def filter_clients(**kwargs):
        return Client.objects.filter(**kwargs)
        
    @staticmethod
    def get_first(**kwargs):
        return Client.objects.filter(**kwargs).first()

    @staticmethod
    def get_all_clients():
        return Client.objects.all()

    @staticmethod
    def get_all():
        return Client.objects.all()

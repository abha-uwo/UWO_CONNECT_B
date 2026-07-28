from ..models import Campaign, Template

class CampaignRepository:
    @staticmethod
    def get_campaign(id):
        return Campaign.objects.filter(id=id).first()
        
    @staticmethod
    def filter_campaigns(**kwargs):
        return Campaign.objects.filter(**kwargs)

    @staticmethod
    def create_campaign(**kwargs):
        return Campaign.objects.create(**kwargs)

class TemplateRepository:
    @staticmethod
    def filter_templates(**kwargs):
        return Template.objects.filter(**kwargs)
        
    @staticmethod
    def get_template(id, client):
        return Template.objects.filter(id=id, client=client).first()

    @staticmethod
    def get_all_campaigns():
        return Campaign.objects.all()

    @staticmethod
    def get_all():
        return Campaign.objects.all()

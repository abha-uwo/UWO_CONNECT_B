from ..models import Template

class TemplateRepository:
    @staticmethod
    def get_template(id):
        return Template.objects.filter(id=id).first()

    @staticmethod
    def filter_templates(**kwargs):
        return Template.objects.filter(**kwargs)

    @staticmethod
    def get_all_templates():
        return Template.objects.all()

    @staticmethod
    def get_all():
        return Template.objects.all()

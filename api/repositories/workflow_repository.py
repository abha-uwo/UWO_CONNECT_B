from ..models import Workflow

class WorkflowRepository:
    @staticmethod
    def get_workflow(id):
        return Workflow.objects.filter(id=id).first()

    @staticmethod
    def filter_workflows(**kwargs):
        return Workflow.objects.filter(**kwargs)

    @staticmethod
    def get_all_workflows():
        return Workflow.objects.all()

    @staticmethod
    def get_all():
        return Workflow.objects.all()

from ..models import KnowledgeDocument, KnowledgeChunk

class KnowledgeRepository:
    @staticmethod
    def filter_documents(**kwargs):
        return KnowledgeDocument.objects.filter(**kwargs)
        
    @staticmethod
    def get_document(id):
        return KnowledgeDocument.objects.filter(id=id).first()

    @staticmethod
    def filter_chunks(**kwargs):
        return KnowledgeChunk.objects.filter(**kwargs)

    @staticmethod
    def create_knowledgedocument(**kwargs):
        return KnowledgeDocument.objects.create(**kwargs)

    @staticmethod
    def create_knowledgechunk(**kwargs):
        return KnowledgeChunk.objects.create(**kwargs)

    @staticmethod
    def get_all_knowledges():
        return KnowledgeDocument.objects.all()

    @staticmethod
    def get_all():
        return KnowledgeDocument.objects.all()

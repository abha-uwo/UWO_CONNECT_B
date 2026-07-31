from rest_framework.renderers import JSONRenderer
from bson import ObjectId

class MongoJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer that automatically converts MongoDB ObjectIds to strings
    during JSON serialization, preventing 'ObjectId is not JSON serializable' errors.
    """
    class MongoJSONEncoder(JSONRenderer.encoder_class):
        def default(self, obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            return super().default(obj)
            
    encoder_class = MongoJSONEncoder

from rest_framework.exceptions import APIException

class ClientSuspendedException(APIException):
    status_code = 403
    default_detail = 'Client is suspended.'
    default_code = 'client_suspended'

class InvalidTokenException(APIException):
    status_code = 401
    default_detail = 'Invalid or expired token.'
    default_code = 'invalid_token'

class BusinessRuleViolation(APIException):
    status_code = 400
    default_detail = 'Business rule violation.'
    default_code = 'business_rule_violation'

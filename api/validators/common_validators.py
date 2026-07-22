import re
from rest_framework.exceptions import ValidationError

def validate_phone_number(phone_number):
    if not re.match(r'^\+?[1-9]\d{1,14}$', phone_number):
        raise ValidationError('Invalid phone number format.')
    return phone_number

def validate_email(email):
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        raise ValidationError('Invalid email format.')
    return email

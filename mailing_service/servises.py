from rest_framework.serializers import ValidationError


def check_valid_number(number: str):
    """ Response status 400 with error messages if phone_number not valid """
    errors = []
    if number[0] != '7':
        errors.append("Phone number must start with 7")
    if not number.isdigit() or len(number) != 11:
        errors.append("Phone number must consist of 11 digits")
    if errors:
        raise ValidationError([errors])

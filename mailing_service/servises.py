import random
from celery import group
import requests

from django.conf import settings
from django.db.models import QuerySet, Q
from rest_framework.serializers import ValidationError
from .models import ClientTag, OperatorCode, Mailing, Client


def check_valid_number(number: str):
    """ Response status 400 with error messages if phone_number not valid """
    errors = []
    if number[0] != '7':
        errors.append("Phone number must start with 7")
    if not number.isdigit() or len(number) != 11:
        errors.append("Phone number must consist of 11 digits")
    if errors:
        raise ValidationError([errors])


def create_related_if_not_exist(initial_data: dict) -> None:
    """ Create non-existent tag and operator_code with passed data
        before update/create related models. """
    if tag_data := initial_data.get("tag"):
        ClientTag.objects.get_or_create(tag=tag_data)
    if operator_code_data := initial_data.get("operator_code"):
        OperatorCode.objects.get_or_create(code=operator_code_data)


def get_clients_from_mailing(mailing: Mailing) -> QuerySet[Client]:
    """ Return queryset of clients according to mailing filters.
        if both filters are empty, return all clients. """
    codes_list = mailing.filter_operator_codes.values_list('code', flat=True)
    tags_list = mailing.filter_client_tags.values_list('tag', flat=True)
    if not (codes_list or tags_list):
        return Client.objects.all()
    else:
        return Client.objects.filter(
            Q(operator_code__code__in=codes_list) |
            Q(tag__tag__in=tags_list)
        ).distinct().select_related('tag', 'operator_code')


def init_start_mailing(mailing_id: int):
    mailing = Mailing.objects.get(pk=mailing_id)
    numbers = get_clients_from_mailing(mailing).values_list('phone_number', flat=True)


def send_message(phone_number: int):
    pass


def send_request_to_external_api(message_id: int, phone_number: int, text: str):
    token = settings.API_TOKEN
    url = "https://probe.fbrq.cloud/v1/send/" + str(message_id)
    headers = {'Authorization': 'Bearer ' + token}
    data = {
        'id': message_id,
        'phone': phone_number,
        'text': text
    }

    response = requests.post(url=url, data=data, headers=headers)
    return response.status_code

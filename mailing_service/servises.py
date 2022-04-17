import json
import requests
import time
import datetime as dt
import random

from django.utils import timezone
from django.conf import settings
from django.db.models import QuerySet, Q, Count
from rest_framework.serializers import ValidationError
from celery.result import AsyncResult

from .models import Mailing, Client, Message, ClientTag, OperatorCode


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


def get_expires_seconds(mailing_id: int):
    """ Return expires option to celery task """
    mailing = Mailing.objects.get(pk=mailing_id)
    stop_datetime = dt.datetime.combine(mailing.stop_date, mailing.stop_time)
    now = dt.datetime.now()
    return (stop_datetime - now).seconds if stop_datetime > now else 0


def get_clients_from_mailing(mailing: Mailing) -> QuerySet[Client]:
    """ Return queryset of clients according to mailing filters.
        if both filters are empty, return all clients. """
    codes_list = mailing.filter_operator_codes.values_list('code', flat=True)
    tags_list = mailing.filter_client_tags.values_list('tag', flat=True)
    if not (codes_list or tags_list):
        if settings.EMPTY_FILTERS_IN_MAILING_TO_ALL_CLIENTS:
            return Client.objects.all()
        else:
            return Client.objects.none()
    else:
        return Client.objects.filter(
            Q(operator_code__code__in=codes_list) |
            Q(tag__tag__in=tags_list)
        ).distinct().select_related('tag', 'operator_code')


def annotate_mailing_with_message_counters() -> QuerySet[Mailing]:
    """ Used with short-statistic mailing serializer """
    return Mailing.objects.annotate(
        total_message_count=Count('q_messages'),
        success_message_count=Count('q_messages', filter=Q(q_messages__status=Message.SUCCESS)),
        fail_message_count=Count('q_messages', filter=Q(q_messages__status=Message.FAULT)),
        planned_message_count=Count('q_messages', filter=Q(q_messages__status=Message.PLANNED)))


def send_planned_message(message_id: int):
    """ Send message with pk=message_id.
        Uses with celery task. """
    message = Message.objects.select_related('client', 'mailing').get(pk=message_id)
    text, phone_number = message.mailing.message, message.client.phone_number
    print(text)
    # status = send_request_to_external_api(message_id, phone_number, text)
    status = fake_request()  # to test
    message.status = status
    message.save()
    if status != Message.SUCCESS:
        raise Exception("Не успешный результат")


def get_planned_messages(mailing_id: int) -> list[int]:
    """ Return list of message's id which related with mailing(pk=mailing_id)
        with status 'Planned' """
    return list(Mailing.objects.prefetch_related('messages').get(pk=mailing_id).messages.filter(
        status=Message.PLANNED).values_list('pk', flat=True))


def create_messages_without_sending(mailing_id: int) -> None:
    """ Creates message objects to clients that match the filters
        specified in the mailing with pk=mailing_id.
        Called when creating a mailing list the api """
    mailing = Mailing.objects.get(pk=mailing_id)
    clients_info = get_clients_from_mailing(mailing).values_list('phone_number', 'pk')
    messages = []
    for number, client_id in clients_info:
        messages.append(Message(
            status=Message.PLANNED,
            mailing_id=mailing_id,
            client_id=client_id
        ))
    Message.objects.bulk_create(messages)


def send_request_to_external_api(message_id: int, phone_number: int, text: str):
    """ Sends a request to external api and return status of response """
    token = settings.API_TOKEN
    url = "https://probe.fbrq.cloud/v1/send/" + str(message_id)
    headers = {'Authorization': 'Bearer ' + token}
    data = {
        'id': message_id,
        'phone': phone_number,
        'text': text
    }

    response = requests.post(url=url, data=json.dumps(data), headers=headers)
    time.sleep(10)
    return response.status_code


def fake_request():
    """ Fake to hand testing of retrying sending"""
    time.sleep(20)
    if random.random() < 0.5:
        raise Exception("Ошибка отправления")
    return random.choice((200, 400, 400))


def start_new_mailing(response):
    from mailing_service.tasks import celery_send_all_planned_messages, celery_create_messages_without_sending

    stop_datetime = dt.datetime.fromisoformat(f"{response.data['stop_date']} {response.data['stop_time']}")
    start_datetime = dt.datetime.fromisoformat(f"{response.data['start_date']} {response.data['start_time']}")
    start_datetime = start_datetime.astimezone(timezone.get_current_timezone())
    if stop_datetime > dt.datetime.now():
        res = celery_create_messages_without_sending.apply_async(
            args=[response.data.get("id")],
            expires=stop_datetime,
            link=celery_send_all_planned_messages.signature(options={
                'eta': start_datetime
            })
        )
        mailing = Mailing.objects.get(pk=response.data["id"])
        mailing.send_all_message_task_id = res.id
        mailing.save(update_fields=('send_all_message_task_id',))


def _datetimes_changed(old_mailing: Mailing, updated_mailing: Mailing) -> bool:
    old_start_datetime = old_mailing.start_datetime
    updated_start_datetime = updated_mailing.start_datetime
    old_stop_datetime = old_mailing.stop_datetime
    updated_stop_datetime = updated_mailing.stop_datetime
    return not (old_start_datetime == updated_start_datetime and old_stop_datetime == updated_stop_datetime)


def _message_changed(old_mailing: Mailing, updated_mailing: Mailing) -> bool:
    return not (old_mailing.message == updated_mailing.message)


def _filters_changed(old_filter_client_tags,
                     old_filter_operator_codes,
                     updated_mailing: Mailing, ) -> bool:
    updated_filter_client_tags = set(updated_mailing.filter_client_tags.values_list('tag', flat=True))
    updated_filter_operator_codes = set(updated_mailing.filter_operator_codes.values_list('code', flat=True))
    return not (old_filter_operator_codes == updated_filter_operator_codes and old_filter_client_tags == updated_filter_client_tags)


def _refresh_failed_tasks(mailing_id):
    """ Used when existing mailing was changed"""
    Mailing.objects.get(pk=mailing_id).messages.filter(status=Message.FAULT).update(status=Message.PLANNED)


def _remove_all_planned_messages(mailing_id):
    """ Used when existing mailing was changed"""
    Mailing.objects.get(pk=mailing_id).messages.filter(status=Message.PLANNED).delete()


def _stop_previous_mailing(mailing_id):
    """ Used when existing mailing was changed"""
    res = AsyncResult(Mailing.objects.get(pk=mailing_id).send_all_message_task_id)
    print(repr(res))
    group = res.children[0].children[0]
    print(repr(group))
    group.revoke(terminate=True)


def update_mailing(mailing_id: int,
                   old_filter_client_tags: set[str],
                   old_filter_operator_codes: set[int],
                   old_mailing: Mailing,
                   updated_mailing: Mailing) -> None:
    filters_changed = _filters_changed(old_filter_client_tags,
                                       old_filter_operator_codes,
                                       updated_mailing)
    message_changed = _message_changed(old_mailing, updated_mailing)
    datetimes_changed = _datetimes_changed(old_mailing, updated_mailing)
    _stop_previous_mailing(mailing_id)

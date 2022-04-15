from django.db import models
from pytz import all_timezones
from datetime import time

class OperatorCode(models.Model):
    code = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.code)


class ClientTag(models.Model):
    tag = models.TextField(unique=True)

    def __str__(self):
        return self.tag


class Mailing(models.Model):
    start_date = models.DateField()
    start_time = models.TimeField(default=time(0))
    stop_date = models.DateField()
    stop_time = models.TimeField(default=time(0))
    message = models.TextField()
    filter_operator_codes = models.ManyToManyField(OperatorCode, related_name='mailings', blank=True)
    filter_client_tags = models.ManyToManyField(ClientTag, related_name='mailings', blank=True)

    class Meta:
        ordering = ['start_date', 'start_time', 'stop_date', 'stop_time']

    def __str__(self):
        return f"Mailing with start at {self.start_date} {self.start_time}, " \
               f"stop at {self.stop_date} {self.stop_time}. " \
               f"Codes: {list(self.filter_operator_codes.values_list('code', flat=True))}, " \
               f"Tags: {list(self.filter_client_tags.values_list('tag', flat=True))}"

    @property
    def numbers(self):
        from .servises import get_clients_from_mailing
        return get_clients_from_mailing(self).values_list('phone_number', flat=True)


class Client(models.Model):
    # tuple to choices in client_instance.timezone
    TZ = tuple(zip(all_timezones, all_timezones))
    default_tz = 'Europe/Moscow'

    phone_number = models.IntegerField(unique=True)
    operator_code = models.ForeignKey(OperatorCode, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ForeignKey(ClientTag, on_delete=models.SET_NULL, null=True, blank=True)

    # max_length = len(max(pytz.all_timezones, key=lambda x: len(x))) = 32
    timezone = models.CharField(max_length=32, default=default_tz, choices=TZ)

    def __str__(self):
        return f"Phone: {self.phone_number}, tag: {self.tag.tag}, operators code: {self.operator_code.code}\n"


class Message(models.Model):
    SUCCESS = 200
    FAULT = 400
    PLANNED = 100
    STATUS_CHOICES = [
        (SUCCESS, 'Success'),
        (FAULT, 'Fault'),
        (PLANNED, 'Planned')
    ]

    send_date_time = models.DateTimeField(auto_now_add=True)
    response_code = models.IntegerField(default=PLANNED, choices=STATUS_CHOICES)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='messages', related_query_name='q_messages')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='clients')

    def __str__(self):
        return f"Status: {self.get_response_code_display()}, to {self.client.phone_number}, " \
               f"send at {self.send_date_time}"


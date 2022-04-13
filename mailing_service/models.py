from django.db import models
from pytz import all_timezones


class OperatorCode(models.Model):
    code = models.IntegerField(unique=True)


class ClientTag(models.Model):
    tag = models.TextField(unique=True)


class Mailing(models.Model):
    start_date = models.DateField()
    start_time = models.TimeField()
    stop_date = models.DateField()
    stop_time = models.TimeField()
    message = models.TextField()
    filter_operator_codes = models.ManyToManyField(OperatorCode, related_name='mailings', blank=True)
    filter_client_tags = models.ManyToManyField(ClientTag, related_name='client_tags', blank=True)


class Client(models.Model):
    # tuple to choices in client_instance.timezone
    TZ = tuple(zip(all_timezones, all_timezones))
    default_tz = 'Europe/Moscow'

    phone_number = models.IntegerField(unique=True)
    operator_code = models.ForeignKey(OperatorCode, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ForeignKey(ClientTag, on_delete=models.SET_NULL, null=True, blank=True)

    # len(max(pytz.all_timezones, key=lambda x: len(x))) is 32
    timezone = models.CharField(max_length=32, default=default_tz, choices=TZ)


class Message(models.Model):
    send_date_time = models.DateTimeField(auto_now_add=True)
    response_code = models.IntegerField()
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='messages')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='clients')

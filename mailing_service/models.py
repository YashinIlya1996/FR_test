from django.db import models
from pytz import all_timezones


class Mailing(models.Model):
    start_date = models.DateField()
    start_time = models.TimeField()
    stop_date = models.DateField()
    stop_time = models.TimeField()
    message = models.TextField()
    filter_operator_codes = models.TextField()
    filter_client_tags = models.TextField()


class Client(models.Model):
    # tuple to choices in client_instance.timezone
    TZ = tuple(zip(all_timezones, all_timezones))
    default_tz = 'Europe/Moscow'

    phone_number = models.IntegerField(unique=True)
    operator_code = models.IntegerField()
    tag = models.TextField()

    # len(max(pytz.all_timezones, key=lambda x: len(x))) is 32
    timezone = models.CharField(max_length=32, default=default_tz, choices=TZ)


class Message(models.Model):
    send_date_time = models.DateTimeField(auto_now_add=True)
    response_code = models.IntegerField()
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

""" import it in app.ready to register callback functions """

from django.db.models.signals import pre_save
from django.dispatch import receiver

from mailing_service.models import Mailing
from mailing_service.servises import create_messages_without_sending


# @receiver(post_save, sender=Mailing)
# def prepare_messages(sender, **kwargs):
#     print(kwargs)
#     if kwargs.get("created"):
#         mailing = kwargs.get("instance")
#         create_messages_without_sending(mailing.pk)


# @receiver(pre_save, sender=Mailing)
# def change_send_messages_task(sender, **kwargs):
#     pk = kwargs["instance"].pk
#     mailing_from_db = Mailing.objects.get(pk=pk)
#     dt = mailing_from_db.stop_date
#     print(kwargs)


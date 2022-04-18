""" import it in app.ready to register callback functions """

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from mailing_service.models import Mailing
from mailing_service.servises import _stop_previous_mailing


@receiver(signal=pre_delete, sender=Mailing)
def delete_stop_mailing_hook(sender, **kwargs):
    instance = kwargs.get("instance")
    if instance and instance.pk is not None:
        _stop_previous_mailing(instance.pk)




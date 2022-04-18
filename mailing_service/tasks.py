from FR_test.celery import app
from celery import group, Task

from .servises import (
    create_messages_without_sending,
    send_planned_message,
    get_planned_messages,
    get_expires_seconds,
)


class BaseTaskWithRetries(Task):
    """ Settings to retry failed messages sending """
    autoretry_for = (Exception,)
    max_retries = None
    retry_backoff = 5
    retry_backoff_max = 600
    retry_jitter = True


@app.task
def celery_create_messages_without_sending(mailing_id: int, refresh_success=True):
    create_messages_without_sending(mailing_id, refresh_success)
    return mailing_id


@app.task(bind=True, base=BaseTaskWithRetries)
def celery_send_planned_message(self, message_id: int):
    send_planned_message(message_id)


@app.task(bind=True)
def celery_send_all_planned_messages(self, mailing_id: int):
    planned_messages = get_planned_messages(mailing_id)
    expires = get_expires_seconds(mailing_id)
    group([celery_send_planned_message.s(pk) for pk in planned_messages], expires=expires)()

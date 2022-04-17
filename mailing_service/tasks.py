from FR_test.celery import app
from celery import group
from .servises import (
    create_messages_without_sending,
    send_planned_message,
    get_planned_messages,
)


@app.task
def celery_create_messages_without_sending(mailing_id: int):
    create_messages_without_sending(mailing_id)
    return mailing_id


@app.task
def celery_send_planned_message(message_id: int):
    send_planned_message(message_id)


@app.task
def celery_send_all_planned_messages(mailing_id: int):
    planned_messages = get_planned_messages(mailing_id)
    group_res = group(
        celery_send_planned_message.s(pk) for pk in planned_messages
    ).apply_async()
    return group_res.id

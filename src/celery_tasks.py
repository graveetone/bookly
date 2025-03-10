from typing import List

from asgiref.sync import async_to_sync
from celery import Celery

from src.mail import mail, create_message

celery_app = Celery()

celery_app.config_from_object("src.config")


@celery_app.task
def send_email(recipients: List[str], subject: str, body: str):
    message = create_message(
        recipients=recipients,
        subject=subject,
        body=body,
    )

    async_to_sync(mail.send_message)(
        message=message
    )
    print("Email sent!")

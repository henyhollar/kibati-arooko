from huey.djhuey import task, periodic_task, crontab
from .views import message_as_sms, message_as_email

@task(retries=2, retry_delay=120)
def online_sms(data):
    message_as_sms(data)

def online_email(data):
    message_as_email(data)
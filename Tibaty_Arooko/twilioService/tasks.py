from huey.djhuey import db_task
from transaction.utils import OnlineTransfer


@db_task()
def twilio_task(data):
    OnlineTransfer(data)
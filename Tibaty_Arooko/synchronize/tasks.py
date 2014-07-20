from huey.djhuey import task, periodic_task, crontab
from .utils import Request
from pyamf import AMF3
from pyamf.remoting.client import RemotingService
from message.views import message_as_email, message_as_sms
from synchronize.models import Sync


@task(retries=5, retry_delay=60)
def task_request(obj, domain, method):
    if method == 'register':
        try:
            gw = RemotingService(domain+'sync/', amf_version=AMF3)
            service = gw.getService('SyncService')
            http_data = service.register(obj)

            return http_data
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()

    elif method == 'update_user':
        try:
            gw = RemotingService(domain+'sync/', amf_version=AMF3)
            service = gw.getService('SyncService')
            http_data = service.update_user(obj)

            return http_data
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()

    elif method == 'update_wallet':
        try:
            gw = RemotingService(domain+'sync/', amf_version=AMF3)
            service = gw.getService('SyncService')
            http_data = service.update_wallet(obj)

            return http_data
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()

    elif method == 'update_schedule':
        try:
            gw = RemotingService(domain+'sync/', amf_version=AMF3)
            service = gw.getService('SyncService')
            http_data = service.update_schedule(obj)

            return http_data
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()

    elif method == 'update_transaction':
        try:
            gw = RemotingService(domain+'sync/', amf_version=AMF3)
            service = gw.getService('SyncService')
            http_data = service.update_transaction(obj)

            return http_data
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()

    elif method == 'create_transaction':
        try:
            gw = RemotingService(domain+'sync/', amf_version=AMF3)
            service = gw.getService('SyncService')
            http_data = service.create_transaction(obj)

            return http_data
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()

    Sync.objects.filter(method=method, model_id=obj.id).update(ack=True)


@periodic_task(crontab(minute='*/1'))
def every_five_mins():
    print 'Every five minutes this will be printed by the consumer'



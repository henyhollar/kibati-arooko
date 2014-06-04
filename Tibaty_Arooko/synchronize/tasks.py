from huey.djhuey import task
from .utils import Request
from message.views import message_as_email, message_as_sms


@task(retries=5, retry_delay=60)
def task_request(obj, domain, url, method):
    if method == 'register_user':
        try:
            resp = Request(domain, url, method)
            reply = resp.data_request(data={'username': obj.username, 'obj': obj, 'id': False})
            return reply
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()

    elif method == 'update_user':
        try:
            resp = Request(domain, url, method)
            reply = resp.data_request(data={'username': obj.username, 'obj': obj, 'id': True})
            return reply
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()

    elif method == 'update_wallet':
        try:
            resp = Request(domain, url, method)
            reply = resp.data_request(data={'owner': obj.username, 'obj': obj, 'id': True})
            return reply
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()

    elif method == 'update_schedule':
        try:
            resp = Request(domain, url, method)
            reply = resp.data_request(data={'user': obj.username, 'obj': obj, 'id': True})
            return reply
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()

    elif method == 'update_transaction':
        try:
            resp = Request(domain, url, method)
            reply = resp.data_request(data={'phone_no': obj.username, 'obj': obj, 'id': True})
            return reply
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()

    elif method == 'create_transaction':
        try:
            resp = Request(domain, url, method)
            reply = resp.data_request(data={'phone_no': obj.username, 'obj': obj, 'id': False})
            return reply
        except Exception, e:
            # set the admin phone nos as global variable in the settings and make message_as_sms() loop over the nos.
            data = {'subject': 'Offline Registration Error', 'message': e, 'phone': '08137474080'}
            message_as_email(data)
        raise LookupError()
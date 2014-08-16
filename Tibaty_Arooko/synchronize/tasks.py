from huey.djhuey import task, periodic_task, crontab
from pyamf import AMF3
from pyamf.remoting.client import RemotingService
from message.views import message_as_email, message_as_sms
from .models import Sync
from scheduler.models import getSchedule

import zmq.green as zmq
from .utils import schedule, update_schedule, sync_down
from datetime import datetime
from dateutil.rrule import *


mtn = set(['0803', '0813', '0703', '0806', '0816', '0706', '0810', '0814', '0903'])
eti = set(['0818', '0809', '0819', '0817'])
zain = set(['0802', '0812', '0701', '0708', '0808'])
glo = set(['0805', '0815', '0705', '0807', '0811'])


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
            return

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
            return

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
            return

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
            return

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
            return

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
            return

    Sync.objects.filter(method=method, model_id=obj.id).update(ack=True)


@task()
def load(phone, amount, request, recipient='', retry=None):
    if request.lower() == 'normal':
        data = {'phone': phone, 'amount': amount, 'request': 'c#m'}if retry is None else {'phone': phone, 'amount': amount, 'request': 'c#m', 'retry': retry}
    elif request.lower() == 'card':
        data = {'phone': phone, 'amount': amount, 'request': 'p#m'}if retry is None else {'phone': phone, 'amount': amount, 'request': 'p#m', 'retry': retry}
    elif request.lower() == 'share':
        if recipient != '':
            data = {'phone': phone, 'recipient': recipient, 'amount': amount, 'request': 'share'}if retry is None else {'phone': phone, 'recipient': recipient, 'amount': amount, 'request': 'share', 'retry': retry}
        else:
            data = {'phone': phone, 'amount': amount, 'request': 'c#m'}if retry is None else {'phone': phone, 'amount': amount, 'request': 'c#m', 'retry': retry}

    net = phone[:4]

    if net in mtn:
        port = '6000'
    elif net in eti:
        port = '6010'
    elif net in glo:
        port = '6020'
    elif net in zain:
        port = '6030'

    context = zmq.Context()

    push_socket = context.socket(zmq.PUSH)
    push_socket.connect("tcp://localhost:"+port)
    push_socket.send_pyobj(data)
    push_socket.close()
    context.term()


def getdatetime(cdate, ctime):
    return datetime.combine(cdate, ctime)


@periodic_task(crontab(minute='*/10'))
def scheduler():
    querysets = schedule()
    for item in querysets:
        #print datetime.date(item.date), datetime.time(item.time)
        cdatetime = getdatetime(datetime.date(item.date), datetime.time(item.time))
        if any([item.frequency != " ", item.due_dates != '0']):
            load.schedule(args=(item.user.username, item.amount, item.type, item.phone_no), eta=cdatetime)
            try:
                inter, loop = item.frequency.split('-')    # eg 2-month
            except ValueError:
                loop = ''

            if loop == 'month':
                freq = MONTHLY

            elif loop == 'week':
                freq = WEEKLY

            elif loop == 'day':
                freq = DAILY

            elif loop == 'hour':
                freq = HOURLY

            else:
                if item.due_dates == '0':
                    return


            a = rrule(MONTHLY, interval=1, count=2, bymonthday=(map(int, item.due_dates.split(','))), dtstart=cdatetime) if item.due_dates != '0' else rrule(freq, interval=int(inter), count=2, dtstart=cdatetime)
            sch_datetime = a.after(cdatetime, inc=False)
            print sch_datetime
            if sch_datetime is None:
                return

            item.date = sch_datetime
            item.time = sch_datetime

            update_schedule(item)


@periodic_task(crontab(minute='*/30'))
def check_online():
    sync_down()


@task()
def notification():
    data = {'phone': '08137474080', 'sms': 'There is a pending transaction or a problem in the transaction. Please see to it'}
    context = zmq.Context()

    push_socket = context.socket(zmq.PUSH)
    push_socket.connect("tcp://localhost:6000")     # think of a random port each belonging to the networks
    push_socket.send_pyobj(data)
    push_socket.close()
    context.term()
    #start a logic that will query for confirmation
    #or check balance against earlier transaction with the same cid
    #if it is less by the amount requested, clear the status and report


# The interval between each freq iteration. For example, when using YEARLY, an interval of 2 means once every two years,
# but with HOURLY, it means once every two hours. The default interval is 1.
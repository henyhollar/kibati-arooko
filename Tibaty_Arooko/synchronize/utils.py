from pyamf import AMF3
from pyamf.remoting.client import RemotingService

domain = 'http://127.0.0.1:8000/'   # talk down with ngrok
online_domain = 'http://mighty-reaches-7475.herokuapp.com/'



def schedule():
    gw = RemotingService(domain+'action/', amf_version=AMF3)
    service = gw.getService('ActionService')
    http_data = service.schedule()

    return http_data


def ping_offline():
    gw = RemotingService(online_domain+'action/', amf_version=AMF3)
    service = gw.getService('ActionService')
    http_data = service.ping_offline()

    return http_data


def update_schedule(data):
    gw = RemotingService(domain+'sync/', amf_version=AMF3)
    service = gw.getService('SyncService')
    http_data = service.update_schedule(data)

    return http_data


def sync_down():
    gw = RemotingService(online_domain+'sync/', amf_version=AMF3)
    service = gw.getService('SyncService')
    http_data = service.sync_down()

    return http_data

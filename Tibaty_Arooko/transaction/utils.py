from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from register.user import UserBehaviour
from wallet.models import OfflineWallet


User = get_user_model()


def check_status(f):
        def wrapper(req, data):
                if 'stop' in data:
                        return f(req, data)

                user = User.objects.get(username=data['phone'])
                if data['request'] == 'beep':
                    data.update({'amount': user.default_amt})
                hierarchy = user.hierarchy
                permission = user.permission

                user_behaviour = UserBehaviour(obj=user)

                if hierarchy == 'slave':
                    master = User.objects.get(id=user_behaviour.get_hierarchy())
                    data.update({'master': master, 'status': 'slave'})

                if permission == 'downlink':
                    uplink = User.objects.get(id=user_behaviour.get_permission())
                    data.update({'uplink': uplink, 'status': 'downlink'})

                data.update({'user': user})
                return f(req, data)
        return wrapper


from pyamf import AMF3
from pyamf.remoting.client import RemotingService

online_domain = 'http://mighty-reaches-7475.herokuapp.com/'


def update_Transaction(data):
    gw = RemotingService(online_domain+'sync/', amf_version=AMF3)
    service = gw.getService('SyncService')
    http_data = service.update_Transaction(data)

    return http_data


def create_Transaction(data):
    gw = RemotingService(online_domain+'sync/', amf_version=AMF3)
    service = gw.getService('SyncService')
    http_data = service.create_Transaction(data)

    return http_data









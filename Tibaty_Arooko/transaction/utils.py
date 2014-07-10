from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from register.user import UserBehaviour
from wallet.models import OfflineWallet
from .models import Cards


User = get_user_model()
network = ['mtn', 'eti', 'glo', 'zain']
mtn = set(['0803','0813','0703','0806','0816','0706','0810','0814','0903'])
eti = set(['0818','0809','0819','0817'])
zain = set(['0802','0812','0701','0708','0808'])
glo = set(['0805','0815','0705','0807','0811'])

mtn_card = ['100', '200', '400', '750', '1500']
eti_card = ['100', '200', '500', '1000']
glo_card = ['100', '200', '500', '1000']
zain_card = ['100', '200', '500', '1000']

card_loader = ['*555*', '*123*']


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


def choose_values(f):
    def wrapper(req, data):
            if 'stop' in data:
                    return f(req, data)

            if 'recipient' in data:
                    net = data['recipient'][:4]
            else:
                    net = data['phone'][:4]

            card_amount = data['amount']

            netwk = [nw for nw in network if net in eval(nw)]

            cardList = netwk[0]+'_card'

            card = [card for card in eval(cardList) if divmod(int(card_amount), int(card))[0] != 0]

            data.update({'amount': card[-1]})

            data.update({'network': netwk[0]})

            return f(req, data)
    return wrapper


def pop_card(f):
    def wrapper(request, data):
        try:

            card = Cards.card.getCard(data['network'], data['amount'])
            if data['network'] == "mtn":
                    cards = "*555*"+str(card.pin)+"#"

            elif data['network'] == "glo":
                    cards = "*123*"+str(card.pin)+"#"

            elif data['network'] == "zain":
                    cards = "*126*"+str(card.pin)+"#"

            else:
                    cards = card.pin

            Cards.card.delCard(card.id)
            card_count = Cards.counter.count(data['network'], data['amt'])

            data.update({'pay-load': cards, "amount": data['amount'], 'card_count': card_count})

        except IndexError:
            data.update({'stop': 'cards exhausted'})

        return f(request, data)
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

import hashlib
from suds.client import Client


def generate_checksum(f):  # Include public key in data
    def wrapper(req, data):
        if data['method'] == 'FlexiRecharge':
            string1 = data['LoginId']+'|'+data['RequestId']+'|'+data['BatchId']+'|'+data['SystemServiceID']+'|'+data['ReferalNumber']+'|'+data['Amount']+'|'+data['FromANI']+'|'+data['Email']+'|'+data['PublicKey']
        elif data['method'] == 'ResellerBalance':
            string1 = data['LoginId']+'|'+data['TillDate']+'|'+data['PublicKey']
        elif data['method'] == 'EchoCheck':
            string1 = data['LoginId']+'|'+data['Message']+'|'+data['PublicKey']

        print string1
        checksum = hashlib.sha1(string1).hexdigest()
        data.update({'Checksum': hashlib.md5(checksum).hexdigest()})
        data.pop('PublicKey')
        data.pop('method')
        print data
        return f(req, data)

    return wrapper


def flexi_recharge(data):
    client = Client('http://arizonaadmin.mobifinng.com/WebService/iTopUp/reseller_itopup.server.php?wsdl')

    return client.service.FlexiRecharge(data)  # write a parser function


def reseller_balance(data):
    client = Client('http://arizonaadmin.mobifinng.com/WebService/iTopUp/reseller_itopup.server.php?wsdl')

    return client.service.ResellerBalance(data)


def echo_check(data):
    client = Client('http://arizonaadmin.mobifinng.com/WebService/iTopUp/reseller_itopup.server.php?wsdl')

    return client.service.EchoCheck(data)








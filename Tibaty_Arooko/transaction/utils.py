from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from register.user import UserBehaviour
from wallet.models import OfflineWallet, Wallet
from .models import Cards, Transaction, Methods
from django.db.models import Q
import string
import random


User = get_user_model()

network = ['pad', 'pad', 'pad', 'pad', 'pad', 'mtn', 'glo', 'eti', 'zain']

mtn = set(['0803','0813','0703','0806','0816','0706','0810','0814','0903'])
eti = set(['0818','0809','0819','0817'])
zain = set(['0802','0812','0701','0708','0808'])
glo = set(['0805','0815','0705','0807','0811'])
pad = set([''])

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
        print data
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
        print data
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
    def wrapper(data):
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
        return f(data)

    return wrapper


@generate_checksum
def flexi_recharge(data):
    client = Client('http://arizonaadmin.mobifinng.com/WebService/iTopUp/reseller_itopup.server.php?wsdl')

    return client.service.FlexiRecharge(data)  # write a parser function


@generate_checksum
def reseller_balance(data):
    client = Client('http://arizonaadmin.mobifinng.com/WebService/iTopUp/reseller_itopup.server.php?wsdl')

    return client.service.ResellerBalance(data)


@generate_checksum
def echo_check(data):
    client = Client('http://arizonaadmin.mobifinng.com/WebService/iTopUp/reseller_itopup.server.php?wsdl')

    return client.service.EchoCheck(data)


class OnlineTransfer(object):

    def __init__(self, data):
        """
        This will call the an api from arooko. Note that the data may bear STOP in it. If so, the api will use online
        wallet since the local calculator will not calculate.
        Note that we will check for internet availability and pending. If false, another method will be chosen by the
        Selector. If internet is not available, no instance is made for this class
        It must return the success of this transaction or otherwise so as to clear the pending status.

        """
        self.data = data
        self.check_network()
        self.logger(self.data)
        print self.data
        #calculate
        self.run()

    def check_network(self):
        data = dict(Message='Test', method='EchoCheck', LoginId='28820081', PublicKey='53876806', Checksum='')
        mobifin_response = echo_check(data)
        print mobifin_response
        if [x[1] for x in mobifin_response if x[0] == 'Message'][0] != 'Test':
            #notify them to call these mobile numbers
            pass

    def run(self):
        requestID = self.id_generator(4)  # we can use a randint for the arg
        phone = self.data['phone'] if not 'recipient'in self.data else self.data['recipient']
        amount = int(self.data['amount'])*100
        sys_id = '2'
        net = self.data['phone'][:4]
        batch_id = str([i for i, nw in enumerate(network) if net in eval(nw)][0])
        print batch_id

        command = dict(Email='', FromANI='',  method='FlexiRecharge', LoginId='28820081', RequestId=requestID, BatchId=batch_id, SystemServiceID=sys_id, ReferalNumber=phone, Amount=str(amount), PublicKey='53876806', Checksum='')
        self.parse(phone, flexi_recharge(command))

    def parse(self, phone, res):
        if [x[1] for x in res if x[0] == 'ResponseCode'][0] == '000':
            data = dict(LoginId='28820081', TillDate='', PublicKey='53876806', method='ResellerBalance')
            mobifin_response = reseller_balance(data)
            if [x[1] for x in mobifin_response if x[0] == 'ResponseCode'][0] == '000':
                data = {'phone_no': phone, 'balance': float([x[1] for x in mobifin_response if x[0] == 'CurrentBalance'][0]), 'cid': 'www#000'}
                print data
                trans = Transaction.objects.filter(Q(phone_no=data['phone_no']) | Q(recipient=data['phone_no']), status='pending', cid=data['cid'])
                trans_id = trans.latest('id').id
                trans.filter(id=trans_id).update(balance=data['balance'], status='ON')

            elif [x[1] for x in res if x[0] == 'ResponseCode'][0] != '000':
                #notify them to call these mobile numbers
                #refund
                pass

    @check_status
    def logger(self, data):
        transaction = Transaction(phone_no=data['phone'], amount=data['amount'], cid=data['cid'], status='pending')
        transaction.save()

    def id_generator(self, size=6, chars=string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


def calculate(data):
    """
        calculator calculates the remainder for a user. It goes a step further if the person is a
        slave to a master by deducting from the master's wallet.
    """
    if 'stop' in data:
        return data

    #user = User.objects.get(username=data['phone'])
    wallet_to_update = Wallet.objects.filter(owner=data['user']['id']) if data['platform'] is 'online' else OfflineWallet.objects.filter(owner=data['user']['id'])
    print wallet_to_update
    user_wallet = wallet_to_update.get(owner=data['user']['id'])

    print user_wallet.amount

    if (float(user_wallet.amount) >= 100.0) and (float(user_wallet.amount) >= float(data['amount'])):
        new_wallet_amount = float(user_wallet.amount) - float(data['amount'])

    elif (float(user_wallet.amount) >= 100.0) and (float(user_wallet.amount) < float(data['amount'])):
        data.update({'amount': user_wallet.amount})
        new_wallet_amount = float(user_wallet.amount) - float(data['amount'])

    elif 'slave' in data:
        wallet_to_update = Wallet.objects.filter(owner=data['master']['id']) if data['platform'] == 'online'\
            else OfflineWallet.objects.get(owner=data['master']['id'])

        master_wallet = wallet_to_update.get(owner=data['master']['id'])

        if (float(master_wallet.amount) >= 100.0) and (float(master_wallet.amount) >= float(data['amount'])):
            new_wallet_amount = float(master_wallet.amount) - float(data['amount'])
        elif (float( master_wallet.amount) >= 100.0) and (float(master_wallet.amount) < float(data['amount'])):
            data.update({'amount':  master_wallet.amount})
            new_wallet_amount = float(master_wallet.amount) - float(data['amount'])
        else:
            data.update({'stop': 'not enough balance in the account'})
            return data

    else:
        data.update({'stop': 'not enough balance in the account'})
        return data

    wallet_to_update.update(amount=new_wallet_amount)

    data.update({'balance': new_wallet_amount})

    return data

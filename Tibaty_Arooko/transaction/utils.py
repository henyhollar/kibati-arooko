from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from register.user import UserBehaviour
from wallet.models import OfflineWallet, Wallet, WalletLog, OfflineWalletLog
from .models import Cards, Transaction, Methods
from django.db.models import Q
import string
import random
from message.views import message_as_sms


User = get_user_model()

MTN = [('50', '100'), ('51', '200'), ('52', '400'), ('53', '750'), ('54', '1500')]
ETI = [('38', '100'), ('45', '200')]
GLO = [('50', '100'), ('51', '200'), ('52', '400'), ('53', '750'), ('54', '1500')]  # not yet available
ZAIN = [('37', '100'), ('55', '200'), ('56', '500'), ('57', '1000')]

network = [('pad', 'pad'), ('zain', ''), ('eti', '08189091170'), ('pad', 'pad'), ('pad', 'pad'), ('mtn', '07069654477'), ('glo', '08111052510')]

mtn = set(['0803','0813','0703','0806','0816','0706','0810','0814','0903'])
eti = set(['0818','0809','0819','0817'])
zain = set(['0802','0812','0701','0708','0808'])
glo = set(['0805','0815','0705','0807','0811'])
pad = set([''])

mtn_card = ['100', '200', '400', '750', '1500']
eti_card = ['100', '200', '500', '1000']
glo_card = ['100', '200', '500', '1000']
zain_card = ['100', '200', '500', '1000']

card_loader = ['*555*', '*123*', '*222*']


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

        netwk = [nw[0] for nw in network if net in eval(nw[0])]

        cardList = netwk[0]+'_card'

        card = [card for card in eval(cardList) if divmod(int(card_amount), int(card))[0] != 0]

        data.update({'amount': card[-1]})  # find the difference in amount and refund

        diff = float(card_amount) - float(data['amount'])
        if diff:
            fund_data = data.copy()
            fund_data.update({'amount': diff})
            re_fund(fund_data)

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
            card_count = Cards.counter.count(data['network'], data['amount'])

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
        elif data['method'] == 'FixRecharge':
            string1 = data['LoginId']+'|'+data['RequestId']+'|'+data['BatchId']+'|'+data['SystemServiceID']+'|'+data['ReferalNumber']+'|'+data['FromANI']+'|'+data['Email']+'|'+data['PublicKey']
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
def fix_recharge(data):
    client = Client('http://arizonaadmin.mobifinng.com/WebService/iTopUp/reseller_itopup.server.php?wsdl')

    return client.service.FixRecharge(data)  # write a parser function


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
        calculate(self.data)

        self.run()

    def check_network(self):
        data = dict(Message='Test', method='EchoCheck', LoginId='28820081', PublicKey='53876806', Checksum='')
        mobifin_response = echo_check(data)
        print mobifin_response
        if [x[1] for x in mobifin_response if x[0] == 'Message'][0] != 'Test':
            #notify that it failed and they should try again
            pass

    def run(self):
        requestID = self.id_generator(4)  # we can use a randint for the arg
        if self.data['method'] == 'FlexiRecharge':
            phone = self.data['phone'] if not 'recipient'in self.data else self.data['recipient']
            amount = int(self.data['amount'])*100
            sys_id = '2'
            net = self.data['phone'][:4]
            batch_id = str([i for i, nw in enumerate(network) if net in eval(nw[0])][0])
            print batch_id

            command = dict(Email='', FromANI='',  method='FlexiRecharge', LoginId='28820081', RequestId=requestID, BatchId=batch_id, SystemServiceID=sys_id, ReferalNumber=phone, Amount=str(amount), PublicKey='53876806', Checksum='')
            self.parse(phone, flexi_recharge(command))
        else:
            sys_id = '32'
            net = self.data['network']
            phone = [nw[1] for nw in network if net == nw[0]][0]
            batch_id = [item[0] for item in eval(net.upper()) if item[1] == self.data['amount']][0]
            print batch_id

            command = dict(Email='', FromANI='',  method='FixRecharge', LoginId='28820081', RequestId=requestID, BatchId=str(batch_id), SystemServiceID=sys_id, ReferalNumber=phone, PublicKey='53876806', Checksum='')
            self.parse_fix(phone, fix_recharge(command))

    def parse(self, phone, res):
        if [x[1] for x in res if x[0] == 'ResponseCode'][0] == '000':
            data = dict(LoginId='28820081', TillDate='', PublicKey='53876806', method='ResellerBalance')
            mobifin_response = reseller_balance(data)
            if [x[1] for x in mobifin_response if x[0] == 'ResponseCode'][0] == '000':
                balance = float([x[1] for x in mobifin_response if x[0] == 'CurrentBalance'][0])
                trans = Transaction.objects.filter(Q(phone_no=phone) | Q(recipient=phone), status='pending', cid='www#000')
                trans_id = trans.latest('id').id
                trans.filter(id=trans_id).update(balance=balance, status='ON')

            elif [x[1] for x in res if x[0] == 'ResponseCode'][0] != '000':
                #notify that it failed and they should try again
                self.refund(self.data)

    def parse_fix(self, phone, res):
        if [x[1] for x in res if x[0] == 'ResponseCode'][0] == '000':
            pin = res[4][1].strip('{}').split(':')[1].strip('"')

            sms_data = {'phone': self.data['phone'] if not 'recipient'in self.data else self.data['recipient'], 'message': 'Below is the pin you requested for: '+str(pin)}
            message_as_sms(sms_data)

            data = dict(LoginId='28820081', TillDate='', PublicKey='53876806', method='ResellerBalance')
            mobifin_response = reseller_balance(data)
            if [x[1] for x in mobifin_response if x[0] == 'ResponseCode'][0] == '000':
                balance = float([x[1] for x in mobifin_response if x[0] == 'CurrentBalance'][0])
                trans = Transaction.objects.filter(Q(phone_no=phone) | Q(recipient=phone), status='pending', cid='www#001')
                trans_id = trans.latest('id').id
                trans.filter(id=trans_id).update(balance=balance, pin=pin, status='ON')

            elif [x[1] for x in res if x[0] == 'ResponseCode'][0] != '000':
                #notify that it failed and they should try again
                self.refund(self.data)

    @check_status
    def logger(self, data):
        transaction = Transaction(phone_no=data['phone'], amount=data['amount'], cid=data['cid'], status='pending')
        transaction.save()

    def refund(self, data):
        user = User.objects.get(username=data['phone'])
        wallet_to_update = Wallet.objects.filter(owner=user.id) if data['platform'] is 'online' else OfflineWallet.objects.filter(owner=user.id)
        user_wallet = wallet_to_update.get(owner=user.id)
        new_wallet_amount = float(user_wallet.amount) + float(data['amount'])
        wallet_to_update.update(amount=new_wallet_amount)

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
        wallet_to_update = Wallet.objects.filter(owner=data['master']['id']) if data['platform'] == 'online' else OfflineWallet.objects.get(owner=data['master']['id'])

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

    log = WalletLog(wallet=user_wallet, amount=new_wallet_amount, report='withdrawal') if data['platform'] is 'online' else OfflineWalletLog(wallet=user_wallet, amount=new_wallet_amount, report='withdrawal')
    log.save()

    return data


def retryTransaction(cid, status):
    import zmq.green as zmq

    context = zmq.Context()

    trans = Methods.objects.get(cid=cid, status='pending')
    trans.status = 'OFF' if status is None else 'ON'
    trans.save()

    if trans and status != 'DISCARD':
        if trans.recipient:
            data = {'phone': trans.phone_no, 'recipient': trans.recipient, 'amount': trans.amount, 'request': 'c#m', 'retry': True}
        else:
            data = {'phone': trans.phone_no, 'amount': trans.amount, 'request': 'c#m', 'retry': True}

        net = trans.phone_no[:4]

        if net in mtn:
            port = '6000'
        elif net in eti:
            port = '6010'
        elif net in glo:
            port = '6020'
        elif net in zain:
            port = '6030'

        push_socket = context.socket(zmq.PUSH)
        push_socket.connect("tcp://localhost:"+port)
        push_socket.send_pyobj(data)
        push_socket.close()
        context.term()


def re_fund(data):
    user = User.objects.get(username=data['phone'])
    wallet_to_update = Wallet.objects.filter(owner=user.id) if data['platform'] is 'online' else OfflineWallet.objects.filter(owner=user.id)
    user_wallet = wallet_to_update.get(owner=user.id)
    new_wallet_amount = float(user_wallet.amount) + float(data['amount'])
    wallet_to_update.update(amount=new_wallet_amount)

    log = WalletLog(wallet=user_wallet, amount=new_wallet_amount, report='refund') if data['platform'] is 'online' else OfflineWalletLog(wallet=user_wallet, amount=new_wallet_amount, report='refund')
    log.save()
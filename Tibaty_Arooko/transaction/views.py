from django.contrib.auth import get_user_model
from pyamf.remoting.gateway.django import DjangoGateway
from django.db.models import Q
from .utils import check_status
from wallet.models import OfflineWallet, Wallet
from transaction.models import Transaction, Cards, Methods
from message.views import message_as_sms
from scheduler.models import getSchedule
from .utils import update_Transaction, create_Transaction, flexi_recharge, generate_checksum, reseller_balance, choose_values, echo_check, pop_card


User = get_user_model()


def ping(request, echo):
    return echo


@check_status
def beepRequest(request, data):

    return data


@check_status
def messageRequest(request, data):

    return data


@choose_values
@check_status
def cardRequest(request, data):

    return data


def queryTransaction(request, data):
    method = Methods.objects.filter(Q(status='pending') | Q(status='OFF'), cid=data['cid']).exists()
    #if data['cid'] == 'www#05': do echocheck
    return method


def rescheduleTransaction(request, cid):
    method = Methods.objects.get(cid=cid, status='pending')
    method.status = 'OFF'
    method.save()

    return method


def updateTransaction(request, data):
    Transaction.objects.filter(phone_no=data['phone_no'], status='pending', cid=data['cid']).update(balance=data['balance'], status='ON')
    Methods.objects.filter(phone_no=data['phone_no'], status='pending', cid=data['cid']).update(status='ON')

    #update_Transaction(data)  # this goes to create transaction online
    return 'success'


def logger(request, data):
    transaction = Transaction(phone_no=data['phone'], amount=data['amount'], cid=data['cid'], status='pending')
    method, created = Methods.objects.get_or_create(cid=data['cid'])
    method.phone_no = data['phone']
    method.amount = data['amount']
    method.status = 'pending'
    if 'recipient' in data:
        transaction.recipient = data['recipient']
        method.recipient = data['recipient']

    if 'pay-load' in data:
        transaction.pin = data['pay-load']
        method.status = 'ON'

    transaction.save()
    method.save()

    #create_Transaction(data)  # this goes to create transaction online

    return 'successful'


def sendMessage(data):
    message_as_sms(data)

    return 'success'


def schedule(request):
    return getSchedule()


@generate_checksum
def mobifin_recharge(request, data):
    res = flexi_recharge(data)
    return list(res)


@generate_checksum
def mobifin_balance(request, data):
    res = reseller_balance(data)
    return list(res)


@generate_checksum
def mobifin_echo(request, data):
    res = echo_check(data)
    return list(res)


@pop_card
@choose_values
def calling_card(request, data):
    #call count and put into front-end data
    return data


def counter(request, data):
    card_count = Cards.counter.count(data['network'], data['category'])
    data.update({'card_count': card_count})
    return data


def card_to_db(request, data):
    card = Cards(
        network=data['network'],
        category=data['category'],
        pin=data['pin'],
        serial_no=data['serial_no']
    )
    card.save()

    return 'successful'


def refund(request, data):
    user = User.objects.get(username=data['phone'])
    wallet_to_update = Wallet.objects.filter(owner=user.id) if data['platform'] is 'online' else OfflineWallet.objects.filter(owner=user.id)
    user_wallet = wallet_to_update.get(owner=user.id)
    new_wallet_amount = float(user_wallet.amount) + float(data['amount'])
    wallet_to_update.update(amount=new_wallet_amount)

    return 'success'


def calculator(request, data):
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


# Finally to expose django views use DjangoGateway
agw = DjangoGateway({"ActionService.beepRequest": beepRequest,
                    "ActionService.messageRequest": messageRequest,
                    "ActionService.calculator": calculator,
                    "ActionService.refund": refund,
                    "ActionService.cardRequest": cardRequest,
                    "ActionService.queryTransaction": queryTransaction,
                    "ActionService.rescheduleTransaction": rescheduleTransaction,
                    "ActionService.updateTransaction": updateTransaction,
                    "ActionService.logger": logger,
                    "ActionService.sendMessage": sendMessage,
                    "ActionService.schedule": schedule,
                    "ActionService.mobifin_recharge": mobifin_recharge,
                    "ActionService.mobifin_balance": mobifin_balance,
                    "ActionService.mobifin_echo": mobifin_echo,
                    "ActionService.calling_card": calling_card,
                    "ActionService.counter": counter,
                    "ActionService.card_to_db": card_to_db,
                    "ActionService.ping": ping,

})




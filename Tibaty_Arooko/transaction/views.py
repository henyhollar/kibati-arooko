from django.contrib.auth import get_user_model
from pyamf.remoting.gateway.django import DjangoGateway
from django.db.models import Q
from .utils import check_status
from wallet.models import OfflineWallet, Wallet
from transaction.models import Transaction
from message.views import message_as_sms
from synchronize.models import getSchedule


User = get_user_model()


@check_status
def beepRequest(request, data):

    return data


@check_status
def messageRequest(request, data):

    return data


@check_status
def cardRequest(request, data):

    return data


def queryTransaction(request, data):
    transaction = Transaction.objects.filter(Q(status='pending') | Q(status='OFF'), cid=data['cid']).exists()
    return transaction


def updateTransaction(request, data):
    Transaction.objects.filter(phone_no=data['phone_no'], status='pending').update(
        balance=data['balance'],
        status='ON'
    )



def logger(request, data):
    transaction = Transaction(
        phone_no=data['phone'],
        amount=data['amount'],
        cid=data['cid'],
        status='pending'
    )
    #if 'recipient' in data:
        #transaction.recipient=data['recipient']

    transaction.save()

    return 'successful'


def sendMessage(data):
    message_as_sms(data)

    return 'success'


def schedule():
    return getSchedule()


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
                    "ActionService.cardRequest": cardRequest,
                    "ActionService.queryTransaction": queryTransaction,
                    "ActionService.updateTransaction": updateTransaction,
                    "ActionService.logger": logger,
                    "ActionService.sendMessage": sendMessage,
                    "ActionService.schedule": schedule,

 })
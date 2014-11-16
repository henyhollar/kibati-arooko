from django.contrib.auth import get_user_model
from pyamf.remoting.gateway.django import DjangoGateway
from django.db.models import Q
from .utils import check_status
from wallet.models import OfflineWallet, Wallet, WalletLog, OfflineWalletLog
from transaction.models import Transaction, Cards, Methods
from message.views import message_as_sms
from scheduler.models import getSchedule
from .utils import update_Transaction, create_Transaction, flexi_recharge, calculate, reseller_balance, choose_values, echo_check, pop_card, fix_recharge, retryTransaction, re_fund, OnlineTransfer


User = get_user_model()


def ping(request, echo):
    return echo


@check_status
def beepRequest(request, data):

    return data


@check_status
def messageRequest(request, data):

    return data


#@choose_values
@check_status
def cardRequest(request, data):

    return data


def queryTransaction(request, data):
    method = Methods.objects.filter(~Q(status='ON'), cid=data['cid']).exists()
    #if data['cid'] == 'www#05': do echocheck
    return method


def issueTransaction(request, data=None):
    obj = Methods.objects.filter(~Q(status='ON')) if data is None else Transaction.objects.filter(~Q(balance=None), cid=data['cid']).latest('id')

    return obj


def rescheduleTransaction(request, cid):
    method = Methods.objects.get(cid=cid, status='pending')
    method.status = 'OFF'
    method.save()

    return method


def retry(request, cid, status):
    retryTransaction(cid, status)

    return 'success'


def updateTransaction(request, data):
    Methods.objects.filter(Q(phone_no=data['phone_no']) | Q(recipient=data['phone_no']), status='pending', cid=data['cid']).update(status='ON')
    trans = Transaction.objects.filter(Q(phone_no=data['phone_no']) | Q(recipient=data['phone_no']), status='pending', cid=data['cid'])
    trans_id = trans.latest('id').id
    trans.filter(id=trans_id).update(balance=data['balance'], status='ON')

    #update_Transaction(data)  # this goes to create transaction online
    return 'successful'


def logger(request, data):
    transaction = Transaction(phone_no=data['phone'], amount=data['amount'], cid=data['cid'], status='pending')

    method, created = Methods.objects.get_or_create(cid=data['cid'])
    method.phone_no = data['phone']
    method.amount = data['amount']
    method.status = 'pending' if not any(['card#06' == data['cid'], 'card#16' == data['cid'], 'card#26' == data['cid'], 'card#36' == data['cid']]) else 'ON'

    transaction.recipient = method.recipient = data['recipient'] if 'recipient' in data else ''

    if 'pay-load' in data:
        transaction.pin, method.status = (data['pay-load'], 'ON')

    transaction.save()
    method.save()

    #create_Transaction(data)  # this goes to create transaction online

    return 'successful'


def log_bal(request, data):
    transaction = Transaction(phone_no=data['phone'], amount=data['amount'], cid=data['cid'], status='pending')
    transaction.save()

    return 'successful'


def sendMessage(data):
    message_as_sms(data)

    return 'success'


def schedule(request):
    return getSchedule()


def mobifin_recharge(request, data):
    res = flexi_recharge(data)
    return list(res)


def mobifin_card_recharge(request, data):
    res = fix_recharge(data)
    return list(res)


def mobifin_balance(request, data):
    res = reseller_balance(data)
    return list(res)


def mobifin_echo(request, data):
    res = echo_check(data)
    return list(res)


@choose_values  # will run first
@pop_card
def calling_card(request, data):    # refund the difference
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
        pin=data['pin']
    )
    card.save()

    return 'successful'


def refund(request, data):
    re_fund(data)

    return 'success'


def calculator(request, data):

    return calculate(data)


from rest_framework.views import APIView
from rest_framework.response import Response
from huey.djhuey import task


class Recharge(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get(self, request, username):
        # get info about last transaction from Transaction
        last_transaction = Transaction.objects.filter(phone_no=username)
        return last_transaction.latest('id').status

    def post(self, request, username):
        if request.DATA['request'] == 'beep':
            data = {'phone': request.DATA['phone'].replace('+234', '0'), 'request': request.DATA['request'], 'platform': 'online', 'method': 'FlexiRecharge', 'recipient': request.DATA['recipient'].replace('+234', '0')}
        else:
            data = {'phone': request.DATA['phone'].replace('+234', '0'), 'request': request.DATA['request'], 'platform': 'online', 'method': request.DATA['method'], 'recipient': request.DATA['recipient'].replace('+234', '0'), 'amount': request.DATA['amount']}

        self.recharge(data)

        return Response('Processing your request please wait...')

    @task
    def recharge(self, data):
        OnlineTransfer(data)



# Finally to expose django views use DjangoGateway
agw = DjangoGateway({"ActionService.beepRequest": beepRequest,
                    "ActionService.messageRequest": messageRequest,
                    "ActionService.calculator": calculator,
                    "ActionService.refund": refund,
                    "ActionService.cardRequest": cardRequest,
                    "ActionService.queryTransaction": queryTransaction,
                    "ActionService.issueTransaction": issueTransaction,
                    "ActionService.rescheduleTransaction": rescheduleTransaction,
                    "ActionService.retry": retry,
                    "ActionService.updateTransaction": updateTransaction,
                    "ActionService.logger": logger,
                    "ActionService.log_bal": log_bal,
                    "ActionService.sendMessage": sendMessage,
                    "ActionService.schedule": schedule,
                    "ActionService.mobifin_recharge": mobifin_recharge,
                    "ActionService.mobifin_card_recharge": mobifin_card_recharge,
                    "ActionService.mobifin_balance": mobifin_balance,
                    "ActionService.mobifin_echo": mobifin_echo,
                    "ActionService.calling_card": calling_card,
                    "ActionService.counter": counter,
                    "ActionService.card_to_db": card_to_db,
                    "ActionService.ping": ping,

})




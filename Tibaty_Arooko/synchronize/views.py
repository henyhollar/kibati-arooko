from django.contrib.auth import get_user_model
from django.shortcuts import get_list_or_404
from rest_framework import generics
from pyamf.remoting.gateway.django import DjangoGateway
from wallet.models import OfflineWallet, Wallet
from scheduler.models import Schedule
from transaction.models import Transaction
from .models import Sync
from .tasks import task_request, notification, get_balance


User = get_user_model()
notice = None
count = 0

def register(request, obj):
    User.objects.create(username=obj.username)
    for user in User.objects.all():
        try:
            OfflineWallet.objects.create(owner=user)
        except IntegrityError:
            pass
        try:
            Schedule.objects.create(user=user)
        except IntegrityError:
            pass
    return 'success'


def update_user(request, obj):
    User.objects.filter(username=obj.username).update(
        default_amt=obj.default_amt,
        plug=obj.plug,
        glue=obj.glue,
        hierarchy=obj.hierarchy,
        permission=obj.permission,
        ack=True
    )
    return 'success'


def update_wallet(request, obj):
    Wallet.objects.filter(owner=obj.id).update(
        amount=obj.amount,
        ack=True
    )
    return 'success'


def update_offline_wallet(request, obj):
    OfflineWallet.objects.filter(owner=obj.id).update(
        amount=obj.amount,
        ack=True
    )
    return 'success'


def update_schedule(request, obj):
    Schedule.objects.filter(user=obj.id).update(
        amount=obj.amount,
        date=obj.date,
        time=obj.time,
        frequency=obj.frequency,
        due_dates=obj.due_dates,
        type=obj.type,
        phone_no=obj.phone_no,
        status=obj.status,
        ack=True
    )
    return 'success'


def update_transaction(request, data):
    Transaction.objects.filter(phone_no=data['phone_no'], status='pending').update(
        balance=data['balance'],
        status='ON'
    )
    return 'success'


def create_transaction(request, data):
    transaction = Transaction(
        phone_no=data['phone'],
        amount=data['amount'],
        cid=data['cid'],
        status='pending'
    )
    transaction.recipient = data['recipient'] if 'recipient' in data else ''

    if 'pay-load' in data:
        transaction.pin, transaction.status = (data['pay-load'], 'ON')  # when pin is requested

    transaction.save()

    return 'success'


def sync_down(request):
    """
        this will be called to sync the offline after a startup or network restore. The sync table is updated every time
        an event occurs at various important functions. The sync table is ack after every successful sync, so it will
        not be called any more.
    """
    synk = Sync.objects.filter(ack=False)
    for syn in synk:
        if syn.method == 'register' or syn.method == 'update_user':
            obj = User.objects.get(id=syn.id)
        elif syn.method == 'update_wallet':
            obj = Wallet.objects.get(id=syn.id)
        elif syn.method == 'update_offline_wallet':
            obj = OfflineWallet.objects.get(id=syn.id)
        elif syn.method == 'update_schedule':
            obj = Schedule.objects.get(id=syn.id)
        elif syn.method == 'update_transaction':
            obj = Transaction.objects.get(id=syn.id)
        elif syn.method == 'create_transaction':
            obj = Transaction.objects.get(id=syn.id)

        res = task_request(obj, 'www.arooko.ngrok.com', syn.method)     # the receiver should ack=True
        #if res == 'success':
            #Sync.objects.filter(id=syn.id).update(ack=True)


def notify(request):
    global notice, count
    if count != 1:
        notice = notification.schedule(delay=(60 * 5))  # there should be one at a time
        count += 1
        get_balance()

def revoker(request):
    global notice, count
    notice.revoke()
    count = 0


# Finally to expose django views use DjangoGateway
sync = DjangoGateway({"SyncService.register": register,
                    "SyncService.update_user": update_user,
                    "SyncService.update_wallet": update_wallet,
                    "SyncService.update_offline_wallet": update_offline_wallet,
                    "SyncService.update_schedule": update_schedule,
                    "SyncService.update_transaction": update_transaction,
                    "SyncService.create_transaction": create_transaction,
                    "SyncService.sync_down": sync_down,
                    "SyncService.notify": notify,
                    "SyncService.revoker": revoker,
 })
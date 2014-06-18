from django.contrib.auth import get_user_model
from django.shortcuts import get_list_or_404
from rest_framework import generics
from pyamf.remoting.gateway.django import DjangoGateway
from wallet.models import OfflineWallet
from scheduler.models import Schedule
from transaction.models import Transaction


User = get_user_model()


def register(request, obj):
    user = User.objects.create(username=obj.username)
    #signal post save to create schedule and offlinewallet
    #for user in User.objects.all():
    #    try:
    #        OfflineWallet.objects.create(owner=user)
    #    except IntegrityError:
    #        pass
    #    try:
    #        Schedule.objects.create(user=user)
    #    except IntegrityError:
    #        pass
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


def update_transaction(request, obj):
    Transaction.objects.filter(phone_no=obj.username).update(
        amount=obj.amount,
        balance=obj.balance,
        cid=obj.cid,
        status=obj.status,
        ack=True
    )
    return 'success'


def create_transaction(request, obj):
    Transaction.objects.create(
        phone_no=obj.username,
        amount=obj.amount,
        balance=obj.balance,
        cid=obj.cid,
        status=obj.status,
        ack=True
    )
    return 'success'


# Finally to expose django views use DjangoGateway
sync = DjangoGateway({"SyncService.register": register,
                    "SyncService.update_user": update_user,
                    "SyncService.update_wallet": update_wallet,
                    "SyncService.update_schedule": update_schedule,
                    "SyncService.update_transaction": update_transaction,
                    "SyncService.create_transaction": create_transaction,
 })
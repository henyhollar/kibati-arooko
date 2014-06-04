from django.contrib.auth import get_user_model
from django.shortcuts import get_list_or_404
from rest_framework import generics
from .serializers import OfflineUserUpdateSerializer, OfflineRegisterUserSerializer, UpdateOfflineWalletSerializer, \
    TransactionUpdateSerializer, OfflineScheduleUpdateSerializer, CreateTransactionSerializer
from wallet.models import OfflineWallet
from scheduler.models import Schedule
from transaction.models import Transaction

User = get_user_model()


class OfflineRegisterUser(generics.CreateAPIView):
    """
        This class will register offline user i.e it is a one-way class
    """
    model = User
    serializer_class = OfflineRegisterUserSerializer

    def pre_save(self, obj):
        user = self.request.DATA.get('obj')
        obj.default_amt = user.default_amt
        #Relationships
        obj.plug = user.plug
        obj.glue = user.glue
        #Status
        obj.hierarchy = user.hierarchy
        obj.permission = user.permission
        obj.ack = True

    def post_save(self, obj, created=False):
        for user in User.objects.all():
            try:
                OfflineWallet.objects.create(owner=user)
            except IntegrityError:
                pass
            try:
                Schedule.objects.create(user=user)
            except IntegrityError:
                pass


class OfflineUserUpdate(generics.UpdateAPIView):
    """
        This class will update offline user i.e it is a one-way class
    """
    queryset = User.objects.all()
    serializer_class = OfflineUserUpdateSerializer
    lookup_field = 'username'

    def pre_save(self, obj):
        user = self.request.DATA.get('obj')
        obj.default_amt = user.default_amt
        #Relationships
        obj.plug = user.plug
        obj.glue = user.glue
        #Status
        obj.hierarchy = user.hierarchy
        obj.permission = user.permission
        obj.ack = True


class WalletUpdate(generics.UpdateAPIView):
    """
        This class will update offline wallet on both ends.
    """

    queryset = OfflineWallet.objects.all()
    serializer_class = UpdateOfflineWalletSerializer
    lookup_field = 'owner'

    def pre_save(self, obj):
        wallet = self.request.DATA.get('obj')
        obj.amount = wallet.amount
        obj.ack = True


class OfflineScheduleUpdate(generics.UpdateAPIView):
    """
        This class will update schedule at the offline platform alone.
    """
    queryset = Schedule.objects.all()
    serializer_class = OfflineScheduleUpdateSerializer
    lookup_field = 'user'

    def pre_save(self, obj):
        schedule = self.request.DATA.get('obj')
        obj.date = schedule.date
        obj.time = schedule.time
        obj.frequency = schedule.frequency
        obj.due_dates = schedule.due_dates
        obj.type = schedule.type
        obj.phone_no = schedule.phone_no
        obj.status = schedule.status
        obj.ack = True


class CreateTransaction(generics.CreateAPIView):
    """
        This class will create transaction on online platforms.
    """
    model = Transaction
    serializer_class = CreateTransactionSerializer

    def pre_save(self, obj):
        trans = self.request.DATA.get('obj')
        obj.amount = trans.amount
        obj.balance = trans.balance
        obj.cid = trans.cid
        obj.status = trans.status
        obj.ack = True


class TransactionUpdate(generics.UpdateAPIView):
    """
        This class will update transaction on online platforms.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionUpdateSerializer
    lookup_field = 'phone_no'

    def get_object(self):
        filters = {
            str(self.lookup_field): self.kwargs[self.lookup_field],
            'status': 'pending'
        }
        obj = get_list_or_404(self.queryset, filters)

        return obj

    def pre_save(self, obj):
        trans = self.request.DATA.get('obj')
        obj.amount = trans.amount
        obj.balance = trans.balance
        obj.cid = trans.cid
        obj.status = trans.status
        obj.ack = True



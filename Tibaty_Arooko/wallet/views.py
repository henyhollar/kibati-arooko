from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics
from .models import Wallet, WalletLog, OfflineWallet, OfflineWalletLog
from .serializers import CheckBalanceSerializer, UpdateWalletSerializer, UpdateOfflineWalletSerializer
from synchronize.tasks import task_request
from synchronize.models import Sync
from message.views import message_as_email

User = get_user_model()


class CheckBalance(generics.RetrieveAPIView):
    queryset = Wallet.objects.all()
    serializer_class = CheckBalanceSerializer


class UpdateWallet(generics.UpdateAPIView):
    def __init__(self):
        super(UpdateWallet, self).__init__()
        self.uplink_user = None
        self.master_user = None

    def get_queryset(self):
        if self.kwargs.get('uplink_username', False):
            try:
                self.uplink_user = User.objects.get(username=self.kwargs['uplink_username'], permission='uplink')
            except:
                raise generics.PermissionDenied

        elif self.kwargs.get('master_username', False):
            try:
                self.master_user = User.objects.get(username=self.kwargs['master_username'], hierarchy='master')
            except:
                raise generics.PermissionDenied

        try:
            owner = User.objects.get(Q(Q(plug__isnull=True) | Q(plug=self.uplink_user)) | Q(Q(glue__isnull=True) | Q(glue=self.master_user)), username=self.kwargs['owner'])
        except:
            raise generics.PermissionDenied

        self.kwargs['owner'] = owner
        self.kwargs['uplink_user'] = self.uplink_user
        self.kwargs['master_user'] = self.master_user

        return Wallet.objects.all()

    serializer_class = UpdateWalletSerializer
    lookup_field = 'owner'

    def get_serializer_context(self):
        context = super(UpdateWallet, self).get_serializer_context()
        # you have access to self.request here
        context.update({
            'kwargs':self.kwargs
        })

        return context

    def pre_save(self, obj):
        pass

    def post_save(self, obj, created=False):
        if self.uplink_user:
            WalletLog.objects.create(wallet=obj, user_from=self.uplink_user, amount=obj.amount, report='uplink-to-downlink')
        elif self.master_user:
            WalletLog.objects.create(wallet=obj, user_from=self.master_user, amount=obj.amount, report='master-to-slave')
        else:
            WalletLog.objects.create(wallet=obj, amount=obj.amount, report='self')

        msg = 'Dear Customer, {} credited your account with {}. Thanks for your patronage!'.format(self.kwargs['owner'].get_full_name, obj.amount)
        data = {'message': msg, 'phone': self.kwargs['owner'].phone}
        message_as_sms(data)


class UpdateOfflineWallet(generics.UpdateAPIView):
    def __init__(self):
        super(UpdateOfflineWallet, self).__init__()
        self.uplink_user = None
        self.master_user = None

    def get_queryset(self):
        if self.kwargs.get('uplink_username', False):
            try:
                self.uplink_user = User.objects.get(username=self.kwargs['uplink_username'], permission='uplink')
            except:
                raise generics.PermissionDenied

        elif self.kwargs.get('master_username', False):
            try:
                self.master_user = User.objects.get(username=self.kwargs['master_username'], hierarchy='master')
            except:
                raise generics.PermissionDenied

        try:
            owner = User.objects.get(Q(Q(plug__isnull=True) | Q(plug=self.uplink_user)) | Q(Q(glue__isnull=True) | Q(glue=self.master_user)), username=self.kwargs['owner'])
        except:
            raise generics.PermissionDenied

        self.kwargs['owner'] = owner
        self.kwargs['uplink_user'] = self.uplink_user
        self.kwargs['master_user'] = self.master_user

        return OfflineWallet.objects.all()

    serializer_class = UpdateOfflineWalletSerializer
    lookup_field = 'owner'

    def get_serializer_context(self):
        context = super(UpdateOfflineWallet, self).get_serializer_context()
        # you have access to self.request here
        context.update({
            'kwargs': self.kwargs
        })

        return context

    def pre_save(self, obj):
        pass

    def post_save(self, obj, created=False):
        if self.uplink_user:
            OfflineWalletLog.objects.create(wallet=obj, user_from=self.uplink_user, amount=obj.amount, report='uplink-to-downlink')
        elif self.master_user:
            OfflineWalletLog.objects.create(wallet=obj, user_from=self.master_user, amount=obj.amount, report='master-to-slave')
        else:
            OfflineWalletLog.objects.create(wallet=obj, amount=obj.amount, report='self')

        Sync.objects.create(method='update_wallet', model_id=obj.id)

        task_request(obj, 'www.arooko.ngrok.com', 'update_wallet')

        #send this message in the sync after sync
        msg = 'Dear Customer, {} credited your account with {}. Thanks for your patronage!'.format(self.kwargs['owner'].get_full_name, obj.amount)
        data = {'message':msg, 'phone':self.kwargs['owner'].phone}
        message_as_sms(data)
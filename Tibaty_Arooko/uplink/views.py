from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.authtoken.models import Token
from serializers import UplinkRegisterSerializer, PlugUserSerializer
from wallet.models import Wallet
from register.user import UserBehaviour
from .permissions import IsUplink
from synchronize.tasks import task_request
from message.views import message_as_email, message_as_sms

User = get_user_model()


class UplinkRegisterList(generics.ListCreateAPIView):

    def get_queryset(self):
        try:
            uplink_user = User.objects.get(username=self.kwargs['uplink_username'], permission='uplink')
        except:
            raise generics.PermissionDenied

        return User.objects.filter(plug=uplink_user)

    serializer_class = UplinkRegisterSerializer

    def pre_save(self, obj):
        reset_password = User.objects.make_random_password(length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        print reset_password
        obj.set_password(reset_password)
        #remeber to send the password to the phone no. of the user. Once the email is set, the user can make choices.
        data = {
            'message': 'Dear customer, thanks for signing up. Your password is:' + reset_password +
                       '. Have the best re-charging experience ever! ',
            'phone': obj.username
        }
        message_as_sms(data)

        user_behaviour = UserBehaviour(obj)

        #get the instance of the uplink
        uplink_user = User.objects.get(username=self.kwargs['uplink_username'])

        #plug the new user to the uplink
        user_behaviour.plug_into = uplink_user

    def post_save(self, obj, created=True):
        for user in User.objects.all():
            try:
                Wallet.objects.create(owner=user)
            except IntegrityError:
                pass
            try:
                OfflineWallet.objects.create(owner=user)
            except IntegrityError:
                pass
            try:
                Token.objects.create(user=user)
            except IntegrityError:
                pass
            try:
                Schedule.objects.create(user=user)
            except IntegrityError:
                pass

        task_request(obj, 'www.arooko.ngrok.com', 'register')


class PlugUser(generics.UpdateAPIView):
    def __init__(self):
        super(PlugUser, self).__init__()
        self.uplink_user = None

    def get_queryset(self):
        if self.kwargs.get('uplink_username', False):
            try:
                self.uplink_user = User.objects.get(username=self.kwargs['uplink_username'], permission='uplink')
            except:
                raise generics.PermissionDenied

        try:
            downlink_user = User.objects.get(username=self.kwargs['username'], permission='normal', hierarchy='master')
        except User.DoesNotExist:
            try:
                downlink_user = User.objects.get(username=self.kwargs['username'], permission='downlink', hierarchy='master')
            except User.DoesNotExist:
                raise generics.PermissionDenied

        #state reasons why permission might fail in the front-end eg. the user is already a downlink/uplink
        #send notification to the proposed downlink

        self.kwargs['uplink_user'] = self.uplink_user
        self.kwargs['downlink_user'] = downlink_user

        return User.objects.all()


    serializer_class = PlugUserSerializer
    lookup_field = 'username'
    permission_classes = (IsUplink,)

    def get_serializer_context(self):
        context = super(PlugUser, self).get_serializer_context()
        # you have access to self.request here
        context.update({
            'kwargs':self.kwargs
        })

        return context

    def post_save(self, obj, created=False):
        task_request(obj, 'www.arooko.ngrok.com', 'update_user')


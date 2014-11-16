from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.contrib.auth import logout, login, authenticate
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions, status
from .permissions import IsMaster
from rest_framework.views import APIView
from rest_framework.response import Response
from serializers import RegisterSerializer, RegisterSlaveSerializer, ChangePasswordSerializer, UpdateSerializer, \
    GlueUserSerializer, ChangeDefaultSerializer, SessionSerializer
from django.http import HttpResponse
from wallet.models import Wallet, OfflineWallet
from scheduler.models import Schedule
from .user import UserBehaviour, UserGroups
from message.tasks import task_sms
from message.views import message_as_email, message_as_sms
from synchronize.tasks import task_request
from synchronize.models import Sync
from rest_framework.decorators import api_view
from rest_framework.response import Response



User = get_user_model()


class RegisterList(generics.ListCreateAPIView):
    """
        Register with only phone no & the password will be sent to it. if the user has never logged-in before,
        and clicks forget password, the password will be sent again. But if he has logged-in, forget password
        will need your email. That means you should have entered your email earlier. With this, we send you a
        click-able link to effect the change of password or discard it if not requested by you.
    """

    def __init__(self):
        super(RegisterList, self).__init__()
        self.reset_password = None

    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def pre_save(self, obj):
        self.reset_password = User.objects.make_random_password(length=10,
                                                           allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
        print self.reset_password
        obj.set_password(self.reset_password)

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

        #send notification: consider using ngrok to call an offline API or try twilio later on
        Sync.objects.create(method='register', model_id=obj.id)

        task_request(obj, 'www.arooko.ngrok.com', 'register')   # ack sync table if successful

        #remeber to send the password to the phone no. of the user. Once the email is set, the user can make choices.
        data = {
            'message': 'Dear customer, thanks for signing up. Your password is: {}. Have the best re-charging experience ever!'.format(self.reset_password),
            'phone': obj.username
        }
        task_sms(data)


class RegisterSlaveList(generics.ListCreateAPIView):
    """

    """

    queryset = User.objects.all()
    serializer_class = RegisterSlaveSerializer

    def pre_save(self, obj):
        userbehaviour = UserBehaviour(obj=obj)
        userbehaviour.glue_to = User.objects.get(username=self.request.DATA.get('username'))

    def get_serializer_context(self):
        context = super(RegisterSlaveList, self).get_serializer_context()
        # you have access to self.request here
        context.update({
            'kwargs': self.kwargs
        })

        return context

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

        #send notification: consider using ngrok to call an offline API
        Sync.objects.create(method='register', model_id=obj.id)

        task_request(obj, 'www.arooko.ngrok.com', 'register')
        data = {
            'message': 'Dear customer, thanks for signing up. Have the best re-charging experience ever!',
            'phone': obj.username
        }
        task_sms(data)


class ChangePassword(generics.UpdateAPIView):
    def get_queryset(self):
        if self.kwargs.get('username') == self.request.user.username:
            return User.objects.all()
        raise generics.PermissionDenied

    lookup_field = 'username'
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def pre_save(self, obj):
        new_password = self.request.DATA.get('new_password')
        old_password = self.request.DATA.get('old_password')
        print obj.password
        if check_password(old_password, obj.password):
            obj.set_password(new_password)
            #send to user
            data = {
                'subject': 'Password Change',
                'message': 'Dear customer, your new password is:'
                           + new_password + '. Have the best re-charging experience ever! ',
                'phone': obj.username
            }
            # make sure the email of the user is already set
            message_as_email(data)


class UserDetail(APIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get_wallet(self, request):
        wallet = Wallet.objects.get(owner=request.user)

        return {'wallet': wallet.amount}

    def get_object(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise generics.PermissionDenied

    def get(self, request, username, format=None):
        query = self.get_object(username)
        user_group = UserGroups(query)
        group_property = user_group.populate_family_group()
        group_property.update(self.get_wallet(request))

        return Response(group_property)

    def put(self, request, username, format=None):
        query = self.get_object(username)
        serializer = UpdateSerializer(query, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #def post_save(self, obj, created=False):
    #    task_request(obj, 'www.arooko.ngrok.com', 'update_user')



def ResetPassword(request, username):
    if request.method == 'GET':
        user = User.objects.get(username=username)
        reset_password = User.objects.make_random_password(length=10,
                                                           allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')

        #remeber to send the password to the phone no. of the user. Once the email is set, the user can make choices.
        data = {
            'subject': 'Password Reset',
            'message': 'Dear customer, your new password is:' + reset_password + '. Have the best re-charging experience ever! ',
            'recipient': request.user.email,
            'phone': request.user.username
        }
        if request.user.email is not None or request.user.email is not ' ':
            user.set_password(reset_password)
            user.save()
            message_as_email(data)

        else:
            message_as_sms(data)

        return Response({'success': True})


#only the master user can add other users as his slaves. There at the front-end, only the user who's status is master will have a menu called add users.
#and in this case, the user has to be already registered.
# functions are: offline-update, master and uplink wallet-update
class GlueUser(generics.UpdateAPIView):
    def __init__(self):
        super(GlueUser, self).__init__()
        self.master_user = None

    def get_queryset(self):
        if self.kwargs.get('master_username', False):
            try:
                self.master_user = User.objects.get(username=self.kwargs['master_username'], hierarchy='master')
            except:
                raise generics.PermissionDenied

        try:
            slave_user = User.objects.get(~Q(permission='uplink'), username=self.kwargs['username'], hierarchy='master')
        except:
            try:
                slave_user = User.objects.get(~Q(permission='uplink'), username=self.kwargs['username'],
                                              hierarchy='slave')
            except:
                raise generics.PermissionDenied

        self.kwargs['master_user'] = self.master_user
        self.kwargs['slave_user'] = slave_user

        return User.objects.all()


    serializer_class = GlueUserSerializer
    lookup_field = 'username'
    #permission_classes = (IsMaster,)

    def get_serializer_context(self):
        context = super(GlueUser, self).get_serializer_context()
        # you have access to self.request here
        context.update({
            'kwargs': self.kwargs
        })

        return context

    def post_save(self, obj, created=False):
        Sync.objects.create(method='update_user', model_id=obj.id)
        task_request(obj, 'www.arooko.ngrok.com', 'update_user')


class ChangeDefault(generics.UpdateAPIView):
    def get_queryset(self):
        if self.kwargs.get('username') == self.request.user.username:
            return User.objects.all()
        raise generics.PermissionDenied

    serializer_class = ChangeDefaultSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'username'

    def post_save(self, obj, created=False):
        Sync.objects.create(method='update_user', model_id=obj.id)

        task_request(obj, 'www.arooko.ngrok.com', 'update_user')


class SessionView(APIView):
    error_messages = {
        'invalid': "Invalid username or password",
        'disabled': "Sorry, this account is suspended",
    }

    def _error_response(self, message_key):
        data = {
            'success': False,
            'message': self.error_messages[message_key],
            'user_id': None,
        }
        return Response(data)

    def get(self, request, *args, **kwargs):
        # Get the current user
        if request.user.is_authenticated():
            return Response({'user_id': request.user.id})
        return Response({'user_id': None})

    def post(self, request, *args, **kwargs):
        # Login
        #serializer = SessionSerializer(data=request.DATA)
        #if serializer.is_valid():
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return Response({'success': True, 'user_id': user.id})
            return self._error_response('disabled')
        return self._error_response('invalid')

        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        # Logout
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
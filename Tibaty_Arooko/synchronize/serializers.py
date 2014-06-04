from django.contrib.auth import get_user_model
from rest_framework import serializers
from wallet.models import OfflineWallet
from scheduler.models import Schedule
from transaction.models import Transaction

User = get_user_model()


class OfflineRegisterUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'id')  # the response values will be used in the online to change ack to True

    def restore_object(self, attrs, instance=None):
        """
        Instantiate a new Offline User instance.
        """
        assert instance is None, 'Cannot update users with OfflineRegisterUser'
        user = User(username=attrs['username'])
        user.is_active = True
        return user


class OfflineUserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'id')


class UpdateOfflineWalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfflineWallet
        fields = ('owner', 'id', 'amount')


class OfflineScheduleUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Schedule
        fields = ('user', 'id')


class CreateTransactionSerializer(serializers.ModelSerializer):
    phone_no = serializers.CharField(max_length=11)
    amount = serializers.FloatField(read_only=True)
    balance = serializers.FloatField(ead_only=True)
    cid = serializers.CharField(max_length=10, read_only=True)
    status = serializers.CharField(max_length=10, read_only=True)

    class Meta:
        model = Transaction
        fields = ()

    def restore_object(self, attrs, instance=None):
        """
        Instantiate a new online transaction instance.
        """
        assert instance is None, 'Cannot update users with CreateTransaction'
        transaction = Transaction(phone_no=attrs['phone_no'])
        return transaction


class TransactionUpdateSerializer(serializers.ModelSerializer):
    phone_no = serializers.CharField(max_length=11)
    amount = serializers.FloatField(read_only=True)
    balance = serializers.FloatField(ead_only=True)
    cid = serializers.CharField(max_length=10, read_only=True)
    status = serializers.CharField(max_length=10, read_only=True)

    class Meta:
        model = Transaction
        fields = ()







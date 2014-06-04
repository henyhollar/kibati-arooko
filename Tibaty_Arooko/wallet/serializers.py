from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Wallet, WalletLog
from register.user import UserBehaviour
from register.extra_field import PostModelSerializer

User = get_user_model()

def phoneCleaner(phone_no):
    prefix = ['07','08','09']
    if phone_no.isdigit() and len(phone_no)==11:
        if phone_no[0:2] in prefix:
            return True
        return False

class CheckBalanceSerializer(serializers.ModelSerializer):
    """
    API to check balance
    """
    class Meta:
        model = Wallet
        fields = ('amount',)


class UpdateWalletSerializer(serializers.ModelSerializer):
    """
    API to update wallet
    """
    uplink_username = serializers.CharField(max_length=11, min_length=11, required=False)

    class Meta:
        model = Wallet
        fields = ('amount', 'walletID')

    def validate_owner(self, attrs, source):
        phone_no = attrs[source]
        if not phoneCleaner(phone_no):
            raise serializers.ValidationError("Please check your phone no. the format is incorrect")

        return attrs

    def validate_uplink_username(self, attrs, source):
        phone_no = attrs[source]
        if not phoneCleaner(phone_no):
            raise serializers.ValidationError("Please check your phone no. the format is incorrect")

        return attrs

    def restore_object(self, attrs, instance=None):
        assert instance
        if self.context['kwargs'].get('uplink_user', False):
            uplink_wallet = Wallet.objects.get(owner=self.context['kwargs']['uplink_user'])
            uplink_wallet = UserBehaviour.subtract_from_wallet(uplink_wallet, attrs['amount'])
            uplink_wallet.save()

            instance = UserBehaviour.add_to_wallet(instance, attrs['amount'])
            return instance

        elif self.context['kwargs'].get('master_user', False):
            master_wallet = Wallet.objects.get(owner=self.context['kwargs']['master_user'])
            master_wallet = UserBehaviour.subtract_from_wallet(master_wallet, attrs['amount'])
            master_wallet.save()

            instance = UserBehaviour.add_to_wallet(instance, attrs['amount'])
            return instance

        instance = UserBehaviour.subtract_from_wallet(instance, attrs['amount'])
        return instance





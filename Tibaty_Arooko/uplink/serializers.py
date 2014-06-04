from django.contrib.auth import get_user_model
from rest_framework import serializers
from wallet.serializers import CheckBalanceSerializer
from register.user import UserBehaviour

User = get_user_model()

def phoneCleaner(phone_no):
    prefix = ['07','08','09']
    if phone_no.isdigit() and len(phone_no)==11:
        if phone_no[0:2] in prefix:
            return True
        return False

class UplinkRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=11, min_length=11)
    wallet = CheckBalanceSerializer(read_only=True)
    default_amt = serializers.FloatField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'default_amt', 'wallet')


    def validate_username(self, attrs, source):
        """
        this will validate the phone nos.
        """

        downlink_phone_no = attrs[source]

        if not phoneCleaner(downlink_phone_no):
            raise serializers.ValidationError("Please check your phone no., the format is incorrect")


        try:
            User.objects.get(username__iexact=downlink_phone_no)
        except User.DoesNotExist:
            return attrs
        raise serializers.ValidationError("You cannot register an existing no. You can only plug the bearer unto yourself online")


class PlugUserSerializer(serializers.ModelSerializer):
    class Meta:
        plug = serializers.IntegerField(required=False)
        model = User
        fields = ('plug',)

    def restore_object(self, attrs, instance=None):
        """
        toggle effect for de-plugging.
        """
        assert instance

        if self.context['kwargs'].get('uplink_user', False):
            user_behaviour = UserBehaviour(instance)
            user_behaviour.plug_into = self.context['kwargs']['uplink_user']
        else:
            user_behaviour = UserBehaviour(username=instance.username)
            instance = user_behaviour.unplug()

        return instance
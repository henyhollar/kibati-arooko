from django.contrib.auth import get_user_model
from rest_framework import serializers
from extra_field import PostModelSerializer
from wallet.serializers import CheckBalanceSerializer
from user import UserBehaviour


User = get_user_model()

def phoneCleaner(phone_no):
    prefix = ['07','08','09']
    if phone_no.isdigit() and len(phone_no)==11:
        if phone_no[0:2] in prefix:
            return True
        return False


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=11, min_length=11)
    #email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'id')

    def validate_username(self, attrs, source):
        """
        this will validate the phone no.
        """
        phone_no = attrs[source]
        if not phoneCleaner(phone_no):
            raise serializers.ValidationError("Please check your phone no. the format is incorrect")

        try:
            User.objects.get(username__iexact=phone_no)
        except User.DoesNotExist:
            return attrs
        raise serializers.ValidationError("Phone number already exists. If are trying to glue, consider the glue option")

    def restore_object(self, attrs, instance=None):
        """
        Instantiate a new User instance.
        """
        assert instance is None, 'Cannot update users with CreateUserSerializer'
        user = User(username=attrs['username'])
        user.is_active = True
        return user


class RegisterSlaveSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=11, min_length=11)
    slave = serializers.CharField(max_length=11, min_length=11)
    #email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'id')

    def validate_username(self, attrs, source):
        """
        this will validate the phone no.
        """
        phone_no = attrs[source]
        if not phoneCleaner(phone_no):
            raise serializers.ValidationError("Please check your phone no. the format is incorrect")

        try:
            us = User.objects.get(username__iexact=phone_no)
        except User.DoesNotExist:
            raise serializers.ValidationError("Phone number must already be registered before doing this")

        if us.hierarchy != 'master':
            raise serializers.ValidationError("Phone number must not be a slave to another user")

        return attrs

    def validate(self, attrs):
        """
        this will validate the phone no.
        """
        phone_no = self.context['kwargs'].get('slave')
        if not phoneCleaner(phone_no):
            raise serializers.ValidationError("Please check your phone no. the format is incorrect")

        try:
            User.objects.get(username__iexact=phone_no)
        except User.DoesNotExist:
            attrs.update({'slave': phone_no})
            return attrs
        raise serializers.ValidationError("Phone number already exists. If you are trying to glue, consider the glue option")

    def restore_object(self, attrs, instance=None):
        """
        Instantiate a new User instance.
        """
        assert instance is None, 'Cannot update users with CreateUserSerializer'
        user = User(username=attrs['slave'])
        user.is_active = True
        return user


class UpdateSerializer(serializers.ModelSerializer):
    """
    Update records
    """
    wallet = CheckBalanceSerializer(read_only=True)


    class Meta:
        model = User
        fields = ()

    def validate_email(self, attrs, source):
        email = attrs[source]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return attrs
        raise serializers.ValidationError('Email already exists')

    def validate_default_amt(self, attrs, source):
        default_amt = attrs[source]
        if default_amt >= 100:
            return attrs
        raise serializers.ValidationError('default_amt cannot be less that =N=100')




class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)

    def restore_object(self, attrs, instance=None):
        if instance.email is not " " or instance.email is not None:
            super(ChangePasswordSerializer, self).restore_object(attrs, instance)
        raise serializers.ValidationError('You must enter a valid email address where we will send your new password.')


class GlueUserSerializer(serializers.ModelSerializer):
    class Meta:
        glue = serializers.IntegerField(required=False)
        model = User
        fields = ('glue',)

    def restore_object(self, attrs, instance=None):
        assert instance
        if self.context['kwargs'].get('master_user', False):
            user_behaviour = UserBehaviour(instance)
            user_behaviour.glue_to = self.context['kwargs']['master_user']

        else:
            user_behaviour = UserBehaviour(username=instance.username, request=self.context['request'])
            instance = user_behaviour.unglue()

        return instance


class ChangeDefaultSerializer(serializers.ModelSerializer):
    class Meta:
        default_amt = serializers.FloatField(default=100.0)
        model = User
        fields = ('default_amt',)

    def validate_deault_amt(self, attrs, source):
        default_amt = attrs[source]
        if default_amt >= 100:
            return attrs
        raise serializers.ValidationError('The amount cannot be less than =N=100')

    def restore_object(self, attrs, instance=None):
        assert instance
        use_behaviour = UserBehaviour(instance)
        use_behaviour.default_amt = attrs['default_amt']

        return instance


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')

    def validate_username(self, attrs, source):
        print attrs
        username = attrs[source]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist yet. Click sign-up to register')
        return attrs

    def restore_object(self, attrs, instance=None):
        pass

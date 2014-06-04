from django.contrib.auth import get_user_model
from rest_framework import generics
from message.views import message_as_email, message_as_sms

User = get_user_model()

class UserBehaviour(object):
    def __init__(self, obj=None, username=None):
        if obj is None:
            self._obj = User.objects.get(username=username)
        else:
            self._obj = obj

    @property
    def get_hierarchy(self):
        """
        Gets the user who is the master
        """
        return self._obj.hierarchy

    @property
    def get_permission(self):
        """
        Gets the user who is the master
        """
        return self._obj.permission

    @property
    def plug_into(self):
        """
        Gets the user plugged to an uplink. The user in the setter is an instance of the uplink
        """
        return self._obj.plug

    @plug_into.setter
    def plug_into(self, user=None, create=False):
        if user is None:
            self._obj.permission = 'normal'
        else:
            self._obj.permission = 'downlink'

        self._obj.plug = user
        self._obj.ack = False

        if create:
            self._obj.save()


    @property
    def glue_to(self):
        """
        Gets the user glued to a master. The user in the setter is an instance of the master.
        """
        return self._obj.glue

    @glue_to.setter
    def glue_to(self, user=None, create=False):
        if user is None:
            self._obj.hierarchy = 'master'
            reset_password = User.objects.make_random_password(length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
            print reset_password
            #send to the user
            data = {
                'subject': 'Password Reset',
                'message': 'Dear customer, your new password is:' + reset_password + '. Have the best re-charging experience ever! ',
                'phone': self._obj.username
            }
            if self._obj.email is not None or self._obj.email is not ' ':
                self._obj.set_password(reset_password)
                message_as_email(data)
            else:
                raise generics.PermissionDenied


        else:
            self._obj.hierarchy = 'slave'
            self._obj.set_unusable_password()
            #send notification that the user can only log in with the master

        self._obj.glue = user
        self._obj.ack = False

        if create:
            self._obj.save()




    @property
    def default_amt(self):
        """
        Gets the user glued to a master. The user in the setter is an instance of the master.
        """
        return self._obj.default_amt

    @default_amt.setter
    def default_amt(self, amt=None, create=False):
        if amt < 100 or amt is None:
            self._obj.default_amt = 100
        else:
            self._obj.default_amt = amt

        self._obj.ack = False
        if create:
            self._obj.save()


    def become_uplink(self):
        pass#send a notification to admin after the user has filled a form and agreed with the terms and  conditions.

    @staticmethod
    def add_to_wallet(obj, amount):
        previous_amount = obj.amount
        obj.amount = previous_amount + amount
        if obj.amount < 0:
            raise generics.PermissionDenied
        obj.ack = False
        return obj

    @staticmethod
    def subtract_from_wallet(obj, amount):
        previous_amount = obj.amount
        obj.amount = previous_amount - amount
        if obj.amount < 0:
            raise generics.PermissionDenied
        obj.ack = False
        return obj


    def unglue(self, user=None, create=False):
        if user is None:
            self._obj.hierarchy = 'master'
            reset_password = User.objects.make_random_password(length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
            print reset_password
            #send to the user
            data = {
                'subject': 'Password Reset',
                'message': 'Dear customer, your new password is:' + reset_password + '. Have the best re-charging experience ever! ',
                'phone': self._obj.username
            }
            if self._obj.email is not None or self._obj.email is not ' ':
                self._obj.set_password(reset_password)
                message_as_email(data)
            else:
                raise generics.PermissionDenied

        else:
            self._obj.hierarchy = 'slave'
            self._obj.set_unusable_password()
            #send notification that the user can only log in with the master

        self._obj.glue = user
        self._obj.ack = False

        if create:
            self._obj.save()

        return self._obj

    def unplug(self, user=None, create=False):
        if user is None:
            self._obj.permission = 'normal'
        else:
            self._obj.permission = 'downlink'

        self._obj.plug = user
        self._obj.ack = False

        if create:
            self._obj.save()

        return self._obj





class UserGroups(object):
    def __init__(self, user_no, model):
        self.user_no = user_no
        self.model = model
        self.immediate_family_group = []
        self.extended_family_group = []
        self.glue_to = None
        self.plug_to = None
    def populate_family_group(self):
        user = self.model.objects.get(username=self.user_no)
        self.glue_to = user.glue
        self.plug_to = user.plug
        if self.glue_to:
            master_user = self.model.objects.get(id=self.glue_to)
            self.immediate_family_group.append(master_user)
            slave_user = self.model.objects.filter(glue=self.glue_to)
            for glued_user in slave_user:
                self.immediate_family_group.append(glued_user)

        if self.plug_to:
            uplink_user = self.model.objects.get(id=self.plug_to)
            self.extended_family_group.append(uplink_user)
            downlink_user = self.model.objects.filter(plug=self.plug_to)
            for plugged_user in downlink_user:
                self.extended_family_group.append(plugged_user)

        return self.immediate_family_group, self.extended_family_group


    @property
    def count_users_in_group(self, group_tuple_list):
        immediate, extended = group_tuple_list
        immediate_family_length = len(immediate)
        extended_family_length = len(extended)

        return immediate_family_length, extended_family_length













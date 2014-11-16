from django.db import models
from django.contrib.auth import get_user_model
import datetime
from pytz import utc

from Tibaty_Arooko.settings import base


class Wallet(models.Model):
        # the first place money paid will go into after which sync of wallet is carried out
        # then,the money will be moved to the amount field.
        # the front-end should display info like:
        # "You have paid a sum of N1000, we will update your overall balance soon. Note that you can continue using your
        # account normally, in as much as it does not exceed the amount you just paid.
        # We are sorry for the inconvenience. Thanks for your patronage!"
        # Calculator should be able to use tempo_amount if it is not zero and can cater for the amount requested for.
        owner = models.OneToOneField(base.AUTH_USER_MODEL, related_name='wallet', unique=True)
        amount = models.FloatField(default=0.0)
        tempo_amount = models.FloatField(default=0.0)
        datetime = models.DateTimeField(default=utc.localize(datetime.datetime.utcnow()))
        walletID = models.CharField(max_length=10, default="00000")
        ack = models.BooleanField(default=False)

        def __unicode__(self):
                return u'%s' % self.owner

        @property
        def set_ack(self):
            return self.ack

        @set_ack.setter
        def set_ack(self, bol):
            self.ack = bol


class WalletLog(models.Model):
        wallet = models.ForeignKey(Wallet)
        user_from = models.ForeignKey(base.AUTH_USER_MODEL, null=True, blank=True)
        amount = models.FloatField()    # saving the wallet balance at this time
        datetime = models.DateTimeField(default=utc.localize(datetime.datetime.utcnow()))
        report = models.CharField(max_length=100)


        def __unicode__(self):
                return u'%s' % self.wallet


class OfflineWallet(models.Model):
    owner = models.OneToOneField(base.AUTH_USER_MODEL, related_name='offlinewallet', unique=True)
    amount = models.FloatField(default=0.0)
    datetime = models.DateTimeField(default=utc.localize(datetime.datetime.utcnow()))
    ack = models.BooleanField(default=False)

    def __unicode__(self):
            return u'%s' % self.owner

    @property
    def set_ack(self):
        return self.ack

    @set_ack.setter
    def set_ack(self, bol):
        self.ack = bol


class OfflineWalletLog(models.Model):
        wallet = models.ForeignKey(OfflineWallet)
        user_from = models.ForeignKey(base.AUTH_USER_MODEL, null=True, blank=True)
        amount = models.FloatField()
        datetime = models.DateTimeField(default=utc.localize(datetime.datetime.utcnow()))
        report = models.CharField(max_length=100)


        def __unicode__(self):
                return u'%s' % self.wallet

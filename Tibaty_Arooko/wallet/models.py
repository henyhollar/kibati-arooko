from django.db import models
from django.contrib.auth import get_user_model
import datetime
from pytz import utc

from Tibaty_Arooko.settings import base


class Wallet(models.Model):
        owner = models.OneToOneField(base.AUTH_USER_MODEL, related_name='wallet', unique=True)
        amount = models.FloatField(default=0.0)
        datetime = models.DateTimeField(default=utc.localize(datetime.datetime.utcnow()))
        walletID = models.CharField(max_length=10,default="00000")
        ack = models.BooleanField(default=True)

        def __unicode__(self):
                return u'%s' %(self.owner)

        @property
        def set_ack(self):
            return self.ack

        @set_ack.setter
        def set_ack(self, bol):
            self.ack = bol


class WalletLog(models.Model):
        wallet = models.ForeignKey(Wallet)
        user_from = models.ForeignKey(base.AUTH_USER_MODEL, null=True, blank=True)
        amount = models.FloatField()
        datetime = models.DateTimeField(default=utc.localize(datetime.datetime.utcnow()))
        report = models.CharField(max_length=100)


        def __unicode__(self):
                return u'%s' %(self.wallet)


class OfflineWallet(models.Model):
    owner = models.OneToOneField(base.AUTH_USER_MODEL, related_name='offlinewallet', unique=True)
    amount = models.FloatField(default=0.0)
    datetime = models.DateTimeField(default=utc.localize(datetime.datetime.utcnow()))
    ack = models.BooleanField(default=True)

    def __unicode__(self):
            return u'%s' %(self.owner)

    @property
    def set_ack(self):
        return self.ack

    @set_ack.setter
    def set_ack(self, bol):
        self.ack = bol




from django.db import models
import datetime
from pytz import utc


class PendingMethod(models.Manager):
    def get(self, *args, **kwargs):
        super(PendingMethod, self).get(*args, **kwargs)


class UserTransaction(models.Manager):
    def filter(self, *args, **kwargs):
        super(UserTransaction, self).filter(*args, **kwargs)


class Transaction(models.Model):
    phone_no = models.CharField(max_length=11)
    recipient = models.CharField(max_length=11, blank=True)
    amount = models.FloatField()
    balance = models.FloatField(null=True, blank=True)   # balance of the phone for this transaction
    datetime = models.DateTimeField(default=utc.localize(datetime.datetime.utcnow()))
    cid = models.CharField(max_length=10)
    status = models.CharField(max_length=10)
    ack = models.BooleanField(default=False)

    objects = models.Manager()
    pending_method = PendingMethod()    # this will return the pending method based on the CID
    user_transactions = UserTransaction()  # this will build the user's log

    def __unicode__(self):
                return u'Transaction for %s' % self.phone_no

    @property
    def set_ack(self):
        return self.ack

    @set_ack.setter
    def set_ack(self, bol):
        self.ack = bol
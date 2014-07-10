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
    pin = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=10)    # ON/OFF/pending
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


class CardCounter(models.Manager):
    def count(self, network, category):
        return self.filter(network__iexact=network, category=category).count()


class CardManager(models.Manager):
    def getCard(self, network, category):
        return self.filter(network__iexact=network, category=category)[0]

    def delCard(self,ids):
        return self.get(id=ids).delete()


class Cards(models.Model):
    network = models.CharField(max_length=10)
    category = models.CharField(max_length=10)
    pin = models.CharField(max_length=30, unique=True)
    serial_no = models.CharField(max_length=30)
    datetime = models.DateTimeField(default=utc.localize(datetime.datetime.utcnow()))



    objects = models.Manager()
    counter = CardCounter()
    card = CardManager()

    def __unicode__(self):
        return u'%s %s %s' % (self.network, self.category, self.pin)


class Methods(models.Model):
    phone_no = models.CharField(max_length=11, default='08137474080')
    recipient = models.CharField(max_length=11, blank=True)
    amount = models.FloatField(default=0.0)
    cid = models.CharField(max_length=10)
    status = models.CharField(max_length=10, default='ON')    # ON/OFF/pending

    objects = models.Manager()

    def __unicode__(self):
                return u'Method %s' % self.phone_no

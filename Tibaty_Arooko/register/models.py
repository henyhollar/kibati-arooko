from django.db import models
from django.contrib.auth.models import AbstractUser



class ArookoUser(AbstractUser):
    #Identity
    location = models.CharField(max_length=100, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    interest = models.CharField(max_length=100, blank=True)
    birth_day = models.DateField(blank=True, null=True)

    #Account
    #wallet = models.FloatField(null=True, blank=True)#change to one to one key with the wallet app
    default_amt = models.FloatField(default=100.0)

    #Relationships
    plug = models.ForeignKey('self', null=True, blank=True, related_name='gulp')
    glue = models.ForeignKey('self', null=True, blank=True, related_name='eulg')

    #Status
    hierarchy = models.CharField(max_length=10, default='master')   # master/slave
    permission = models.CharField(max_length=10, default='normal')  # uplink/downlink/normal

    #State
    ack = models.BooleanField(default=False)  # this will be changed to True after offline registration
    status = models.CharField(max_length=20, default='clear')  # status will show pending if the user has not accepted
                                                                # a glue or a plug

    @property
    def set_ack(self):
        return self.ack

    @set_ack.setter
    def set_ack(self, bol):
        self.ack = bol


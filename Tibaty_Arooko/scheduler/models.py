from django.db import models
from Tibaty_Arooko.settings import base
from django.utils import dates
from datetime import datetime, timedelta
from pytz import utc


class Schedule(models.Model):
    user = models.ForeignKey(base.AUTH_USER_MODEL, related_name='schedule', unique=True)
    amount = models.FloatField()
    date = models.DateField(default=datetime.utcnow().date())
    time = models.TimeField(default=datetime.utcnow().time())
    frequency = models.IntegerField(default=0)  # yearly not allowed
    due_dates = models.CommaSeparatedIntegerField(default=0, max_length=31) # with this, the start date (above) will have to be the first of the registered days.
    type = models.CharField(default='normal', max_length=10)
    phone_no = models.CharField(max_length=11, blank=True)
    status = models.BooleanField(default=False)  # active or de-active
    ack = models.BooleanField(default=True)

    def __unicode__(self):
                return u'%s:%s' % (self.user, self.status)

    @property
    def set_ack(self):
        return self.ack

    @set_ack.setter
    def set_ack(self, bol):
        self.ack = bol


def getSchedule():
    start = datetime.now()
    end = start + timedelta(hours=1)

    schedule = Schedule.objects.filter(date=start.date(), time__range=(start.time(), end.time()), status=True)

    return schedule

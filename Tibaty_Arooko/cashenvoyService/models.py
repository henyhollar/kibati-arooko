from django.db import models

class CELog(models.Model):
    wallet = models.IntegerField()
    walletID = models.CharField(max_length=9,default="000000000")
    request_amount = models.FloatField(default=0.0)
    confirmed_amount = models.FloatField(default=0.0)
    datetime = models.DateTimeField(default=utc.localize(datetime.datetime.utcnow()))
    status = models.CharField(max_length=15,default="pending")


    def __unicode__(self):
            return u'%s %s' %(self.wallet,self.status)

    class Meta:
            ordering = ["datetime"]

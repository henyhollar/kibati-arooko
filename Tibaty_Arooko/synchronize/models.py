from django.db import models


class Sync(models.Model):
    method = models.CharField(max_length=20)
    model_id = models.SmallIntegerField()
    ack = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s:%s' % (self.method, self.ack)

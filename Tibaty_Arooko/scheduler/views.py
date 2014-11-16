from django.contrib.auth import get_user_model
from rest_framework import generics
from models import Schedule
from serializers import ScheduleSerializer
from synchronize.tasks import task_request
from synchronize.models import Sync

User = get_user_model()


class Scheduler(generics.RetrieveUpdateAPIView):
    def get_queryset(self):
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except:
            raise generics.PermissionDenied

        self.kwargs.update({'user': user})

        return Schedule.objects.all()

    serializer_class = ScheduleSerializer
    #permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'user'

    def post_save(self, obj, created=False):
        Sync.objects.create(method='update_schedule', model_id=obj.id)      # sync into sync db

        task_request(obj, 'www.arooko.ngrok.com', 'update_schedule')    # will do it immediately unless network down


#use celery to coordinate the schedule


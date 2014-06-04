from django.contrib.auth import get_user_model
from rest_framework import generics
from models import Schedule
from serializers import ScheduleSerializer

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
        pass#send notification to the offline


#use celery to coordinate the schedule


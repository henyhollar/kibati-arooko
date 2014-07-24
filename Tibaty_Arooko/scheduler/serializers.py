from rest_framework import serializers
from models import Schedule
from django.contrib.auth import get_user_model

User = get_user_model()

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        exclude = ('user',)

    def validate_type(self, attrs, source):
        type = attrs[source]
        print type
        if type == 'share':
            print attrs
            print attrs.get('phone_no', None)
            if not attrs.get('phone_no', None):
                raise serializers.ValidationError('You must enter the phone no. to share to')

        return attrs

    def validate_due_dates(self, attrs, source):
        due_dates = attrs[source]
        for date in due_dates.split(','):
            if not int(date) in range(0,32):
                raise serializers.ValidationError('One of the entered dates is not valid')

        return attrs


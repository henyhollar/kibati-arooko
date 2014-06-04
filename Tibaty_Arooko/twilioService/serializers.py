from rest_framework import serializers
from twilio.util import RequestValidator

class TwilioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ""
        fields = ()

    def validate(self, attrs):
        AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'

        validator = RequestValidator(AUTH_TOKEN)

        # the callback URL you provided to Twilio
        url = "http://www.example.com/my/callback/url.xml"

        # the POST variables attached to the request (eg "From", "To")
        post_vars = {}

        # X-Twilio-Signature header value
        signature = "HpS7PBa1Agvt4OtO+wZp75IuQa0=" # will look something like that

        if validator.validate(url, post_vars, signature):
            print "Confirmed to have come from Twilio."
        else:
            print "NOT VALID.  It might have been spoofed!"

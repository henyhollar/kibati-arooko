from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from twilio.rest import TwilioRestClient
from twilio import twiml
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from serializers import TwilioSerializer
from rest_framework.renderers import XMLRenderer
from django.http import HttpResponse


User = get_user_model()

class Twilio_Make_Call(object):

    ACCOUNT_SID = "ACaaf2e00da34e30a4b95ca240fbf63dd8"
    AUTH_TOKEN = "d0b4cb31251be18af6ba06517b923ab3"

    def __init__(self):
        self.client = TwilioRestClient(self.ACCOUNT_SID, self.AUTH_TOKEN)

    def make_call(self):
        call = self.client.calls.create(to="+2348137474080", from_="+19292276656", url="https://67dae643.ngrok.com/call/.xml", method="GET")
        print call.length
        print call.sid


class Call(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    renderer_classes = (XMLRenderer, )
    def get(self, request, format='.xml'):
        return HttpResponse('''<Response><Reject reason='busy' /></Response>''', content_type="text/xml")


    def post(self, request, format='.xml'):
        # get user's info like the default_amt if amt is not included and update log and wallet
        #Note that this will do the online transaction
        username = request.DATA['From']
        print username
        #snippet = self.get_object(username)
        #serializer = TwilioSerializer(snippet, data=request.DATA)
        #if serializer.is_valid():
        #    serializer.save()
        #    return Response(serializer.data)

        return HttpResponse('''<Response><Reject reason='busy' /></Response>''', content_type="text/xml")


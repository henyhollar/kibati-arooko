from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
import urllib,httplib
from django.contrib.auth import get_user_model
import random

User = get_user_model()


#def extra_info(f):#this for one recipient
#        def wrapper(self, sender, msg, recipient_list, sig=None):
#                if '08189091170' in recipient_list:
#                        return f(self, sender, msg, recipient_list,sig=None)
#                try:
#                        user = User.objects.get(username=recipient_list)
#                except:
#                         pass
#
#                #get msg with location and occupation combination
#                obj = Massager.msg_objects.getMsg()
#                message = obj.msg
#                msg = msg+" "+message
#
#                return f(self,sender, msg, recipient_list,sig=None)
#        return wrapper


class messanger(object):
        #@extra_info
        def __init__(self, sender, msg, recipient_list, sig=None):
                self.headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
                self.conn = None
                self.parameter = None
                self.api_list = ['aratext_api','smsmobile24_api']
                self.sender = sender
                self.message = msg
                self.recipients = recipient_list
                self.count = 0

                self.apiChangeOver()
        def apiChangeOver(self):
                self.count += 1
                random.shuffle(self.api_list)
                for obj in self.api_list:
                        api_instance = eval(obj)(self.sender,self.message,self.recipients)
                        self.parameter = api_instance.paramGenerator()
                        self.conn = httplib.HTTPConnection(api_instance.domain)
                        self.conn.request("POST", api_instance.url, self.parameter, self.headers)
                        response = self.conn.getresponse()
                        #print response.read()
                        if response.status == 200 or 'ok' in response:
                                break
                        else:
                                if self.count <= 5:
                                        self.apiChangeOver()

                return



class aratext_api(object):
	def __init__(self, sender, msg, recipient_list):
		self.domain = "api.aratext.com"
		self.url = "/http/sendmessage/?"
		self.username = "henyhollar"
		self.password = "olatunbosun"
		self.sender = sender
		self.message = msg
		self.recipients = recipient_list

	def paramGenerator(self):
		param = {'username':self.username, 'password':self.password, 'message':self.message, 'recipients':self.recipients, 'sender':self.sender}
		parameter = urllib.urlencode(param)
		return parameter


class smsmobile24_api(object):
        def __init__(self, sender, msg, recipient_list):
                self.domain = "smsmobile24.com"
                self.url = "/components/com_smsreseller/smsapi.php?"
                self.username = "henyhollar"
                self.password = "olatunbosun"
                self.sender = sender
                self.message = msg
                self.recipient = recipient_list
        def paramGenerator(self):
                param = {'username':self.username, 'password':self.password, 'sender':self.sender, 'recipient':self.recipient, 'message':self.message}
                parameter = urllib.urlencode(param)
                return parameter


#attach a decorator here to reformat the message into a beautiful html.
def message_as_email(data):
        send_mail(data['subject'], data['message'], 'info@arooko.com', data['recipient'], fail_silently=True)


def message_as_sms(data):
         messanger('arookoSMS', data['message'], data['phone'])


def message(request):
    message_as_sms(request.POST['data'])
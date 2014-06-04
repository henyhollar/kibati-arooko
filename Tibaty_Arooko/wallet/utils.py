from cloudmailin.views import MailHandler
from django.http import HttpResponseNotFound
from django.contrib.auth import get_user_model
from .models import Wallet, WalletLog

from pytz import utc
import datetime
import re


User = get_user_model()


def extract_mail(**mail):
    agent = mail['from']
    if agent == 'gens@gtbank.com':
        subject = mail['subject']
        content = mail['plain']
        
        data = content_extractor(content)
       
        if data['account'] == '0113011666':
            if subject.find('Credit') != -1:
                try:
                    obj = Wallet.objects.get(walletID=data['walletID'])
                    obj.amount = obj.amount + data['amount']
                    obj.datetime = utc.localize(datetime.datetime.strptime(data['date']+" "+data['time'], '%d-%b-%Y %I:%M%p'))
                    obj.ack = True
                    obj.save()

                    wall = WalletLog(wallet=obj, amount=data['amount'], datetime=utc.localize(datetime.datetime.utcnow()), report='savings')
                    wall.save()

                except Wallet.DoesNotExist:
                    return HttpResponseNotFound()


            elif subject.find('Debit') != -1:
                return HttpResponseNotFound()

        else:
            return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()
        


mail_handler = MailHandler()
mail_handler.register_address(
    address='1784db76d41557bd1385@cloudmailin.net',
    secret='c6f79f44035efd74581c',
    callback=extract_mail
)




def content_extractor(content):
    try:
        tmatch = re.search(r'Account Number[\t:,.0-9 ]+',content, re.IGNORECASE)#[\t:,.0-9 ]+
        account = (re.sub('[\t:,.a-zA-Z ]+', '', tmatch.group()))

        tmatch = re.search(r'Amount[\t:,.0-9 ]+',content, re.IGNORECASE)#[\t:,.0-9 ]+
        amount = float(re.sub('[\t:,a-zA-Z ]+', '', tmatch.group()))

        tmatch = re.search(r'Value Date[-\t:0-9a-zA-Z ]{15}',content, re.IGNORECASE)#[\t:,.0-9 ]+
        date = re.sub('[\t ]+', '', tmatch.group())
        date = date.strip('Value Date :')
        try:
            tmatch = re.search(r'#\d+#',content, re.IGNORECASE)
            walletID = re.sub('#', '', tmatch.group())
        except:
            walletID=" "
        tmatch = re.search(r'Time of Transaction[\t:0-9A-Z ]{12}',content, re.IGNORECASE)#[\t:,.0-9 ]+
        time = re.sub('[\t ]+', '', tmatch.group())
        time = time.strip('Time of Transaction :')

        tmatch = re.search(r'[\t:,.0-9 ]+Naira',content, re.IGNORECASE)#[\t\n:,.0-9 ]+
        balance = float(re.sub('[\t:,a-zA-Z ]+', '', tmatch.group()))

        data = {'amount':amount,'balance':balance,'walletID':walletID,'account':account,'date':date,'time':time}
        
    except:
        data = {'amount':0.0,'balance':0.0,'walletID':'','account':'','date':'','time':''}
        return data
        
    return data

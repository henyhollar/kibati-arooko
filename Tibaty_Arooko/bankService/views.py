from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from wallet.models import Wallet

from os import environ

User = get_user_model()

#note that the cloudmailin service will call the wallet utils by itself after receiving an email from the bank

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def gtPay(request, format=None):
    account_no = environ.get('GTBANK_ACCOUNT_NUMBER')

    walletID = User.objects.make_random_password(length=5, allowed_chars='123456789')

    if Wallet.objects.filter(walletID=walletID):
            walletID = User.objects.make_random_password(length=5, allowed_chars='123456789')

    Wallet.objects.filter(username=request.user.username).update(walletID=walletID, ack=False)

    walletID = '#'+str(walletID)+'#'

    data = {'account_no':account_no,'walletID':walletID}

    return Response(data)

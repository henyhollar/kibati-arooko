from django.contrib.auth import get_user_model
from .utils import check_status
from wallet.models import OfflineWallet

User = get_user_model()


@check_status
def beeper(request, data):

    return data


@check_status
def messageRequest(request, data):

    return data


def calculate(request, data):
    if 'stop' in data:
        return data

    user = User.objects.get(username=data['phone'])
    user_offline_wallet = OfflineWallet.objects.get(owner=user.offlinewallet)
    if (float(user_offline_wallet) >= 100.0) and (float(user_offline_wallet) >= float(data['amount'])):
        new_wallet_amount = float(user_offline_wallet.amount) - float(data['amount'])
        OfflineWallet.objects.filter(owner=user.offlinewallet).update(amount=new_wallet_amount)
        data.update({'balance': new_wallet_amount})

    elif (float(user_offline_wallet) >= 100.0) and (float(user_offline_wallet) < float(data['amount'])):
        data.update({'amount': user_offline_wallet})
        new_wallet_amount = float(user_offline_wallet.amount) - float(data['amount'])
        OfflineWallet.objects.filter(owner=user.offlinewallet).update(amount=new_wallet_amount)
        data.update({'balance': new_wallet_amount})

    elif data['status'] is 'slave':
        offline_wallet = OfflineWallet.objects.get(owner=data['master'].offlinewallet)
        new_wallet_amount = float(offline_wallet.amount) - float(data['amount'])
        OfflineWallet.objects.filter(owner=data['master'].offlinewallet).update(amount=new_wallet_amount)
        data.update({'master_balance': new_wallet_amount})

    else:
        data.update({'stop': 'not enough balance in the account'})

    return data
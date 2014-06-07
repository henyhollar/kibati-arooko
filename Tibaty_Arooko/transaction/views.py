from django.contrib.auth import get_user_model
from .utils import check_status
from wallet.models import OfflineWallet, Wallet

User = get_user_model()


@check_status
def beepRequest(request, data):

    return data


@check_status
def messageRequest(request, data):

    return data


@check_status
def cardRequest(request, data):

    return data


def calculator(request, data):
    """
        calculator calculates the remainder for a user. It goes a step further if the person is a
        slave to a master by deducting from the master's wallet.
    """
    if 'stop' in data:
        return data

    user = User.objects.get(username=data['phone'])

    wallet_to_update = Wallet.objects.filter(owner=user) if data['platform'] is 'online' \
        else OfflineWallet.objects.filter(owner=user)

    user_wallet = wallet_to_update.get(owner=user)

    if (float(user_wallet.amount) >= 100.0) and (float(user_wallet.amount) >= float(data['amount'])):
        new_wallet_amount = float(user_wallet.amount) - float(data['amount'])

    elif (float(user_wallet.amount) >= 100.0) and (float(user_wallet.amount) < float(data['amount'])):
        data.update({'amount': user_wallet.amount})
        new_wallet_amount = float(user_wallet.amount) - float(data['amount'])

    elif data['status'] is 'slave':
        wallet_to_update = Wallet.objects.filter(owner=data['master']) if data['platform'] == 'online'\
            else OfflineWallet.objects.get(owner=data['master'])

        master_wallet = wallet_to_update.get(owner=data['master'])

        if (float(master_wallet.amount) >= 100.0) and (float(master_wallet.amount) >= float(data['amount'])):
            new_wallet_amount = float(master_wallet.amount) - float(data['amount'])
        elif (float( master_wallet.amount) >= 100.0) and (float( master_wallet.amount) < float(data['amount'])):
            data.update({'amount':  master_wallet.amount})
            new_wallet_amount = float(master_wallet.amount) - float(data['amount'])
        else:
            data.update({'stop': 'not enough balance in the account'})
            return data

    else:
        data.update({'stop': 'not enough balance in the account'})
        return data

    wallet_to_update.update(amount=new_wallet_amount)

    data.update({'balance': new_wallet_amount})

    return data
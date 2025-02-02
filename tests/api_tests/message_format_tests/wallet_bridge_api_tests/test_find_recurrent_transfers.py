import pytest

from test_tools import Asset, exceptions

from .local_tools import as_string


@pytest.mark.parametrize(
    'reward_fund_name', [
        'alice',
        'bob',
    ]
)
def test_find_recurrent_transfers_with_correct_value(node, wallet, reward_fund_name):
    create_accounts_and_make_recurrent_transfer(wallet, from_account='alice', to_account='bob')

    node.api.wallet_bridge.find_recurrent_transfers(reward_fund_name)


INCORRECT_VALUES = [
    'non-exist-acc',
    '',
    100,
    True,
]


@pytest.mark.parametrize(
    'reward_fund_name', [
        *INCORRECT_VALUES,
        *as_string(INCORRECT_VALUES),
    ]
)
def test_find_recurrent_transfers_with_incorrect_value(node, reward_fund_name):
    with pytest.raises(exceptions.CommunicationError):
        node.api.wallet_bridge.find_recurrent_transfers(reward_fund_name)


@pytest.mark.parametrize(
    'reward_fund_name', [
        ['alice']
    ]
)
def test_find_recurrent_transfers_with_incorrect_type_of_argument(node, wallet, reward_fund_name):
    create_accounts_and_make_recurrent_transfer(wallet, from_account='alice', to_account='bob')

    with pytest.raises(exceptions.CommunicationError):
        node.api.wallet_bridge.find_recurrent_transfers(reward_fund_name)


def test_find_recurrent_transfers_with_additional_argument(node, wallet):
    create_accounts_and_make_recurrent_transfer(wallet, from_account='alice', to_account='bob')

    node.api.wallet_bridge.find_recurrent_transfers('alice', 'additional_argument')


def create_accounts_and_make_recurrent_transfer(wallet, from_account, to_account):
    with wallet.in_single_transaction():
        wallet.api.create_account('initminer', from_account, '{}')
        wallet.api.create_account('initminer', to_account, '{}')

    wallet.api.transfer_to_vesting('initminer', from_account, Asset.Test(100))
    wallet.api.transfer('initminer', from_account, Asset.Test(500), 'memo')
    wallet.api.recurrent_transfer(from_account, to_account, Asset.Test(20), 'memo', 100, 10)

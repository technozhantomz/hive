import pytest

from test_tools import exceptions

from .local_tools import as_string


ACCOUNTS = [f'account-{i}' for i in range(3)]

CORRECT_VALUES = [
    [''],
    ['non-exist-acc'],
    [ACCOUNTS[0]],
    ACCOUNTS,
    [100],
    [True],
]


@pytest.mark.parametrize(
    'rc_accounts', [
        *CORRECT_VALUES,
        *as_string(CORRECT_VALUES),
    ]
)
def test_find_rc_accounts_with_correct_value(node, wallet, rc_accounts):
    wallet.create_accounts(len(ACCOUNTS))
    node.api.wallet_bridge.find_rc_accounts(rc_accounts)


@pytest.mark.parametrize(
    'rc_accounts', [
        "['non-exist-acc']",
        True,
        100,
        '100',
        'incorrect_string_argument',
    ]
)
def test_find_rc_accounts_with_incorrect_type_of_argument(node, rc_accounts):
    with pytest.raises(exceptions.CommunicationError):
        node.api.wallet_bridge.find_rc_accounts(rc_accounts)

import pytest

from test_tools import exceptions

from .local_tools import as_string, create_account_and_create_order


CORRECT_VALUES = [
        0,
        10,
        500,
    ]


@pytest.mark.parametrize(
    'orders_limit', [
        * CORRECT_VALUES,
        *as_string(CORRECT_VALUES),
        True,  # bool is treated like numeric (0:1)
    ]
)
def test_get_order_book_with_correct_value(node, wallet, orders_limit):
    create_account_and_create_order(wallet, account_name='alice')
    node.api.wallet_bridge.get_order_book(orders_limit)


@pytest.mark.parametrize(
    'orders_limit', [
        -1,
        501,
    ]
)
def test_get_order_book_with_incorrect_value(node, orders_limit):
    with pytest.raises(exceptions.CommunicationError):
        node.api.wallet_bridge.get_order_book(orders_limit)


@pytest.mark.parametrize(
    'orders_limit', [
        [0],
        'incorrect_string_argument',
        'true'
    ]
)
def test_get_order_book_with_incorrect_type_of_argument(node, orders_limit):
    with pytest.raises(exceptions.CommunicationError):
        node.api.wallet_bridge.get_order_book(orders_limit)

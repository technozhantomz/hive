import pytest

from test_tools import exceptions


def test_sign_legacy_transaction_with_hf26_wallet(wallet_with_legacy_serialization, wallet_with_hf26_serialization):
    legacy_transaction = wallet_with_legacy_serialization.api.create_account('initminer', 'alice', '{}', broadcast=False)
    wallet_with_hf26_serialization.api.sign_transaction(legacy_transaction)


def test_sign_hf26_transaction_with_legacy_wallet(wallet_with_legacy_serialization, wallet_with_hf26_serialization):
    hf26_transaction = wallet_with_hf26_serialization.api.create_account('initminer', 'alice', '{}', broadcast=False)
    with pytest.raises(exceptions.CommunicationError):
        wallet_with_legacy_serialization.api.sign_transaction(hf26_transaction)

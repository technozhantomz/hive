import pytest

import test_tools as tt

from .local_tools import test_asset_serialization, Mismatched


@test_asset_serialization(_100_tests=tt.Asset.Test(100), _100_tbd=tt.Asset.Tbd(100))
def test_transfer_matched(prepared_wallet, _100_tests, _100_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer('initminer', 'alice', _100_tests, 'memo')
    prepared_wallet.api.transfer('initminer', 'alice', _100_tbd, 'memo')


@test_asset_serialization(_100_tests=Mismatched(tt.Asset.Test(100)), _100_tbd=Mismatched(tt.Asset.Tbd(100)))
def test_transfer_mixed(prepared_wallet, _100_tests, _100_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.transfer('initminer', 'alice', _100_tests, 'memo')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.transfer('initminer', 'alice', _100_tbd, 'memo')


@test_asset_serialization(_100_tests=tt.Asset.Test(100), _100_tbd=tt.Asset.Tbd(100))
def test_transfer_nonblocking_matched(prepared_wallet, _100_tests, _100_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer_nonblocking('initminer', 'alice', _100_tests, 'memo')
    prepared_wallet.api.transfer_nonblocking('initminer', 'alice', _100_tbd, 'memo')


@test_asset_serialization(_100_tests=Mismatched(tt.Asset.Test(100)), _100_tbd=Mismatched(tt.Asset.Tbd(100)))
def test_transfer_nonblocking_mixed(prepared_wallet, _100_tests, _100_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.transfer_nonblocking('initminer', 'alice', _100_tests, 'memo')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.transfer_nonblocking('initminer', 'alice', _100_tbd, 'memo')


@test_asset_serialization(_1_tbd=tt.Asset.Tbd(1), _2_tests=tt.Asset.Test(2))
def test_escrow_transfer_matched(prepared_wallet, _1_tbd, _2_tests):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    prepared_wallet.api.escrow_transfer('initminer', 'alice', 'bob', 99, _1_tbd, _2_tests, _1_tbd,
                                        '2029-06-02T00:00:00', '2029-06-02T01:01:01', '{}')


@test_asset_serialization(_1_tbd=Mismatched(tt.Asset.Tbd(1)), _2_tests=Mismatched(tt.Asset.Test(2)))
def test_escrow_transfer_mixed(prepared_wallet, _1_tbd, _2_tests):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.escrow_transfer('initminer', 'alice', 'bob', 99, _1_tbd, _2_tests, _1_tbd,
                                            '2029-06-02T00:00:00', '2029-06-02T01:01:01', '{}')


@test_asset_serialization(_1_tbd=tt.Asset.Tbd(1), _2_tests=tt.Asset.Test(2), _50_tests=tt.Asset.Test(50))
def test_escrow_release_matched(prepared_wallet, _1_tbd, _2_tests, _50_tests):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _50_tests)
        prepared_wallet.api.transfer_to_vesting('initminer', 'bob', _50_tests)

    prepared_wallet.api.escrow_transfer('initminer', 'alice', 'bob', 99, _1_tbd, _2_tests, _1_tbd,
                                        '2029-06-02T00:00:00', '2029-06-02T01:01:01', '{}')

    prepared_wallet.api.escrow_approve('initminer', 'alice', 'bob', 'bob', 99, True)

    prepared_wallet.api.escrow_approve('initminer', 'alice', 'bob', 'alice', 99, True)

    prepared_wallet.api.escrow_dispute('initminer', 'alice', 'bob', 'initminer', 99)

    prepared_wallet.api.escrow_release('initminer', 'alice', 'bob', 'bob', 'alice', 99, _1_tbd, _2_tests)


@test_asset_serialization(_1_tbd_mismatched=Mismatched(tt.Asset.Tbd(1)),
                          _2_tests_mismatched=Mismatched(tt.Asset.Test(2)), _1_tbd=tt.Asset.Tbd(1),
                          _2_tests=tt.Asset.Test(2), _50_tests=tt.Asset.Test(50))
def test_escrow_release_mixed(prepared_wallet, _1_tbd_mismatched, _2_tests_mismatched, _1_tbd, _2_tests,
                              _50_tests):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _50_tests)
        prepared_wallet.api.transfer_to_vesting('initminer', 'bob', _50_tests)

    prepared_wallet.api.escrow_transfer('initminer', 'alice', 'bob', 99, _1_tbd, _2_tests, _1_tbd,
                                        '2029-06-02T00:00:00', '2029-06-02T01:01:01', '{}')

    prepared_wallet.api.escrow_approve('initminer', 'alice', 'bob', 'bob', 99, True)

    prepared_wallet.api.escrow_approve('initminer', 'alice', 'bob', 'alice', 99, True)

    prepared_wallet.api.escrow_dispute('initminer', 'alice', 'bob', 'initminer', 99)

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.escrow_release('initminer', 'alice', 'bob', 'bob', 'alice', 99, _1_tbd_mismatched,
                                           _2_tests_mismatched)


# po ulepszeniu Piotrka będziemy przyśpieszać
@test_asset_serialization(_0_tests=tt.Asset.Test(0))
def test_claim_account_creation_matched(node, prepared_wallet, _0_tests):
    node.wait_number_of_blocks(18)
    prepared_wallet.api.claim_account_creation('initminer', _0_tests)


# po ulepszeniu Piotrka będziemy przyśpieszać
@test_asset_serialization(_0_tests=Mismatched(tt.Asset.Test(0)))
def test_claim_account_creation_mixed(node, prepared_wallet, _0_tests):
    node.wait_number_of_blocks(18)
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.claim_account_creation('initminer', _0_tests)


# po ulepszeniu Piotrka będziemy przyśpieszać
@test_asset_serialization(_0_tests=tt.Asset.Test(0))
def test_claim_account_creation_nonblocking_matched(node, prepared_wallet, _0_tests):
    node.wait_number_of_blocks(18)
    prepared_wallet.api.claim_account_creation_nonblocking('initminer', _0_tests)


# po ulepszeniu Piotrka będziemy przyśpieszać
@test_asset_serialization(_0_tests=Mismatched(tt.Asset.Test(0)))
def test_claim_account_creation_nonblocking_mixed(node, prepared_wallet, _0_tests):
    node.wait_number_of_blocks(18)
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.claim_account_creation_nonblocking('initminer', _0_tests)


@test_asset_serialization(_2_tests=tt.Asset.Test(2))
def test_create_funded_account_with_keys_matched(node, prepared_wallet, _2_tests):
    key = 'TST8grZpsMPnH7sxbMVZHWEu1D26F3GwLW1fYnZEuwzT4Rtd57AER'
    prepared_wallet.api.create_funded_account_with_keys('initminer', 'alice2', _2_tests, 'memo', '{}', key, key, key, key)


@test_asset_serialization(_2_tests=Mismatched(tt.Asset.Test(2)))
def test_create_funded_account_with_keys_mixed(node, prepared_wallet, _2_tests):
    key = 'TST8grZpsMPnH7sxbMVZHWEu1D26F3GwLW1fYnZEuwzT4Rtd57AER'
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.create_funded_account_with_keys('initminer', 'alice2', _2_tests, 'memo', '{}', key, key, key,
                                                            key)


@test_asset_serialization(_50_tests=tt.Asset.Test(50), _1_vest=tt.Asset.Vest(1))
def test_delegate_vesting_shares_matched(node, prepared_wallet, _50_tests, _1_vest):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _50_tests)
    prepared_wallet.api.delegate_vesting_shares('alice', 'bob', _1_vest)


@test_asset_serialization(_50_tests=tt.Asset.Test(50), _1_vest=Mismatched(tt.Asset.Vest(1)))
def test_delegate_vesting_shares_mixed(node, prepared_wallet, _50_tests, _1_vest):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _50_tests)
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.delegate_vesting_shares('alice', 'bob', _1_vest)


@test_asset_serialization(_50_tests=tt.Asset.Test(50), _1_vest=tt.Asset.Vest(1))
def test_delegate_vesting_shares_nonblocking_matched(node, prepared_wallet, _50_tests, _1_vest):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _50_tests)
    prepared_wallet.api.delegate_vesting_shares_nonblocking('alice', 'bob', _1_vest)


@test_asset_serialization(_50_tests=tt.Asset.Test(50), _1_vest=Mismatched(tt.Asset.Vest(1)))
def test_delegate_vesting_shares_nonblocking_mixed(node, prepared_wallet, _50_tests, _1_vest):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _50_tests)
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.delegate_vesting_shares_nonblocking('alice', 'bob', _1_vest)


@test_asset_serialization(_50_tests=tt.Asset.Test(50), _1_vest=tt.Asset.Vest(1), _6_tests=tt.Asset.Test(6))
def test_delegate_vesting_shares_and_transfer_matched(node, prepared_wallet, _50_tests, _1_vest, _6_tests):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _50_tests)
        prepared_wallet.api.transfer('initminer', 'alice', _50_tests, 'memo')

    prepared_wallet.api.delegate_vesting_shares_and_transfer('alice', 'bob', _1_vest, _6_tests, 'transfer_memo')


@test_asset_serialization(_50_tests=tt.Asset.Test(50), _1_vest=Mismatched(tt.Asset.Vest(1)),
                          _6_tests=Mismatched(tt.Asset.Test(6)))
def test_delegate_vesting_shares_and_transfer_mixed(node, prepared_wallet, _50_tests, _1_vest, _6_tests):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _50_tests)
        prepared_wallet.api.transfer('initminer', 'alice', _50_tests, 'memo')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.delegate_vesting_shares_and_transfer('alice', 'bob', _1_vest, _6_tests,
                                                                 'transfer_memo')


@test_asset_serialization(_50_tests=tt.Asset.Test(50), _1_vest=tt.Asset.Vest(1), _6_tbd=tt.Asset.Test(6))
def test_delegate_vesting_shares_and_transfer_nonblocking_matched(node, prepared_wallet, _50_tests, _1_vest, _6_tbd):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _50_tests)
        prepared_wallet.api.transfer('initminer', 'alice', _50_tests, 'memo')

    prepared_wallet.api.delegate_vesting_shares_and_transfer_nonblocking('alice', 'bob', _1_vest, _6_tbd,
                                                                         'transfer_memo')


@test_asset_serialization(_50_tests=tt.Asset.Test(50), _1_vest=Mismatched(tt.Asset.Vest(1)),
                          _6_tbd=Mismatched(tt.Asset.Test(6)))
def test_delegate_vesting_shares_and_transfer_nonblocking_mixed(node, prepared_wallet, _50_tests, _1_vest, _6_tbd):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _50_tests)
        prepared_wallet.api.transfer('initminer', 'alice', _50_tests, 'memo')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.delegate_vesting_shares_and_transfer_nonblocking('alice', 'bob', _1_vest, _6_tbd,
                                                                             'transfer_memo')


@test_asset_serialization(_100_tests=tt.Asset.Test(100))
def test_transfer_to_vesting_matched(prepared_wallet, _100_tests):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _100_tests)


@test_asset_serialization(_100_tests=Mismatched(tt.Asset.Test(100)))
def test_transfer_to_vesting_nonblocking_mixed(prepared_wallet, _100_tests):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.transfer_to_vesting_nonblocking('initminer', 'alice', _100_tests)


@test_asset_serialization(_100_tests=tt.Asset.Test(100))
def test_transfer_to_vesting_nonblocking_matched(prepared_wallet, _100_tests):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer_to_vesting_nonblocking('initminer', 'alice', _100_tests)


@test_asset_serialization(_100_tests=Mismatched(tt.Asset.Test(100)))
def test_transfer_to_vesting_mixed(prepared_wallet, _100_tests):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _100_tests)


@test_asset_serialization(_100_tests=tt.Asset.Test(100), _100_tbd=tt.Asset.Tbd(100))
def test_transfer_to_savings_matched(prepared_wallet, _100_tests, _100_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer_to_savings('initminer', 'alice', _100_tests, 'memo')
    prepared_wallet.api.transfer_to_savings('initminer', 'alice', _100_tbd, 'memo')


@test_asset_serialization(_100_tests=Mismatched(tt.Asset.Test(100)), _100_tbd=Mismatched(tt.Asset.Tbd(100)))
def test_transfer_to_savings_mixed(prepared_wallet, _100_tests, _100_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.transfer_to_savings('initminer', 'alice', _100_tests, 'memo')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.transfer_to_savings('initminer', 'alice', _100_tbd, 'memo')


@test_asset_serialization(_1_tests=tt.Asset.Test(1), _1_tbd=tt.Asset.Tbd(1), _10_tests=tt.Asset.Test(10),
                          _10_tbd=tt.Asset.Tbd(10))
def test_transfer_from_savings_matched(prepared_wallet, _1_tests, _1_tbd, _10_tests, _10_tbd):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _10_tests)

    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer_to_savings('initminer', 'alice', _10_tests, 'memo')
        prepared_wallet.api.transfer_to_savings('initminer', 'alice', _10_tbd, 'memo')

    prepared_wallet.api.transfer_from_savings('alice', 1000, 'bob', _1_tests, 'memo')
    prepared_wallet.api.transfer_from_savings('alice', 1001, 'bob', _1_tbd, 'memo')


@test_asset_serialization(_1_tests=Mismatched(tt.Asset.Test(1)), _1_tbd=Mismatched(tt.Asset.Tbd(1)),
                          _10_tests=tt.Asset.Test(10), _10_tbd=tt.Asset.Tbd(10))
def test_transfer_from_savings_mixed(prepared_wallet, _1_tests, _1_tbd, _10_tests, _10_tbd):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _10_tests)

    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer_to_savings('initminer', 'alice', _10_tests, 'memo')
        prepared_wallet.api.transfer_to_savings('initminer', 'alice', _10_tbd, 'memo')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.transfer_from_savings('alice', 1000, 'bob', _1_tests, 'memo')
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.transfer_from_savings('alice', 1001, 'bob', _1_tbd, 'memo')


@test_asset_serialization(_100_tests=tt.Asset.Test(100), _10_vest=tt.Asset.Vest(10))
def test_withdraw_vesting_matched(prepared_wallet, _100_tests, _10_vest):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _100_tests)
    prepared_wallet.api.withdraw_vesting('alice', _10_vest)


@test_asset_serialization(_100_tests=tt.Asset.Test(100), _10_vest=Mismatched(tt.Asset.Vest(10)))
def test_withdraw_vesting_mixed(prepared_wallet, _100_tests, _10_vest):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer_to_vesting_nonblocking('initminer', 'alice', _100_tests)
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.withdraw_vesting('alice', _10_vest)


# convert_hbd
# convert_hive_with_collateral
# estimate_hive_collateral

@test_asset_serialization(_100_tests=tt.Asset.Test(100))
def test_convert_hive_with_collateral_matched(prepared_wallet, _100_tests):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer('initminer', 'alice', _100_tests, 'memo')
    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _100_tests)
    prepared_wallet.api.convert_hive_with_collateral('alice', _100_tests)


@test_asset_serialization(_100_tests=tt.Asset.Test(100), _10_tbd=Mismatched(tt.Asset.Tbd(10)))
def test_convert_hive_with_collateral_mixed(prepared_wallet, _100_tests, _10_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer('initminer', 'alice', _100_tests, 'memo')
    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _100_tests)
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.convert_hive_with_collateral('alice', _10_tbd)


@test_asset_serialization(_100_tests=tt.Asset.Test(100), _10_tbd=tt.Asset.Tbd(10))
def test_convert_hbd_matched(prepared_wallet, _100_tests, _10_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer('initminer', 'alice', _100_tests, 'memo')
    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _100_tests)
    prepared_wallet.api.convert_hive_with_collateral('alice', _100_tests)
    prepared_wallet.api.convert_hbd('alice', _10_tbd)


@test_asset_serialization(_100_tests=tt.Asset.Test(100), _10_tbd=Mismatched(tt.Asset.Tbd(10)))
def test_convert_hbd_mixed(prepared_wallet, _100_tests, _10_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer('initminer', 'alice', _100_tests, 'memo')
    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _100_tests)
    prepared_wallet.api.convert_hive_with_collateral('alice', _100_tests)
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.convert_hbd('alice', _10_tbd)


@test_asset_serialization(_100_tests=tt.Asset.Test(100))
def test_estimate_hive_collateral_matched(prepared_wallet, _100_tests):
    prepared_wallet.api.estimate_hive_collateral(_100_tests)


@test_asset_serialization(_100_tests=Mismatched(tt.Asset.Test(100)))
def test_estimate_hive_collateral_mixed(prepared_wallet, _100_tests):
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.estimate_hive_collateral(_100_tests)


@test_asset_serialization(_100_tests=tt.Asset.Test(100), _100_tbd=tt.Asset.Tbd(100), _100_vest=tt.Asset.Vest(100))
def test_estimate_hive_collateral_matched(prepared_wallet, _100_tests, _100_tbd, _100_vest):

    # Workaround, ignoring message is necessary, because run this method correctly in testnet easy way is impossible.
    with pytest.raises(tt.exceptions.CommunicationError) as exception:
        prepared_wallet.api.claim_reward_balance('initminer', _100_tests, _100_tbd, _100_vest)

    exception_message = exception.value.response['error']['message']
    assert 'Cannot claim that much VESTS' not in exception_message


@test_asset_serialization(_100_tests=Mismatched(tt.Asset.Test(100)), _100_tbd=Mismatched(tt.Asset.Tbd(100)), _100_vest=Mismatched(tt.Asset.Vest(100)))
def test_estimate_hive_collateral_mixed(prepared_wallet, _100_tests, _100_tbd, _100_vest):
    # Workaround, ignoring message is necessary, because run this method correctly in testnet easy way is impossible.
    with pytest.raises(tt.exceptions.CommunicationError) as exception:
        prepared_wallet.api.claim_reward_balance('initminer', _100_tests, _100_tbd, _100_vest)

    exception_message = exception.value.response['error']['message']
    assert 'Invalid cast from object_type to string' in exception_message or 'Asset has to be treated as object' in exception_message


@test_asset_serialization(_100_tests=tt.Asset.Test(100), _100_tbd=tt.Asset.Tbd(100))
def test_create_order_matched(prepared_wallet, _100_tests, _100_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer('initminer', 'alice', _100_tests, 'memo')
    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _100_tests)
    prepared_wallet.api.create_order('alice', 1000, _100_tests, _100_tbd, False, 1000)


@test_asset_serialization(_10_tests=Mismatched(tt.Asset.Test(10)), _100_tbd=Mismatched(tt.Asset.Tbd(100)),
                          _100_tests=tt.Asset.Test(100))
def test_create_order_mixed(prepared_wallet, _10_tests, _100_tbd, _100_tests):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    prepared_wallet.api.transfer('initminer', 'alice', _100_tests, 'memo')
    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _100_tests)
    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.create_order('alice', 1000, _10_tests, _100_tbd, False, 1000)


@test_asset_serialization(_1000000_tests=tt.Asset.Test(1000000), _1000000_tbd=tt.Asset.Tbd(1000000))
def test_create_proposal_matched(prepared_wallet, _1000000_tests, _1000000_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer('initminer', 'alice', _1000000_tbd, 'memo')
        prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _1000000_tests)

    prepared_wallet.api.post_comment('alice', 'permlink', '', 'parent-permlink', 'title', 'body', '{}')

    prepared_wallet.api.create_proposal('alice', 'alice', '2031-01-01T00:00:00', '2031-06-01T00:00:00', _1000000_tbd,
                                        'subject-1', 'permlink')


@test_asset_serialization(_1000000_tests=tt.Asset.Test(1000000), _1000000_tbd=tt.Asset.Tbd(1000000),
                          _10_tbd=Mismatched(tt.Asset.Tbd(10)))
def test_create_proposal_mixed(prepared_wallet, _1000000_tests, _1000000_tbd, _10_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer('initminer', 'alice', _1000000_tbd, 'memo')
        prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _1000000_tests)

    prepared_wallet.api.post_comment('alice', 'permlink', '', 'parent-permlink', 'title', 'body', '{}')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.create_proposal('alice', 'alice', '2031-01-01T00:00:00', '2031-06-01T00:00:00', _10_tbd,
                                            'subject-1', 'permlink')


@test_asset_serialization(_1000000_tests=tt.Asset.Test(1000000), _1000000_tbd=tt.Asset.Tbd(1000000),
                          _10_tbd=tt.Asset.Tbd(10))
def test_update_proposal_matched(prepared_wallet, _1000000_tests, _1000000_tbd, _10_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer('initminer', 'alice', _1000000_tbd, 'memo')
        prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _1000000_tests)

    prepared_wallet.api.post_comment('alice', 'permlink', '', 'parent-permlink', 'title', 'body', '{}')

    prepared_wallet.api.create_proposal('alice', 'alice', '2031-01-01T00:00:00', '2031-06-01T00:00:00', _1000000_tbd,
                                        'subject-1', 'permlink')

    prepared_wallet.api.update_proposal(0, 'alice', _10_tbd, 'subject-1', 'permlink', '2031-06-01T00:00:00')


@test_asset_serialization(_1000000_tests=tt.Asset.Test(1000000), _1000000_tbd=tt.Asset.Tbd(1000000),
                          _10_tbd=Mismatched(tt.Asset.Tbd(10)))
def test_update_proposal_mixed(prepared_wallet, _1000000_tests, _1000000_tbd, _10_tbd):
    prepared_wallet.api.create_account('initminer', 'alice', '{}')
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.transfer('initminer', 'alice', _1000000_tbd, 'memo')
        prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _1000000_tests)

    prepared_wallet.api.post_comment('alice', 'permlink', '', 'parent-permlink', 'title', 'body', '{}')

    prepared_wallet.api.create_proposal('alice', 'alice', '2031-01-01T00:00:00', '2031-06-01T00:00:00', _1000000_tbd,
                                        'subject-1', 'permlink')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.update_proposal(0, 'alice', _10_tbd, 'subject-1', 'permlink', '2031-06-01T00:00:00')


@test_asset_serialization(_1000000_tests=tt.Asset.Test(1000000))
def test_recurrent_transfer_matched(prepared_wallet, _1000000_tests):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _1000000_tests)
    prepared_wallet.api.transfer('initminer', 'alice', _1000000_tests, 'memo')
    prepared_wallet.api.recurrent_transfer('alice', 'bob', _1000000_tests, 'memo', 100, 10)


@test_asset_serialization(_10_tests=Mismatched(tt.Asset.Test(10)), _100_tests=tt.Asset.Test(100))
def test_recurrent_transfer_mixed(prepared_wallet, _10_tests, _100_tests):
    with prepared_wallet.in_single_transaction():
        prepared_wallet.api.create_account('initminer', 'alice', '{}')
        prepared_wallet.api.create_account('initminer', 'bob', '{}')

    prepared_wallet.api.transfer_to_vesting('initminer', 'alice', _100_tests)
    prepared_wallet.api.transfer('initminer', 'alice', _100_tests, 'memo')

    with pytest.raises(tt.exceptions.CommunicationError):
        prepared_wallet.api.recurrent_transfer('alice', 'bob', _10_tests, 'memo', 100, 10)

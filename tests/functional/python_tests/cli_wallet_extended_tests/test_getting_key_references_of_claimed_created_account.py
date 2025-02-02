# This is a regression test for problem described in following issue:
# https://gitlab.syncad.com/hive/hive/-/issues/113

from test_tools import Account, logger, Asset


def test_getting_key_references_of_claimed_created_account(node, wallet):
    logger.info('Waiting until initminer will be able to create account...')
    node.wait_number_of_blocks(30)

    account = Account('alice')
    key = account.public_key
    wallet.api.claim_account_creation('initminer', Asset.Test(0))
    wallet.api.create_funded_account_with_keys(
        'initminer', account.name, Asset.Test(0), 'memo', '{}', key, key, key, key
    )

    assert node.api.condenser.get_key_references([account.public_key]) == [[account.name]]

from test_tools import Account, logger, Wallet
from test_tools.exceptions import CommunicationError
import json

def test_signing_with_authority(node):
        wallet = Wallet(attach_to=node)
        wallet1 = Wallet(attach_to=node)
        wallet2 = Wallet(attach_to=node)
        wallet3 = Wallet(attach_to=node)

        Alice = Account('tst-alice')
        Auth1 = Account('tst-auth1')
        Auth2 = Account('tst-auth2')
        Auth3 = Account('tst-auth3')

        for account in [Alice, Auth1, Auth2, Auth3]:
            wallet.api.create_account_with_keys('initminer', account.name, "", account.public_key, account.public_key, account.public_key, account.public_key )
            wallet.api.transfer('initminer', account.name, "1.000 TESTS", "test transfer")
            wallet.api.transfer_to_vesting('initminer', account.name, "1.000 TESTS")

        wallet.api.import_key(Alice.private_key)
        wallet1.api.import_key(Auth1.private_key)
        wallet2.api.import_key(Auth2.private_key)
        wallet3.api.import_key(Auth3.private_key)

        # TRIGGER and VERIFY
        wallet.api.transfer(Alice.name, 'initminer', "0.001 TESTS", "this will work")

        wallet.api.update_account_auth_account(Alice.name, 'active', Auth1.name, 1)
        # create circular authority dependency and test wallet behaves correctly, i.e. no duplicate signatures
        wallet1.api.update_account_auth_account(Auth1.name, 'active', Alice.name, 1)
        wallet1.api.update_account_auth_account(Auth1.name, 'active', Auth2.name, 1)
        wallet2.api.update_account_auth_account(Auth2.name, 'active', Auth3.name, 1)

        logger.info("sign with own account keys")
        wallet.api.transfer(Alice.name, 'initminer', "0.001 TESTS", "this will work and does not print warnings")

        # wallet1 and wallet2 can sign only with account authority
        logger.info("sign with account authority")
        wallet1.api.transfer(Alice.name, 'initminer', "0.001 TESTS", "this will work after enhancement")
        logger.info("sign with authority of account authority")

        wallet2.api.transfer(Alice.name, 'initminer', "0.001 TESTS", "this will also work after enhancement")
        logger.info("successfully signed and broadcasted transactions with account authority")

        # assert siging with authority does not work when dependency is to deep
        try:
            logger.info("try signing with authority to deep in dependency tree")
            wallet3.api.transfer(Alice.name, 'initminer', "0.001 TESTS", "this will NOT work")
            assert False
        except CommunicationError as e:
            assert 'Missing Active Authority' in str(e)
            logger.info("couldn't sign transaction with invalid authority")

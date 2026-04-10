import pytest
import boa
from eth_account import Account
from script.deploy_vendor_engine import deploy_vendor
from moccasin.config import get_active_network
from eth_utils import to_wei

AMOUNT = to_wei(100, "ether")
BALANCE = to_wei(10, "ether")
# ------------------------------------------------------------------
#                         SESSION SCOPED
# ------------------------------------------------------------------
@pytest.fixture(scope="session")
def active_network():
    return get_active_network()


@pytest.fixture(scope="session")
def random_user():
    entropy = 13
    account = Account.create(entropy)
    boa.env.set_balance(account.address, BALANCE)
    return account.address



# ------------------------------------------------------------------
#                        FUNCTION SCOPED
# ------------------------------------------------------------------
@pytest.fixture
def v_token(active_network):
    return active_network.manifest_named("token")

@pytest.fixture
def vendor_engine(v_token):
    return deploy_vendor(v_token)

@pytest.fixture
def funded_vendor(vendor_engine, v_token):
    tokens_for_vendor = to_wei(1000, "ether")
    v_token.transfer(vendor_engine.address, tokens_for_vendor)
    return vendor_engine

@pytest.fixture
def vendor_with_funds(funded_vendor, random_user):
    eth_amount = to_wei(2, "ether")
    funded_vendor.buyTokens(value=eth_amount, sender=random_user)
    return funded_vendor

@pytest.fixture
def random_user_with_tokens(random_user, v_token):
    tokens_for_user = to_wei(3, "ether")
    v_token.transfer(random_user, tokens_for_user)
    return random_user   
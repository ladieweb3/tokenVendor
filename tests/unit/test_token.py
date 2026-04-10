from script.deploy_token import INITIAL_SUPPLY
import boa

RANDOM = boa.env.generate_address("non-owner")


def test_token_supply(v_token):
    assert v_token.totalSupply() == INITIAL_SUPPLY
from eth_utils import to_wei
from moccasin.boa_tools import VyperContract

from src import token

INITIAL_SUPPLY = to_wei(1000, "ether")  

def deploy_v_token()-> VyperContract:
    """
    Deploys a simple ERC20 token contract using Vyper.

    Returns:
        VyperContract: The deployed ERC20 token contract instance.
    """
    token_contract = token.deploy(INITIAL_SUPPLY)
    print(f"Token deployed at: {token_contract.address}")
    return token_contract



def moccasin_main():
    """
    Main deployment function for Moccasin framework.

    Returns:
        VyperContract: The deployed ERC20 token contract instance.
    """
    return deploy_v_token()
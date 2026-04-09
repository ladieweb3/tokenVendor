from moccasin.boa_tools import VyperContract
from src import vendor
from moccasin.config import get_active_network

def deploy_vendor(token_contract: VyperContract):
    """Deploys the Vendor contract using the provided token contract."""
    active_network = get_active_network()
    vendor_contract = vendor.deploy(token_contract)

    #verify contract on explorer
    if active_network.has_explorer():
        print("Verifying contract on explorer...")
        result = active_network.moccasin_verify(vendor_contract)
        result.wait_for_verification()
    print(f"Deployed Vendor contract at {vendor_contract.address}")
    return vendor_contract

def moccasin_main():
    """Main deployment function for Moccasin framework."""
    active_network = get_active_network()
    token = active_network.manifest_named("token")
    return deploy_vendor(token)
import boa
from boa.util.abi import Address
from boa import BoaError
from eth_utils import to_wei
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule
from boa.test.strategies import strategy

from script.deploy_vendor_engine import deploy_vendor
from script.deploy_token import deploy_v_token

USERS_SIZE    = 10
MAX_ETH       = to_wei(100, "ether")
INITIAL_BAL   = to_wei(1000, "ether")  # ← balance initiale pour chaque user

class TokenVendorFuzzer(RuleBasedStateMachine):

    @initialize()
    def setup(self):
        self.token  = deploy_v_token()
        self.vendor = deploy_vendor(self.token)

        # Générer les users et leur donner une balance ETH ✅
        self.users = [boa.env.generate_address() for _ in range(USERS_SIZE)]
        for user in self.users:
            boa.env.set_balance(user, INITIAL_BAL)

        # Approvisionner le vendor en tokens ✅
        owner_balance = self.token.balanceOf(boa.env.eoa)
        self.token.transfer(self.vendor.address, owner_balance)

    @rule(
        user_seed=st.integers(min_value=0, max_value=USERS_SIZE - 1),
        amount=strategy("uint256", min_value=1, max_value=MAX_ETH),
    )
    def buy_tokens(self, user_seed, amount):
        user = self.users[user_seed]
        assume_eth  = boa.env.get_balance(user) >= amount
        assume_tokens = self.token.balanceOf(self.vendor.address) >= amount * 100
        if not assume_eth or not assume_tokens:
            return  # ← return au lieu de assume() ✅
        self.vendor.buyTokens(value=amount, sender=user)

    @rule(
        user_seed=st.integers(min_value=0, max_value=USERS_SIZE - 1),
        amount=strategy("uint256", min_value=1, max_value=MAX_ETH),
    )
    def sell_tokens(self, user_seed, amount):
        user = self.users[user_seed]

        eth_to_return = amount // self.vendor.TOKENS_PER_ETH()

        # Guards — préconditions du contrat
        if self.token.balanceOf(user) < amount:                      return
        if boa.env.get_balance(self.vendor.address) < eth_to_return: return

        # ✅ On n'arrive ici que si toutes les conditions sont remplies
        self.token.approve(self.vendor.address, amount, sender=user)
        self.vendor.sellTokens(amount, sender=user)
                
        

    @rule()
    def withdraw(self):
        owner = self.vendor.OWNER()
        if boa.env.get_balance(self.vendor.address) == 0:
            return 
        self.vendor.withdraw(sender=owner)

    @invariant()
    def vendor_eth_balance_is_non_negative(self):
        assert boa.env.get_balance(self.vendor.address) >= 0



token_vendor_fuzzer = TokenVendorFuzzer.TestCase
token_vendor_fuzzer.settings = settings(max_examples=64, stateful_step_count=64)
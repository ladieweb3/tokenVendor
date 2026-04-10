import boa
from eth_utils import to_wei


# ------------------------------------------------------------------
#                   VENDOR CONTRACT
# ------------------------------------------------------------------

def test_vendor_is_initialized_with_correct_token(vendor_engine, v_token):
    """Test that the Vendor contract is initialized with the correct token address.
    
    Args:
        vendor_engine (VyperContract): The deployed Vendor contract instance.
        v_token (VyperContract): The deployed token contract instance.
    """
    # --- ARRANGE ---
    expected_token = v_token.address

    # --- ACT ---
    actual_token = vendor_engine.TOKEN()

    # --- ASSERT ---
    assert actual_token == expected_token


# ------------------------------------------------------------------
#                       BUY TOKENS
# ------------------------------------------------------------------

def test_buy_tokens_reverts_when_zero_eth_sent(vendor_engine):
    """Test that buying tokens reverts when zero ETH is sent.

    Args:
        vendor_engine (VyperContract): The deployed Vendor contract instance.
    """
    # --- ARRANGE ---
    invalid_amount = 0

    # --- ACT & ASSERT ---
    with boa.reverts("Vendor: Invalid amount of ETH sent"):
        vendor_engine.buyTokens(value=invalid_amount)

def test_buy_tokens_reverts_when_vendor_has_no_tokens(vendor_engine, v_token, random_user):
    """Test that buying tokens reverts when the vendor has no tokens.

    Args:
        vendor_engine (VyperContract): The deployed Vendor contract instance.
        v_token (VyperContract): The deployed token contract instance.
        random_user (address): A random user address.
    """
    # --- ARRANGE ---
    vendor_balance = v_token.balanceOf(vendor_engine.address)
    assert vendor_balance == 0, "Vendor should have no tokens"
    eth_amount = to_wei(1, "ether")

    # --- ACT & ASSERT ---
    with boa.reverts("Vendor: Not enough tokens in the reserve"):
        vendor_engine.buyTokens(value=eth_amount, sender=random_user)

def test_buy_tokens_transfers_tokens_to_buyer(vendor_engine, v_token, random_user):
    """Test that buying tokens transfers the correct amount of tokens to the buyer. 
    Args:
        vendor_engine (VyperContract): The deployed Vendor contract instance.
        v_token (VyperContract): The deployed token contract instance.
        random_user (address): A random user address.
    """
    # --- ARRANGE ---
    TOKENS_PER_ETH = 100
    eth_amount = to_wei(1, "ether")
    tokens_bought = eth_amount * TOKENS_PER_ETH
    v_token.transfer(vendor_engine.address, to_wei(1000, "ether"))

    user_eth_before    = boa.env.get_balance(random_user)
    user_tokens_before = v_token.balanceOf(random_user)
    vendor_eth_before  = boa.env.get_balance(vendor_engine.address)

    # --- ACT ---
    vendor_engine.buyTokens(value=eth_amount, sender=random_user)

    # --- ASSERT ---
    assert v_token.balanceOf(random_user) == user_tokens_before + tokens_bought
    assert boa.env.get_balance(random_user) == user_eth_before - eth_amount
    assert boa.env.get_balance(vendor_engine.address) == vendor_eth_before + eth_amount

def test_buy_tokens_emits_buy_tokens_event(funded_vendor, random_user):
    """Test that buying tokens emits the BuyTokens event.

    Args:
        funded_vendor (VyperContract): The deployed Vendor contract instance with funds.
        random_user (address): A random user address.
    """
    # --- ARRANGE ---
    TOKENS_PER_ETH = 100
    eth_amount = to_wei(1, "ether")
    tokens_bought = eth_amount * TOKENS_PER_ETH

    # --- ACT ---
    funded_vendor.buyTokens(value=eth_amount, sender=random_user)

    # --- ASSERT ---
    logs   = funded_vendor.get_logs()
    events = [log for log in logs if type(log).__name__ == "BuyTokens"]

    assert len(events) == 1
    event = events[0]
    assert event.buyer         == random_user
    assert event.amountOfETH   == eth_amount
    assert event.amountOfTokens == tokens_bought


# ------------------------------------------------------------------
#                       WITHDRAW FUNDS
# ------------------------------------------------------------------

def test_withdraw_reverts_when_caller_is_not_owner(vendor_engine, random_user):
    """Test that withdrawing funds reverts when the caller is not the owner.
    Args:
        vendor_engine (VyperContract): The deployed Vendor contract instance.
        random_user (address): A random user address.
    """
    # --- ARRANGE ---
    no_owner = random_user

    # --- ACT & ASSERT ---
    with boa.reverts("Vendor: Only the owner can withdraw"):
        vendor_engine.withdraw(sender=no_owner)

def test_withdraw_sends_eth_to_owner(vendor_with_funds):
    """Test that withdrawing funds sends ETH to the owner.
    Args:
        vendor_with_funds (VyperContract): The deployed Vendor contract instance with funds.
    """
    # --- ARRANGE ---
    owner = vendor_with_funds.OWNER()
    owner_eth_before  = boa.env.get_balance(owner)
    vendor_eth_before = boa.env.get_balance(vendor_with_funds.address)

    assert vendor_eth_before > 0, "Vendor: No ETH to withdraw"

    # --- ACT ---
    vendor_with_funds.withdraw(sender=owner)

    # --- ASSERT ---
    assert boa.env.get_balance(owner) == owner_eth_before + vendor_eth_before
    assert boa.env.get_balance(vendor_with_funds.address) == 0

def test_withdraw_emits_withdraw_event(vendor_with_funds):
    """Test that withdrawing funds emits the Withdraw event.

    Args:
        vendor_with_funds (VyperContract): The deployed Vendor contract instance with funds.
    """
    # --- ARRANGE ---
    owner = vendor_with_funds.OWNER()
    vendor_eth_before = boa.env.get_balance(vendor_with_funds.address)

    # --- ACT ---
    vendor_with_funds.withdraw(sender=owner)

    # --- ASSERT ---
    logs   = vendor_with_funds.get_logs()
    events = [log for log in logs if type(log).__name__ == "Withdraw"]

    assert len(events) == 1
    event = events[0]
    assert event.owner       == owner
    assert event.amountOfETH == vendor_eth_before


# ------------------------------------------------------------------
#                       SELL TOKENS
# ------------------------------------------------------------------

def test_sell_tokens_reverts_when_amount_is_zero(vendor_engine, random_user):
    """Test that selling tokens reverts when the amount is zero.
    Args:
        vendor_engine (VyperContract): The deployed Vendor contract instance.
        random_user (address): A random user address.
    """
    # --- ARRANGE ---
    invalid_amount = 0

    # --- ACT & ASSERT ---
    with boa.reverts("Vendor: Invalid amount of tokens"):
        vendor_engine.sellTokens(invalid_amount, sender=random_user)

def test_sell_tokens_reverts_when_user_has_insufficient_balance(vendor_engine, random_user):
    """Test that selling tokens reverts when the user has insufficient balance.
    Args:
        vendor_engine (VyperContract): The deployed Vendor contract instance.
        random_user (address): A random user address.
    """
    # --- ARRANGE ---
    amount_exceeding_balance = 100

    # --- ACT & ASSERT ---
    with boa.reverts("Vendor: Not enough tokens to sell"):
        vendor_engine.sellTokens(amount_exceeding_balance, sender=random_user)

def test_sell_tokens_reverts_when_vendor_has_no_eth(vendor_engine, v_token, random_user):
    """Test that selling tokens reverts when the vendor has no ETH.
    Args:
        vendor_engine (VyperContract): The deployed Vendor contract instance.
        v_token (VyperContract): The deployed token contract instance.
        random_user (address): A random user address.
    """
    # --- ARRANGE ---
    tokens_to_sell = 100
    v_token.transfer(random_user, tokens_to_sell)

    # --- ACT & ASSERT ---
    with boa.reverts("Vendor: Not enough ETH in the reserve"):
        vendor_engine.sellTokens(tokens_to_sell, sender=random_user)

def test_sell_tokens_transfers_eth_to_seller(vendor_engine, v_token, random_user_with_tokens):
    """Test that selling tokens transfers ETH to the seller.
    Args:
        vendor_engine (VyperContract): The deployed Vendor contract instance.
        v_token (VyperContract): The deployed token contract instance.
        random_user_with_tokens (address): A random user address with tokens.
    """
    # --- ARRANGE ---
    tokens_to_sell = to_wei(2, "ether")
    eth_to_receive = tokens_to_sell // vendor_engine.TOKENS_PER_ETH()

    boa.env.set_balance(vendor_engine.address, to_wei(100, "ether"))
    v_token.approve(vendor_engine.address, tokens_to_sell, sender=random_user_with_tokens)

    user_eth_before    = boa.env.get_balance(random_user_with_tokens)
    user_tokens_before = v_token.balanceOf(random_user_with_tokens)
    vendor_eth_before  = boa.env.get_balance(vendor_engine.address)
    
    # --- ACT ---
    vendor_engine.sellTokens(tokens_to_sell, sender=random_user_with_tokens)

    # --- ASSERT ---
    assert v_token.balanceOf(random_user_with_tokens) == user_tokens_before - tokens_to_sell
    assert boa.env.get_balance(vendor_engine.address) == vendor_eth_before - eth_to_receive
    assert boa.env.get_balance(random_user_with_tokens) == user_eth_before + eth_to_receive
    assert v_token.balanceOf(vendor_engine.address) == tokens_to_sell

def test_sell_tokens_emits_sell_tokens_event(vendor_engine, v_token, random_user_with_tokens):
    """Test that selling tokens emits the SellTokens event.
    Args:
        vendor_engine (VyperContract): The deployed Vendor contract instance.
        v_token (VyperContract): The deployed token contract instance.
        random_user_with_tokens (address): A random user address with tokens.
    """
    # --- ARRANGE ---
    tokens_to_sell = to_wei(2, "ether")
    eth_to_receive = tokens_to_sell // vendor_engine.TOKENS_PER_ETH()

    boa.env.set_balance(vendor_engine.address, to_wei(100, "ether"))
    v_token.approve(vendor_engine.address, tokens_to_sell, sender=random_user_with_tokens)

    # --- ACT ---
    vendor_engine.sellTokens(tokens_to_sell, sender=random_user_with_tokens)

    # --- ASSERT ---
    logs   = vendor_engine.get_logs()
    events = [log for log in logs if type(log).__name__ == "SellTokens"]

    assert len(events) == 1
    event = events[0]
    assert event.seller         == random_user_with_tokens
    assert event.amountOfTokens == tokens_to_sell
    assert event.amountOfETH    == eth_to_receive
# pragma version ^0.4.1
"""
@license MIT
@title V_token
@author You!
@notice This is my ERC20 token!
"""
from src.interfaces import i_token
from ethereum.ercs import IERC20

#CEI
# Checks : assert statements to validate inputs and conditions
# Effects : update the state variables
# Interactions : external calls to other contracts

# ------------------------------------------------------------------
#                        STATE VARIABLES
# ------------------------------------------------------------------

TOKENS_PER_ETH: public(constant(uint256)) = 100 
TOKEN: public(immutable(i_token))
OWNER: public(immutable(address))

# ------------------------------------------------------------------
#                             EVENTS
# ------------------------------------------------------------------

event BuyTokens:
    buyer: indexed(address)
    amountOfETH: uint256
    amountOfTokens: uint256

event SellTokens:
    seller: indexed(address)
    amountOfETH: uint256
    amountOfTokens: uint256

event Withdraw:
    owner: indexed(address)
    amountOfETH: uint256


@deploy
def __init__(token_address: address): 
    TOKEN = i_token(token_address)
    OWNER = msg.sender


@external
@payable
def buyTokens():
    """@notice Allows users to buy tokens from the vendor by sending ETH
    """
    #Checks
    assert msg.value > 0, "Vendor: Invalid amount of ETH sent"
    tokensToBuy: uint256 = msg.value * TOKENS_PER_ETH
    vendorBalance: uint256 = staticcall TOKEN.balanceOf(self)
    assert vendorBalance >= tokensToBuy, "Vendor: Not enough tokens in the reserve"

    #Effects
    log BuyTokens(buyer=msg.sender, amountOfETH=msg.value, amountOfTokens=tokensToBuy)

    #Interactions
    success: bool = extcall TOKEN.transfer(msg.sender, tokensToBuy)
    assert success, "Vendor: Failed to transfer tokens"


@external
def sellTokens(amount: uint256):
    """
    @notice Allows users to sell their tokens back to the vendor in exchange for ETH
    @param amount The amount of tokens the user wants to sell
    """
    #Checks
    assert amount > 0, "Vendor: Invalid amount of tokens"
    userBalance: uint256 = staticcall TOKEN.balanceOf(msg.sender)
    assert userBalance >= amount, "Vendor: Not enough tokens to sell"
    ethToReturn: uint256 = amount // TOKENS_PER_ETH 
    assert self.balance >= ethToReturn, "Vendor: Not enough ETH in the reserve"

    #Effects
    log SellTokens(seller=msg.sender, amountOfETH=ethToReturn, amountOfTokens=amount)

    #Interactions
    success: bool = extcall TOKEN.transferFrom(msg.sender, self, amount)
    assert success, "Vendor: Failed to transfer tokens from user"
    send(msg.sender, ethToReturn)


@external
@nonreentrant
def withdraw():
    """@notice Allows the owner to withdraw all the ETH from the vendor contract
    """
    #Checks
    assert msg.sender == OWNER, "Vendor: Only the owner can withdraw"
    amount: uint256 = self.balance
    assert amount > 0, "Vendor: No ETH to withdraw"

    #Effects
    log Withdraw(owner=msg.sender, amountOfETH=amount)
    
    #Interactions
    send(msg.sender, amount)
    assert self.balance == 0, "Vendor: Withdrawal failed"



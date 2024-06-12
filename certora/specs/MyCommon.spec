// filter methods from abstractBaseHarness.sol
function filterABH(method f) returns bool {
  return f.selector == sig:isOperationDisabledExt(uint32).selector
    || f.selector == sig:isDepositDisabled().selector
    || f.selector == sig:isMintDisabled().selector
    || f.selector == sig:isWithdrawDisabled().selector
    || f.selector == sig:isRedeemDisabled().selector
    || f.selector == sig:isSkimDisabled().selector
    || f.selector == sig:getBalanceAndForwarderExt(address).selector
    || f.selector == sig:vaultCacheOracleConfigured().selector ;
}

// filter borrowharness view like return functions
function filterBorrowHarness(method f) returns bool {
  return f.selector == sig:getVaultInterestAccExt().selector ||
  f.selector == sig:getUnderlyingAssetExt().selector ||
  f.selector == sig:initOperationExternal(uint32,address).selector ;
}

// get the function selector for the main borrow state changing methods only
function borrowNonViews(method f) returns bool {
    return f.selector == sig:borrow(uint256,address).selector ||
    f.selector == sig:repay(uint256,address).selector ||
    f.selector == sig:repayWithShares(uint256,address).selector ||
    f.selector == sig:pullDebt(uint256,address).selector ||
    f.selector == sig:flashLoan(uint256,bytes).selector ||
    f.selector == sig:touch().selector ;
}


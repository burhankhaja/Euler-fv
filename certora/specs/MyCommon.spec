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

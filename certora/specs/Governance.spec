import "./Base.spec";
import "./MyCommon.spec";

methods {
    function _.isHookTarget() external => NONDET;

    function Base.initOperation(uint32 operation, address accountToCheck) internal returns (GovernanceHarness.VaultCache memory, address) with(env e) => CVLInitOperation(e, operation, accountToCheck);
}

function CVLInitOperation(env e, uint32 operation, address accountToCheck) returns (GovernanceHarness.VaultCache, address) {
    GovernanceHarness.VaultCache cache;
    address out;

    return (cache, out);
}

// used to test running time
use builtin rule sanity;

rule onlyGovernorCallsSpecialMethods(method f) filtered {
    f -> (f.selector == sig:setGovernorAdmin(address ).selector ||
        f.selector == sig:setFeeReceiver(address ).selector ||
        f.selector == sig:setLTV(address , uint16 , uint16 , uint32 ).selector ||
        f.selector == sig:clearLTV(address ).selector ||
        f.selector == sig:setMaxLiquidationDiscount(uint16 ).selector ||
        f.selector == sig:setLiquidationCoolOffTime(uint16 ).selector ||
        f.selector == sig:setInterestRateModel(address ).selector ||
        f.selector == sig:setHookConfig(address , uint32 ).selector ||
        f.selector == sig:setConfigFlags(uint32 ).selector ||
        f.selector == sig:setCaps(uint16 , uint16 ).selector ||
        f.selector == sig:setInterestFee(uint16 ).selector)
}{
    env e;
    calldataarg args;
    require !isGovernor(e);

    f@withrevert(e,args);

    assert lastReverted, "special methods are only available to governor";
}

rule NoMalicious_methods(method f) filtered {
    f -> !f.isView
} {
    env e;
    calldataarg args;
    
    f(e,args);

    assert true => (filterABH(f) || f.selector == sig:convertFees().selector || f.selector == sig:setGovernorAdmin(address ).selector ||
        f.selector == sig:setFeeReceiver(address ).selector ||
        f.selector == sig:setLTV(address , uint16 , uint16 , uint32 ).selector ||
        f.selector == sig:clearLTV(address ).selector ||
        f.selector == sig:setMaxLiquidationDiscount(uint16 ).selector ||
        f.selector == sig:setLiquidationCoolOffTime(uint16 ).selector ||
        f.selector == sig:setInterestRateModel(address ).selector ||
        f.selector == sig:setHookConfig(address , uint32 ).selector ||
        f.selector == sig:setConfigFlags(uint32 ).selector ||
        f.selector == sig:setCaps(uint16 , uint16 ).selector ||
        f.selector == sig:setInterestFee(uint16 ).selector) ,"malicous state chaning method detected";
}
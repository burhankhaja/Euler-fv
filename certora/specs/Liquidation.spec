import "./Base.spec";
import "./MyCommon.spec";

using LiquidationHarness as l_harness;
methods {
    function isRecognizedCollateralExt(address collateral) external returns (bool) envfree;
}

// // passing //timing out rule
// rule checkLiquidation_healthy() {
//     env e;
//     address liquidator;
//     address violator; 
//     address collateral;
//     uint256 maxRepay;
//     uint256 maxYield;

//     require oracleAddress != 0;

//     uint256 liquidityCollateralValue;
//     uint256 liquidityLiabilityValue;
//     (liquidityCollateralValue, liquidityLiabilityValue) = 
//         calculateLiquidityExternal(e, violator);

//     require liquidityCollateralValue > liquidityLiabilityValue;

//     (maxRepay, maxYield) = checkLiquidation(e, liquidator, violator, collateral);

//     assert maxRepay == 0;
//     assert maxYield == 0;
// }

// used to test running time
use builtin rule sanity;

//====================================================================================
rule No_Unneccessaryliquidation {
    env e;
    require e.block.timestamp == 0;

    LiquidationHarness.VaultCache cache = getLoadVault(e);
    address liquidator = actualCaller(e);
    address violator;
    address collateral;
    uint256 repayAssets;
    uint256 minYieldBalance;

    // only possible states
    require interestAccumulatorCustom(e) == 1 && interestAccumulatorOfCustom(e, violator) == 1 && interestAccumulatorOfCustom(e,liquidator) == 1;

    uint previousBorrows;
    uint assumedTotalBorrows = AllFormallyPossibleTotalBorrowValues(e, previousBorrows);
   
    uint previousUserData_1;
    uint assumedUserData_1 = AllFormallyPossibleUserDataValues(e, previousUserData_1);

    uint previousUserData_2;
    uint assumedUserData_2 = AllFormallyPossibleUserDataValues(e, previousUserData_2);
   // // // // 


    require totalBorrowsCustom(e) == assumedTotalBorrows;
    require getUserDataCustom(e,liquidator) == assumedUserData_1;
    require getUserDataCustom(e,violator) == assumedUserData_2;

    //==================================================
    mathint liquidatorDebtBefore = debtUpOfCustom(e, liquidator);
    mathint violatorDebtBefore = debtUpOfCustom(e, violator);
    mathint totalBorrowsBefore = totalBorrowsUpCustom(e);
    
    LiquidationModule.LiquidationCache liqCache = calculateLiquidationExt(e,cache,liquidator, violator,collateral,repayAssets);

    require liqCache.yieldBalance == 0; // avoid enforceCollateralTransfer()

    //ACTION
    liquidate(e, violator, collateral, repayAssets, minYieldBalance);
    
    mathint liquidatorDebtAfter = debtUpOfCustom(e, liquidator);
    mathint violatorDebtAfter = debtUpOfCustom(e, violator);
    mathint totalBorrowsAfter = totalBorrowsUpCustom(e);

    assert liqCache.repay > 0 && !isLiquidationAllowedToDecrease(e, cache, liqCache) => liquidatorDebtAfter == liquidatorDebtBefore + liqCache.repay, "liquidators debt must debt amount";
    assert liqCache.repay > 0 && !isLiquidationAllowedToDecrease(e, cache, liqCache) => violatorDebtAfter == violatorDebtBefore - liqCache.repay, "voilaters debt must decrease by repay amount";
    assert liqCache.repay > 0 && !isLiquidationAllowedToDecrease(e, cache, liqCache) => totalBorrowsAfter == totalBorrowsBefore , "totalborrows must remain same";



}

rule NoLiquidation_WhenMinYeild_SurpassesBalance {
    env e;
    require e.block.timestamp == 0;

    LiquidationHarness.VaultCache cache = getLoadVault(e);
    address liquidator = actualCaller(e);
    address violator;
    address collateral;
    uint256 repayAssets;
    uint256 minYieldBalance;


    LiquidationModule.LiquidationCache liqCache = calculateLiquidationExt(e,cache,liquidator, violator,collateral,repayAssets);

    //ACTION
    liquidate@withrevert(e, violator, collateral, repayAssets, minYieldBalance);
    
    //         if (minYieldBalance > liqCache.yieldBalance) revert E_MinYield();
    assert minYieldBalance > liqCache.yieldBalance => lastReverted, "no liquidation should succeed when minimum yeild balance surpasses yieldBalance";

}




//====================================================================================
//====================================================================================
rule liquidatecallsAreOnlyAllowedViaEVC {
    env e;
    calldataarg args;
    require e.msg.sender != evcAddress(e);

    liquidate@withrevert(e,args);

    assert lastReverted , "calls must be only allowed via evc";

}

rule liquidateCantBeReentred {
    env e;
    require e.block.timestamp == 0; 
    calldataarg args;
    // LiquidationHarness.vaultStorage _storage;
    require l_harness.vaultStorage.reentrancyLocked;
    // require _storage.reentrancyLocked;

    liquidate@withrevert(e,args);

    assert lastReverted, "liquidate must have reentrancy protection";

}

rule NoUnexpectedStateChangingMethodsAvailable(method f) filtered {
    f -> !f.isView
}{
    env e;
    calldataarg args;

    f(e,args);

    assert true => filterABH(f) || f.selector == sig:liquidate(address,address,uint256,uint256).selector || f.selector == sig:getLiquidator().selector, "malicious methods detected";

}
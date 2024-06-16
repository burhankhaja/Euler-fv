import "./Base.spec";
import "MyCommon.spec";

using EthereumVaultConnector as _evc;
using RiskManagerHarness as r_harness;
//you can then access things like this    r_harness.vaultStorage.users[evcCaller].getOwed



// used to test running time
use builtin rule sanity;
// dos

methods {
    function evcAddress() external returns address envfree;
    function riskManagerAddress() external returns address envfree;
    function AccountStatusSelector() external returns bytes4 envfree;
    function VaultStatusSelector() external returns bytes4 envfree;
   //  function getOracleAddress() external returns address envfree;
    function getOwedOf(address account) external returns RiskManagerHarness.Owed envfree;
    //@audit maybe i need formal data and totalborrows as of calculations maybe checkout
}

invariant NoDosDueToReentrancy(env e) !r_harness.vaultStorage.reentrancyLocked;

//@audit
// write spec to deal with
// nonReentrant modifier
// unexpected method






//===============
// Disable controller
//===========


rule controllerIsDisabledCorrectly
 {
    env e;
   address controller;
   require controller == riskManagerAddress();

   require e.msg.sender != evcAddress();
   require getOwedOf(e, e.msg.sender) == 0;
   require _evc.isControllerEnabled(e, e.msg.sender, controller);

// example::: currentContract.myState[0].bar[addr][0] where myState is private array of mappings of address=uint
   require _evc.accountControllers[e.msg.sender].numElements == 1;
   
   disableController(e);

   bool controllerEnabled = _evc.isControllerEnabled(e, e.msg.sender, controller);
   
      
   assert !controllerEnabled, "the controller must be disabled by calling disableController";
}

rule controllerCantBeDisabledWhileHavingOutstandingDebt
 {
   env e;
   address controller;
   require e.msg.sender != evcAddress();
   require _evc.isControllerEnabled(e, e.msg.sender, controller);
   require getOwedOf(e, e.msg.sender) != 0;
   requireInvariant NoDosDueToReentrancy(e);
   
   disableController@withrevert(e);
   assert lastReverted, "user shouldn't be able to disablecontroller while having some outstanding debt";
   
 }

//============================
// checkAccountStatus
//============================
rule checkAccountStatusValidatesCorrectly {
   env e;
   requireOnlyEvcChecks(e);
   require e.block.timestamp == 0;
   
   address account;
   RiskManagerHarness.Owed accountOwed = getOwedOf(account);
   
   address[] collaterals;
   require collaterals.length == 1; // be carefull

   bytes4 accountSelector = AccountStatusSelector();
   address oracle = getOracleAddress(e); // require env maybe not still

   RiskManagerHarness.VaultCache cache = getLoadVault(e); // as e.block.timestamp require that why not free
   
   uint liabilityValue = getLiabilityValueHarness(e, cache, account, accountOwed);
   uint collateralValue = getCollateralValueHarness(e, cache, account,collaterals);

   //action
   bytes4 returnValue = checkAccountStatus(e,account,collaterals);
   
   assert oracle == 0 => returnValue != accountSelector, "oracle is not validated correctly";
   assert oracle != 0 && accountOwed == 0 => returnValue == accountSelector, "magic value must be returned when account doesn't have any debt"; //check me separtely while commenting out previous

   assert oracle != 0 && accountOwed != 0 &&  collateralValue >  liabilityValue => returnValue == accountSelector, "when collatervalue > liabilityvalue magic value must be returned assuming oracle aint 0 address and user debt aint 0";

   assert oracle != 0 && accountOwed != 0 &&  collateralValue < liabilityValue => returnValue != accountSelector, "when collatervalue < liabilityvalue function must revert";

}
//======================
// check vault status
//====================

rule checkVaultStatusValidatesCorrectly {
   env e;
   requireOnlyEvcChecks(e);
   require e.block.timestamp == 0;
   
   RiskManagerHarness.VaultCache cache = getLoadVault(e); //load vault
   require cache.hookedOps == 0; // require hookedops to be zero inorder to not invoke callhooktarget

   uint snapshotBorrowsBeforeReset = snapshotBorrows(e);
   uint previousSupplySnapshotBeforeReset = previousSupplySnapshotHarness(e);

   bytes4 vaultSelector = VaultStatusSelector();

   //@note ACTION =================================
   bytes4 returnValue = checkVaultStatus(e);
   // ==============================================

   assert !cache.snapshotInitialized => returnValue == vaultSelector, "when snapshot aint initialized it must return magic value";

   assert cache.snapshotInitialized && totalBorrowsUp(e, cache) > cache.borrowCap && totalBorrowsUp(e, cache) > snapshotBorrowsBeforeReset => returnValue != vaultSelector, "vaultStatus must revert when totalborrows exceep the cap and snapshotborrows";

   assert cache.snapshotInitialized && totalAssetsExternal(e,cache) > cache.supplyCap && totalAssetsExternal(e, cache) > previousSupplySnapshotBeforeReset => returnValue != vaultSelector, "vaultStatus must revert when totalassets exceeds cap and previous totalsupply snapshot";

}

//@audit atleast for view functions write rules that verify whether they call validateoracle and account that is it
//@audit add unexpected method exist rule -> easy as only filter 3 functions + base functions as you can copy that from commonspec

//====================================================
// onlyEVcChecks modifier related rules 
//====================================================

//=====================
// cvl__evcmodifierBypass
//====================
function requireOnlyEvcChecks(env e) {
   require e.msg.sender == evcAddress() && _evc.areChecksInProgress(e);
}
//=======================



rule AccountStatusCheckIsRestricted {
   env e;
   calldataarg args;
   require (e.msg.sender != evcAddress() || !_evc.areChecksInProgress(e));

   checkAccountStatus@withrevert(e,args);
   assert lastReverted, "account status must revert when either evc aint caller or checks aint in progress";
}

rule VaultStatusCheckIsRestricted {
   env e;
   require (e.msg.sender != evcAddress() || !_evc.areChecksInProgress(e));

   checkVaultStatus@withrevert(e);
   
   assert lastReverted, "checkVaultStatus must revert when either evc aint caller or checks aint in progress";
}

rule noUnexpectedStateChangingMethodAvailable(method f) filtered {
    f -> !f.isView
   }{
   env e;
   calldataarg args;
 f(e,args);

   assert true => (filterABH(f) || f.selector == sig:disableController().selector ||f.selector == sig:checkVaultStatus().selector || f.selector == sig:checkAccountStatus(address,address[]).selector), "Unexpected Statechanging functions detected in riskmanager module";

}

rule disableControllerCantBeReentred {
   env e;
   require r_harness.vaultStorage.reentrancyLocked;

   disableController@withrevert(e);

   assert lastReverted, "disableController() can't be reentred";
}

//==============================================================================
// Both view functions validate oracle and controller before returning any value
//==============================================================================

rule accountLiquidityValidatesOracle {
   env e;
   calldataarg args;
   RiskManagerHarness.VaultCache cache = getLoadVault(e);
   require cache.oracle == 0;

   accountLiquidity@withrevert(e,args);

   assert lastReverted, "accountLiquidity() must validate oracle before returning any value";

}

rule accountLiquidityFullValidatesOracle {
   env e;
   calldataarg args;
   RiskManagerHarness.VaultCache cache = getLoadVault(e);
   require cache.oracle == 0;

   accountLiquidityFull@withrevert(e,args);

   assert lastReverted, "accountLiquidityFull() must validate oracle before returning any value";

}

rule accountLiquidityValidatesControllers {
   env e;
   bool liq;
   address account;
   
   RiskManagerHarness.VaultCache cache = getLoadVault(e);
   require !ValidateControllerHarness(e,cache, account);

   //action
   accountLiquidity@withrevert(e, account, liq);

   assert lastReverted, "accountLiquidity() must validate controllers(account) before returning any value";

}

rule accountLiquidityFullValidatesControllers {
   env e;
   bool liq;
   address account;
   
   RiskManagerHarness.VaultCache cache = getLoadVault(e);
   require !ValidateControllerHarness(e,cache, account);
   
   //action
   accountLiquidityFull@withrevert(e, account, liq);

   assert lastReverted, "accountLiquidity_() must validate controllers(account) before returning any value";

}
import "./Base.spec";
import "./MyCommon.spec";

using BorrowingHarness as b_harness;

methods {
    // dispatch and use MockFlashBorrow if more detailed implementation is required
    function _.onFlashLoan(bytes) external => NONDET;
    // custom
    // function cash() external returns (uint256) envfree; // vaultstorage.cash
    // function totalBorrowsExact() external returns (uint256) envfree; 

    function checkReentrancyLock() external returns bool envfree;

    function totalBorrowsCustom() external returns uint256 envfree; 
    function totalBorrowsUpCustom() external returns uint256 envfree;
    function debtUpOfCustom(address) external returns uint256 envfree;
    // function debtOf(e,address) external returns uint256 envfree; it causes initVault problems when set envfree

    function interestAccumulatorCustom() external returns uint256 envfree;
    function interestAccumulatorOfCustom(address) external returns uint256 envfree;
    
    function AssetBalance() external returns uint256 envfree;
    function AssetBalanceOf(address) external returns uint256 envfree;
    function BorrowingModuleAddress() external returns address envfree;
   
}

// used to test running time
use builtin rule sanity;
use invariant NoDosDueToReentrancy;

//=========//
//BORROW   //
//=========//


//================================

rule Borrow_totalBorrowsAndCashAccounting {
    env e;
    // Assume !UpdateVault()
    require e.block.timestamp == 0;

    uint amount;
    address receiver;
    require receiver != BorrowingModuleAddress(); // otherwise assetbalance asserts will go nuts

    uint previousBorrows;
    mathint assumedTotalBorrows = AllFormallyPossibleTotalBorrowValues(e, previousBorrows);
   
    uint previousUserData;
    mathint assumedUserData = AllFormallyPossibleUserDataValues(e, previousUserData);

    require interestAccumulatorCustom() == 1 && interestAccumulatorOfCustom(receiver) == 1;

    require totalBorrowsCustom() == assert_uint256(assumedTotalBorrows);
    require getUserDataCustom(e,receiver) == assert_uint256(assumedUserData);


    mathint totalBorrowsBefore = totalBorrowsUpCustom();
    mathint cashBefore = cash(e);
    mathint receiverAssetsBefore = AssetBalanceOf(receiver);



    borrow(e,amount,receiver);

    mathint totalBorrowsAfter = totalBorrowsUpCustom();
    mathint cashAfter = cash(e);
    mathint receiverAssetsAfter = AssetBalanceOf(receiver);


    
    assert amount == max_uint256 => totalBorrowsAfter == totalBorrowsBefore + cashBefore && cashAfter == 0 && receiverAssetsAfter == receiverAssetsBefore + cashBefore, "borrows must increase by storage_cash when demanded for max uint size And the cashBalance should be zero && assetBalanceOf(receiver) must increase by cashBefore()";
    
    assert amount < max_uint256 => totalBorrowsAfter == totalBorrowsBefore + amount && cashAfter == cashBefore - amount && receiverAssetsAfter == receiverAssetsBefore + amount, "borrows and cash must increase and decrease respectively by the exact amount when demanded in the reasonable quantity && assetBalanceOf(receiver) must increase by the given amount";

}


//===========
// REPAY
//===========
rule repay_CashAndBorrowAccounting {
    env e;
    // Assume !updateVault()
    require e.block.timestamp == 0;

    address evcCaller = actualCaller(e); //@note for testing what checkaccount_none does...
    require evcCaller != BorrowingModuleAddress(); 

    uint previousBorrows;
    mathint assumedTotalBorrows = AllFormallyPossibleTotalBorrowValues(e, previousBorrows);
   
    uint previousUserData;
    mathint assumedUserData = AllFormallyPossibleUserDataValues(e, previousUserData);


    uint amount;
    address receiver;

    require interestAccumulatorCustom() == 1 && interestAccumulatorOfCustom(receiver) == 1; 

    require totalBorrowsCustom() == assert_uint256(assumedTotalBorrows);
    require getUserDataCustom(e,receiver) == assert_uint256(assumedUserData);

    mathint receiverDebt = debtOf(e,receiver);
    mathint cashBefore = cash(e);
    mathint totalBorrowBefore = totalBorrowsUpCustom();
    require totalBorrowBefore >= receiverDebt; //@note later test if it passes without this
    mathint evcCallerAssetsBefore = AssetBalanceOf(evcCaller);
    

    repay(e,amount,receiver);

    mathint cashAfter = cash(e);
    mathint totalBorrowAfter = totalBorrowsUpCustom();
    mathint evcCallerAssetsAfter = AssetBalanceOf(evcCaller);


    assert amount == max_uint256 => cashAfter == cashBefore + receiverDebt && totalBorrowAfter == totalBorrowBefore - receiverDebt && evcCallerAssetsAfter == evcCallerAssetsBefore - receiverDebt, "cash and totalborrows must increase and decrease respectively by the whole users debt when repayed with maxuint size amount && assets(caller) must decrease by receiverDebt";

    assert amount < max_uint256 => cashAfter == cashBefore + amount && totalBorrowAfter == totalBorrowBefore - amount && evcCallerAssetsAfter == evcCallerAssetsBefore - amount, "cash and totalborrows must increase and decrease respectively by the repayed amount when amount < overflow bounds  && assets(caller) must decrease by given amounts";


}

//=================
//repay with shares
//=================
//@audit-issue REPAYWITHSHARES IS PENDING 


//=============
// pullDebt
//================
rule pullDebt_TransferAccounting {
    env e;
    require e.block.timestamp == 0;

    uint previousBorrows;
    mathint assumedTotalBorrows = AllFormallyPossibleTotalBorrowValues(e, previousBorrows);
   
    uint previousUserData;
    mathint assumedUserData = AllFormallyPossibleUserDataValues(e, previousUserData);

    uint256 amount;
    address from;
    address evcCaller = actualCaller(e);

    
    require interestAccumulatorCustom() == 1 && interestAccumulatorOfCustom(from) == 1 && interestAccumulatorOfCustom(evcCaller) == 1;
    
    require totalBorrowsCustom() == assert_uint256(assumedTotalBorrows);
    require getUserDataCustom(e,from) == assert_uint256(assumedUserData);
    require getUserDataCustom(e,evcCaller) == assert_uint256(assumedUserData);

    mathint fromDebtBefore = debtOf(e,from);
    mathint toDebtBefore = debtOf(e,evcCaller);

   

    pullDebt(e, amount, from);

    mathint fromDebtAfter = debtOf(e,from);
    mathint toDebtAfter = debtOf(e,evcCaller);

    assert amount == max_uint256 => fromDebtAfter == 0 && toDebtAfter == toDebtBefore + fromDebtBefore, "from and to debts must increase/decrease respectively by the totalDebt of from when transferred with max uint quantity";

    assert amount < max_uint256 =>  (toDebtAfter == toDebtBefore + amount) && (fromDebtAfter == fromDebtBefore - amount) , "from and to debts must increase/decrease repectively by given amount when transferred within overflow bounds";
    
}

rule pullDebt_NoSelfTransfersArePossible {
    env e;
    require e.block.timestamp == 0;

    uint256 amount;
    address from;
    address evcCaller = actualCaller(e);


    pullDebt@withrevert(e, amount, from);

    assert evcCaller == from => lastReverted, "self transfers must be prevented";
}

//======
//flashLoan
//=====

rule flashLoan_MaintainsAssetBalance {
    env e;
    uint256 amount;
    bytes _data;

    mathint assetBalanceBefore = AssetBalance();
   
    flashLoan(e, amount, _data);
   
    mathint assetBalanceAfter = AssetBalance();

    assert assetBalanceAfter >= assetBalanceBefore, "asset balances must not decrease with flashloan";

}

rule flashLoan_doesntAffectStorage {
    env e;
    uint256 amount;
    bytes _data;

    storage init = lastStorage;
    flashLoan(e, amount, _data);
    assert lastStorage[currentContract] == init[currentContract], "flashLoan doesn't affect the storage by any means";
}
//======================================
// Twisted Rules
//=======================================
// except for flashLoan that requires different kind of msg.sender jujitsu
rule OnlyEVCcanCallStateChangingMethods(method f) filtered {
    f -> f.selector == sig:borrow(uint256,address).selector ||
    f.selector == sig:repay(uint256,address).selector ||
    f.selector == sig:repayWithShares(uint256,address).selector ||
    f.selector == sig:pullDebt(uint256,address).selector ||
    f.selector == sig:touch().selector 
}{
    env e;
    calldataarg args;

    
    require e.msg.sender != evcAddress(e);

    
    f@withrevert(e,args);
    assert lastReverted, "calls must only be allowed from EVC";
    
}



// check unexpected methods
rule NoUnexpectedMethodsAvailable(env e, method f, calldataarg args) filtered{
    f -> !f.isView
} {
    
    f(e,args);

    assert true => borrowNonViews(f) || filterABH(f) || filterBorrowHarness(f), "Unexpected Statechanging functions detected in borrowing module";
}

//@audit-ok verified though not mutated
// verifies that reentrancy by default is always set to false, and no dos is possible due to it
invariant NoDosDueToReentrancy(env e)
  !checkReentrancyLock(e);


// verifies that state changing functions can't be reentered
rule ReentrancyLockWorksCorrect(method f) filtered {
    f -> !f.isView
}
{
    env e;
    calldataarg args;
    
    //@note assume reentracy lock to be true
    require checkReentrancyLock();
    
    f@withrevert(e,args);
 

    assert borrowNonViews(f) => lastReverted, "no reentrancy is possible on the state changing methods";
}

//===========================
// CVL HELPERS
//==============================

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


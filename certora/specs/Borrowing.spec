import "./Base.spec";
import "./MyCommon.spec";

methods {
    // dispatch and use MockFlashBorrow if more detailed implementation is required
    function _.onFlashLoan(bytes) external => NONDET;
    // custom
    function cash() external returns (uint256) envfree; // vaultstorage.cash
    function totalBorrowsExact() external returns (uint256) envfree; // vaultstorage.totalBorrows, //@audit this is causing problems in invariants as the function calls loadVault that potentially modifies state, later debug this:= https://prover.certora.com/output/951980/d65035b8784c47f6b6ee6aa9d83532a3/?anonymousKey=d165951eae1765a458f07935e6e0ac96aa955a86 but for now create your own custom function for that that directly access vaultStorage just like cash() does

    function checkReentrancyLock() external returns bool envfree;

    function totalBorrowsCustom() external returns uint256 envfree; //totalborrows
    // function getTotalBalance() external returns uint112 envfree; //totalshares --> incompatable errors
   
}

// used to test running time
use builtin rule sanity;

//==================
// custom
//==================
//@audit-issue  for catching borrowutil/balanceutil specific mutations, you will do that at the last of writing every spec to write a specific spec that only catches balanceUtil's used functions mutations...
//@audit-issue i might have to create harness for initoperation that takes uint as flag for different operations like OP_BORROW, Op_REPAY etc

//@note first write the main properties of methods then write variable transitions then finally write the authorization thing that happens via evc, you might have to write well prepared preconditions that can make sense for the EVC authorization and finally write those high level invariants and rules


//=========//
//BORROW   //
//=========//


//================================
//@note we will write that kind of spec at last that deals with initoperation
//@note for catching the `if (assets > vaultCache.cash) revert E_InsufficientCash();` mutation i will have to first understand initoperation deeply and pass the rule on correct implementation without any kind of reverts 
//// also commented this out and check that the function still reverts without this check when the amounts are greater than cash reserves



//@note catching `     Assets assets = amount == type(uint256).max ? vaultCache.cash : amount.toAssets();` mutation is silly since i dont think any severe impact could be there anyway we will write a rule where the param ==maxuint only gives out .cash reserves, the amount < max112 gives out or pushes and decreases cash/asset balance by the same given amount (remember number > max112) will always revert by typeConversion

        
//@note `if (assets.isZero()) return 0;`  i think can be caught by above rule, where you will verify that when the amounts are greater than 0 and lesser than above rule checks the .cash and assets balances update accordingly... this will definitely catch the mutation where if the nonzero amounts get returned then the balances won't be updated ...

//@note `increaseBorrow(vaultCache, account, assets);` mutation where maybe certora team just calls decreaseborrow can also be caught by the above twos since you will be checking the end state results, i.e i will be checking vaultstorage.totalborrows to be increasing

//useful to catch if decreaseborrow is used instead of increaseBorrow and if pullassets was used instead of pushassets but remember we don't catch the borrowutil mutation in this we got to either write it deeply or write another rule @note best would be to write separate rule for that
//@note pending: reverting rule, initoperation rule, specific borrowutil rules
rule Borrow_totalBorrowsAndCashAccounting {
    env e;
    uint amount;
    address receiver;
    mathint totalBorrowsBefore = totalBorrowsCustom();
    mathint cashBefore = cash();

    borrow(e,amount,receiver);

    mathint totalBorrowsAfter = totalBorrowsCustom();
    mathint cashAfter = cash();

    //@audit-ok this passes
    assert amount == max_uint256 && cashBefore > 0 => totalBorrowsAfter > totalBorrowsBefore && cashAfter == 0, "borrows must increase by cashamounts when demanded for max uint size And the cashBalance should be zero";
    //@audit-ok this passes
    assert amount <= max_uint112 && amount > 0 => totalBorrowsAfter > totalBorrowsBefore && cashAfter == cashBefore - amount, "borrows and cash must increase and decrease respectively by the exact amount when demanded in the reasonable quantity";
    

    //@audit-issue : assert amount <= max_uint112 => totalBorrowsAfter == totalBorrowsBefore + amount detects the bug in AssetsLib's toOwed() function where 1 is converted into 0x80000000 crazy number

    // assert amount <= max_uint112 => totalBorrowsAfter == totalBorrowsBefore + amount && cashAfter == cashBefore - amount, "borrows and cash must increase and decrease respectively by the exact amount when demanded in the reasonable quantity";

    //  assert amount == max_uint256 => totalBorrowsAfter == totalBorrowsBefore + cashBefore && cashAfter == 0, "borrows must increase by cashamounts when demanded for max uint size And the cashBalance should be zero"; //https://prover.certora.com/output/951980/3616d9e1793e4adf83a1bc2328a59809/?anonymousKey=e6a3beb0ab03d9604e3c35a236416c7272b832e3

}



//@note maybe reason about the increaseBorrow mutations that write rules for them too

//@note `pushAssets(vaultCache, receiver, assets);` maybe certora team uses pullassets mutation for that write the rule that benchmarks .cash and .asset.balanceOf decreases with the amount specified 

//@note and maybe write the fullfledged rule that catches pushAssets mutations also

//@note atlast write a rule that checks that the borrow rule doesn't revert unexpectedly subtracting all the reverting cases


//===========
// REPAY
//===========
rule repay_CashAndBorrowAccounting {
    env e;
    mathint cashBefore = cash();
    mathint totalBorrowBefore = totalBorrowsCustom();

    uint amount;
    address receiver;

    repay(e,amount,receiver);

    mathint cashAfter = cash();
    mathint totalBorrowAfter = totalBorrowsCustom();

    //@audit-issue handle the case for maxuint and first write the true property that includes the amounts also that might catch that toOwed Bug::::

    //@note writing the general property
    //@audit-issue : this catched some crazy issue to debug later
    // assert amount < max_uint256 => cashAfter == cashBefore + amount && totalBorrowAfter == totalBorrowBefore - amount, "cash-borrow__must increase/decrease by amount respectively";\
    

    //@note writing property that might pass
     assert amount < max_uint256 && amount > 0 => cashAfter == cashBefore + amount && totalBorrowAfter < totalBorrowBefore , "cash-borrow__must increase/decrease by amount respectively";
     //@audit this too failed:: write rule that checks that userdata decreases ....++ you might have to require that anyuser data is lesser than totalshares and totalborrows... maybe create harness that gets onbehalf of account then check against him
     // also ask cantina ping how does data differentiate between borrows and shares... // may be by the type of vault they have


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

//@audit-ok verified though not mutated
// verifies that reentrancy by default is always set to false, and no dos is possible due to it
invariant NoDosDueToReentrancy(env e)
  !checkReentrancyLock(e);


//================================
// HIGH LEVEL RULES
//================================
//@audit if borrow reverts when user demands more assets than vaultStorage.cash doesn't it mean that there is invariant relation that vaultborrows <= vaultstorage.cash
//.totalBorrows <= .cash
//@note run at last because debugging high level is very hard
//@note it is very hard to debug and find requireInvariants for now, ignore high level rules
// invariant borrowsToCash() 
//     cash() >= totalBorrowsCustom();

//@audit-issue fails
invariant Solvency(env e, address user)
 getUserDataCustom(e,user) <= totalBorrowsCustom();
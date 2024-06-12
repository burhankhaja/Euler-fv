// @note catches both Borrowing_0 and AssetTransfers_0 public mutations

import "./Borrowing.spec";

// Prove Only borrow() can decrease cash() 
rule cashMustNotDecreaseWithoutBorrowing {
    env e;
    method f;
    calldataarg args;
    uint cashBefore = cash();

    f(e,args);
    
    uint cashAfter = cash();

    assert  cashAfter < cashBefore => f.selector == sig:borrow(uint256,address).selector , "only borrow() method must decrease valtStorage.cash reserves"; 
}
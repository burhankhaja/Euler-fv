import "./VaultFull.spec";
import "./MyCommon.spec";

// simple to run rules are imported from Vault.spec, others are left out. 
// to run the more complex rules, use Vault_complex_verified.conf
use rule conversionOfZero;
use rule conversionWeakIntegrity;
use rule conversionWeakMonotonicity;
use rule convertToAssetsWeakAdditivity;
use rule convertToCorrectness;
use rule convertToSharesWeakAdditivity;
use rule zeroDepositZeroShares;


rule deposit_MustReturnOnZeroSharesBalance {
        env e;
        require e.block.timestamp == 0;
        VaultHarness.VaultCache cache = getLoadVault(e);
        
        uint amount;
        address receiver;
        address evcCaller = actualCaller(e);
        VaultHarness.Assets evcCallerAssetBalance = UintToAssets(e, assetBalanceOf(e, evcCaller));
        VaultHarness.Assets amountToAssets = UintToAssets(e, amount); // only for using in tosharesdown
        VaultHarness.Shares shares = toSharesDownExt(e, amountToAssets, cache);

        // ACTION
        deposit@withrevert(e, amount, receiver);

        assert shares == 0 => lastReverted , "no deposits should be allowed, when no shares are in circulation";

}

rule deposit_AccountingIntegrity {
        env e;
        require e.block.timestamp == 0;
        VaultHarness.VaultCache cache = getLoadVault(e);
        
        uint amount;
        address receiver;
        address evcCaller = actualCaller(e);
        VaultHarness.Assets evcCallerAssetBalanceBefore = UintToAssets(e, assetBalanceOf(e, evcCaller));
        VaultHarness.Assets amountToAssets = UintToAssets(e, amount); // only for using in tosharesdown
        VaultHarness.Shares shares = toSharesDownExt(e, amountToAssets, cache);

        mathint receiverShares_b = shareBalanceOf(e, receiver);

        mathint cashBefore = storage_cash(e);
        mathint totalshares_b = storage_totalShares(e);

        // ACTION
        deposit(e, amount, receiver);
        
        mathint cashAfter = storage_cash(e);
        mathint receiverShares_a = shareBalanceOf(e, receiver);
        mathint totalshares_a = storage_totalShares(e);

        assert amount == max_uint256 => cashAfter == cashBefore + evcCallerAssetBalanceBefore, "cash must increase by whole asset balance of caller when demanded for maxuint";
        assert amount < max_uint256 => cashAfter == cashBefore + amountToAssets, "cashes must increase by the amount";
        assert amount > 0 => receiverShares_a > receiverShares_b && totalshares_a > totalshares_b, "receiver shares must increase and so does the totalshares";
}

rule IsBalanceIncreasedAndDecreasedAsExpected {
    method f;
    env e;
    calldataarg args;
    mathint totalshares_before = storage_totalShares(e);

    f(e,args);

    mathint totalshares_after = storage_totalShares(e);

    assert totalshares_after > totalshares_before => f.selector == sig:skim(uint256 , address).selector ||
    f.selector == sig:mint(uint256,address).selector || f.selector == sig:deposit(uint256,address).selector, "only mint, deposit and skim can increase shares balances";

    assert totalshares_after < totalshares_before => f.selector == sig:withdraw(uint256 , address,address).selector ||
    f.selector == sig:redeem(uint256,address,address).selector , "only redeem and withdraw  can decrease shares balances";

}



rule NoUnexpectedStateChangingMethod(method f) filtered {
    f -> !f.isView
} {
    env e;
    calldataarg args;

    f(e, args);

    assert true => filterABH(f) ||
     f.selector == sig:deposit(uint256 , address ).selector ||
 f.selector == sig:mint(uint256 , address ).selector ||
 f.selector == sig:withdraw(uint256 , address , address).selector ||
 f.selector == sig:redeem(uint256 , address , address).selector ||
 f.selector == sig:skim(uint256 , address ).selector ||
f.selector == sig:approve(address,uint256).selector ||
f.selector == sig:transfer(address,uint256).selector ||
f.selector == sig:transferFrom(address,address,uint256).selector ||
f.selector == sig:transferFromMax(address,address).selector , "Possibly buggy code detected";



}

rule evcIsAuthenticated(method f) filtered {
    f -> f.selector == sig:deposit(uint256 , address ).selector ||
 f.selector == sig:mint(uint256 , address ).selector ||
 f.selector == sig:withdraw(uint256 , address , address).selector ||
 f.selector == sig:redeem(uint256 , address , address).selector ||
 f.selector == sig:skim(uint256 , address ).selector
} {
    env e;
    calldataarg args;

    require e.msg.sender != evcAddress(e);

    
    f@withrevert(e,args);
    assert lastReverted, "calls must only be allowed from EVC";
}



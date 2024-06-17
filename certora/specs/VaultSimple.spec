import "./VaultFull.spec";

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

        uint cashBefore = storage_cash(e);

        // ACTION
        deposit(e, amount, receiver);
        
        uint cashBefore = storage_cash(e);

        /*
        @note finalizeDeposit(vaultCache, assets, shares, account, receiver);
        assets -> in case of maxuint--- callerbalance
        else amount.toAssets ---> amountToassets
        
        */
        // assets == vaultCache.asset.balanceOf(account).toAssets()
        assert amount == max_uint256 => cashAfter == cashBefore + evcCallerAssetBalanceBefore
       

}



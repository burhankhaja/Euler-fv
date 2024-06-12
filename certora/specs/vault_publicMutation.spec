import "./VaultFull.spec";

methods {
    // storage_cash() already declared in VaultFull.spec
    function assetBalanceOfVault() external returns uint envfree;
}

// @note catches Vault_0 public mutation
// Prove that skim only happens when assetBalance is greater than storage_cash()
rule skimWorksAsExpected {
    env e;
    uint256 amount;
    address receiver;
    mathint VaultAssetBalance = assetBalanceOfVault();
    mathint cashBefore = storage_cash();
    require e.block.timestamp == 0; // Assume !updateVault()
    
    skim(e, amount, receiver);

    mathint cashAfter = storage_cash();

    assert VaultAssetBalance <= cashBefore => cashAfter == cashBefore, "skim must only happen when vaults underlying asset balances are greater than vaultStorage.cash";

}

    


/*
rule skim {
    balance = storageAsset.balanceOf(vault)
    cashBefore = storage.cash
    
    skim()
    cashAfter = storage.cash

    assert balance <= cashBefore => cashAfter == cashBefore
}

*/
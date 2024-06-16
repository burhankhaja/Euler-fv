import "./VaultFull.spec";

// simple to run rules are imported from Vault.spec, others are left out. 
// to run the more complex rules, use Vault_complex_verified.conf
// use rule conversionOfZero;
// use rule conversionWeakIntegrity;
// use rule conversionWeakMonotonicity;
// use rule convertToAssetsWeakAdditivity;
// use rule convertToCorrectness;
// use rule convertToSharesWeakAdditivity;
// use rule zeroDepositZeroShares;

rule only_excess_gets_skimmed(env e, calldataarg params) {
    env e;
    no_update_vault(e);
    
    mathint assets = ERC20a.balanceOf(currentContract);
    mathint init_cash = storage_cash();
    
    skim(e, params);

    mathint last_cash = storage_cash();

    assert assets <= init_cash => last_cash == init_cash, "Fund Drainage! only excessive must get skimmed";

}

function no_update_vault(env e) {
   require e.block.timestamp == 0;
}



// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.0;
import "../../../src/interfaces/IPriceOracle.sol";
import {ERC20} from "../../../lib/ethereum-vault-connector/lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";
import "../AbstractBaseHarness.sol";
import "../../../src/EVault/modules/RiskManager.sol";
// import "src/EVault/shared/types/UserStorage.sol";
import "../../../src/EVault/shared/types/Types.sol";

// import "src/interfaces/IPriceOracle.sol";

contract RiskManagerHarness is RiskManager, AbstractBaseHarness {
    constructor(Integrations memory integrations) RiskManager(integrations) {}

    function evcAddress() public view returns (address) {
        return address(evc);
    }

    function getOwedOf(address account) public view returns (Owed) {
        return vaultStorage.users[account].getOwed();
    }

    function riskManagerAddress() public view returns (address) {
        return address(this);
    }

    function AccountStatusSelector() public view returns (bytes4 magicValue) {
        magicValue = IEVCVault.checkAccountStatus.selector;
    }

    function VaultStatusSelector() public view returns (bytes4 magicValue) {
        magicValue = IEVCVault.checkVaultStatus.selector;
    }

    function getOracleAddress() public view returns (address) {
        (, IPriceOracle oracle, ) = ProxyUtils.metadata();
        return address(oracle);
    }

    function getLoadVault() public view returns (VaultCache memory vaultCache) {
        return loadVault();
    }

    function getLiabilityValueHarness(
        VaultCache memory vaultCache,
        address account,
        Owed owed
    ) public view virtual returns (uint256) {
        return getLiabilityValue(vaultCache, account, owed, false);
    }

    function getCollateralValueHarness(
        VaultCache memory vaultCache,
        address account,
        address[] memory collateral
    ) public view returns (uint256) {
        return getCollateralValue(vaultCache, account, collateral[0], false);
    }

    function totalBorrowsUp(
        VaultCache memory vaultCache
    ) public view returns (uint256) {
        return vaultCache.totalBorrows.toAssetsUp().toUint();
    }

    function snapshotBorrows() public view returns (uint) {
        return snapshot.borrows.toUint();
    }

    /**
    
            Assets snapshotCash = snapshot.cash;
            Assets snapshotBorrows = snapshot.borrows;

            uint256 prevBorrows = snapshotBorrows.toUint();
            uint256 borrows = vaultCache.totalBorrows.toAssetsUp().toUint();

            if (borrows > vaultCache.borrowCap && borrows > prevBorrows) revert E_BorrowCapExceeded();

            uint256 prevSupply = snapshotCash.toUint() + prevBorrows;
            uint256 supply = totalAssetsInternal(vaultCache);

            if (supply > vaultCache.supplyCap && supply > prevSupply) revert E_SupplyCapExceeded();
    
     */

    function previousSupplySnapshotHarness() public view returns (uint256) {
        return snapshot.cash.toUint() + snapshot.borrows.toUint();
    }

    function totalSupplyHarness(
        VaultCache memory vaultCache
    ) public pure returns (uint256) {
        return (vaultCache.cash.toUint() +
            vaultCache.totalBorrows.toAssetsUp().toUint());
    }

    function totalAssetsExternal(
        VaultCache memory vaultCache
    ) public pure returns (uint256) {
        return totalAssetsInternal(vaultCache);
    }

    function ValidateControllerHarness(
        VaultCache memory vaultCache,
        address account
    ) public view returns (bool) {
        address[] memory controllers = evc.getControllers(account);

        return controllers.length == 1 && controllers[0] == address(this);
    }
}

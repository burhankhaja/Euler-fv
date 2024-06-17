// SPDX-License-Identifier: GPL-2.0-or-later

pragma solidity ^0.8.0;
import "../../../src/interfaces/IPriceOracle.sol";
import {ERC20} from "../../../lib/ethereum-vault-connector/lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";
import "../AbstractBaseHarness.sol";
import "../../../src/EVault/modules/Liquidation.sol";
import "../../../src/EVault/shared/types/Types.sol";
import "../../../src/EVault/shared/types/UserStorage.sol";

contract LiquidationHarness is AbstractBaseHarness, Liquidation {
    using TypesLib for *;

    constructor(Integrations memory integrations) Liquidation(integrations) {}

    function calculateLiquidityExternal(
        address account
    ) public view returns (uint256 collateralValue, uint256 liabilityValue) {
        return
            calculateLiquidity(
                loadVault(),
                account,
                getCollaterals(account),
                true
            );
    }

    function calculateLiquidationExt(
        VaultCache memory vaultCache,
        address liquidator,
        address violator,
        address collateral,
        uint256 desiredRepay
    ) external view returns (LiquidationCache memory liqCache) {
        return
            calculateLiquidation(
                vaultCache,
                liquidator,
                violator,
                collateral,
                desiredRepay
            );
    }

    function isRecognizedCollateralExt(
        address collateral
    ) external view virtual returns (bool) {
        return isRecognizedCollateral(collateral);
    }

    function getLiquidator() external returns (address liquidator) {
        (, liquidator) = initOperation(OP_LIQUIDATE, CHECKACCOUNT_CALLER);
    }

    function getCurrentOwedExt(
        VaultCache memory vaultCache,
        address violator
    ) external view returns (Assets) {
        return getCurrentOwed(vaultCache, violator).toAssetsUp();
    }

    function getCollateralValueExt(
        VaultCache memory vaultCache,
        address account,
        address collateral,
        bool liquidation
    ) external view returns (uint256 value) {
        return getCollateralValue(vaultCache, account, collateral, liquidation);
    }

    function evcAddress() public view returns (address) {
        return address(evc);
    }

    function getLoadVault() public view returns (VaultCache memory vaultCache) {
        return loadVault();
    }

    /**note this is just used to assume the correct state of the totalBorrows*/
    function AllFormallyPossibleTotalBorrowValues(
        uint _amount
    ) public view returns (Owed) {
        Assets _input = _amount.toAssets();
        Owed amount = _input.toOwed();
        return amount;
    }

    /**note similarly this one in spec returns all correct possible  user data values*/
    function AllFormallyPossibleUserDataValues(
        uint _amount
    ) public view returns (PackedUserSlot) {
        Assets _input = _amount.toAssets();
        Owed owed = _input.toOwed();
        PackedUserSlot emptyPreviousData;
        uint256 data = PackedUserSlot.unwrap(emptyPreviousData);
        uint256 OWED_OFFSET = 112;
        uint256 OWED_MASK = 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF0000000000000000000000000000;

        PackedUserSlot userData = PackedUserSlot.wrap(
            (owed.toUint() << OWED_OFFSET) | (data & ~OWED_MASK)
        );
        return userData;
        // self.data = PackedUserSlot.wrap((owed.toUint() << OWED_OFFSET) | (data & ~OWED_MASK));
    }

    function interestAccumulatorCustom() public view returns (uint256) {
        return vaultStorage.interestAccumulator;
    }

    function interestAccumulatorOfCustom(
        address _user
    ) public view returns (uint256) {
        return vaultStorage.users[_user].interestAccumulator;
    }

    function totalBorrowsCustom() public view returns (uint256) {
        return vaultStorage.totalBorrows.toUint();
    }

    function totalBorrowsUpCustom() public view returns (uint256) {
        return vaultStorage.totalBorrows.toAssetsUp().toUint();
    }

    function debtUpOfCustom(address account) public view returns (uint256) {
        return vaultStorage.users[account].getOwed().toAssetsUp().toUint();
    }

    function getUserDataCustom(
        address account
    ) external view returns (PackedUserSlot) {
        return vaultStorage.users[account].data;
    }

    function isLiquidationAllowedToDecrease(
        VaultCache memory vaultCache,
        LiquidationCache memory liqCache
    ) public view returns (bool) {
        return
            vaultCache.configFlags.isNotSet(CFG_DONT_SOCIALIZE_DEBT) &&
            liqCache.liability > liqCache.repay &&
            checkNoCollateral(liqCache.violator, liqCache.collaterals);
    }
}

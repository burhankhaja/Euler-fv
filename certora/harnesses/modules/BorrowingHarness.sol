pragma solidity ^0.8.0;
import "../../../src/EVault/modules/Borrowing.sol";
import "../../../src/EVault/shared/types/UserStorage.sol";
import "../../../src/EVault/shared/types/Types.sol";
import {ERC20} from "../../../lib/ethereum-vault-connector/lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";
import "../AbstractBaseHarness.sol";

uint256 constant SHARES_MASK = 0x000000000000000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFF;

contract BorrowingHarness is AbstractBaseHarness, Borrowing {
    using TypesLib for uint256;

    constructor(Integrations memory integrations) Borrowing(integrations) {}

    function initOperationExternal(
        uint32 operation,
        address accountToCheck
    ) public returns (VaultCache memory vaultCache, address account) {
        return initOperation(operation, accountToCheck);
    }

    function getTotalBalance() external view returns (Shares) {
        return vaultStorage.totalShares;
    }

    function toAssetsExt(uint256 amount) external pure returns (uint256) {
        return TypesLib.toAssets(amount).toUint();
    }

    function unpackBalanceExt(
        PackedUserSlot data
    ) external view returns (Shares) {
        return Shares.wrap(uint112(PackedUserSlot.unwrap(data) & SHARES_MASK));
    }

    function getUserInterestAccExt(
        address account
    ) external view returns (uint256) {
        return vaultStorage.users[account].interestAccumulator;
    }

    function getVaultInterestAccExt() external returns (uint256) {
        VaultCache memory vaultCache = updateVault();
        return vaultCache.interestAccumulator;
    }

    function getUnderlyingAssetExt() external returns (IERC20) {
        VaultCache memory vaultCache = updateVault();
        return vaultCache.asset;
    }

    //========================
    // custom
    //========================
    function checkReentrancyLock() public view returns (bool) {
        return vaultStorage.reentrancyLocked;
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

    function evcAddress() public view returns (address) {
        return address(evc);
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

    function AssetBalance() public view returns (uint256) {
        (IERC20 asset, , ) = ProxyUtils.metadata();
        return asset.balanceOf(address(this));
    }

    function AssetBalanceOf(address user) public view returns (uint256) {
        (IERC20 asset, , ) = ProxyUtils.metadata();
        return asset.balanceOf(address(user));
    }

    function BorrowingModuleAddress() public view returns (address) {
        return address(this);
    }
}

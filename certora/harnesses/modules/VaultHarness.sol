// SPDX-License-Identifier: GPL-2.0-or-later

pragma solidity ^0.8.0;
// import {IERC20} from "../../lib/ethereum-vault-connector/lib/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import "../../../certora/harnesses/AbstractBaseHarness.sol";
import "../../../src/EVault/modules/Vault.sol";
import "../../../src/EVault/modules/Token.sol";

contract VaultHarness is VaultModule, TokenModule, AbstractBaseHarness {
    using TypesLib for *;
    using UserStorageLib for *;

    constructor(Integrations memory integrations) Base(integrations) {}

    // Linked against DummyERC20A in verification config
    IERC20 underlying_asset;

    function userAssets(address user) public view returns (uint256) {
        // harnessed
        // The assets in the underlying asset contract (not in the vault)
        return IERC20(asset()).balanceOf(user);
        // The assets stored in the vault for a user.
        // return vaultStorage.users[user].getBalance().toAssetsDown(loadVault()).toUint();
    }

    function updateVault()
        internal
        override
        returns (VaultCache memory vaultCache)
    {
        // initVaultCache is difficult to summarize because we can't
        // reason about the pass-by-value VaultCache at the start and
        // end of the call as separate values. So this harness
        // gives us a way to keep the loadVault summary when updateVault
        // is called
        vaultCache = loadVault();
        if (block.timestamp - vaultCache.lastInterestAccumulatorUpdate > 0) {
            vaultStorage.lastInterestAccumulatorUpdate = vaultCache
                .lastInterestAccumulatorUpdate;
            vaultStorage.accumulatedFees = vaultCache.accumulatedFees;

            vaultStorage.totalShares = vaultCache.totalShares;
            vaultStorage.totalBorrows = vaultCache.totalBorrows;

            vaultStorage.interestAccumulator = vaultCache.interestAccumulator;
        }
        return vaultCache;
    }

    // VaultStorage Accessors:
    function storage_lastInterestAccumulatorUpdate()
        public
        view
        returns (uint48)
    {
        return vaultStorage.lastInterestAccumulatorUpdate;
    }

    function storage_cash() public view returns (Assets) {
        return vaultStorage.cash;
    }

    function storage_supplyCap() public view returns (uint256) {
        return vaultStorage.supplyCap.resolve();
    }

    function storage_borrowCap() public view returns (uint256) {
        return vaultStorage.borrowCap.resolve();
    }

    // reentrancyLocked seems not direclty used in loadVault
    function storage_hookedOps() public view returns (Flags) {
        return vaultStorage.hookedOps;
    }

    function storage_snapshotInitialized() public view returns (bool) {
        return vaultStorage.snapshotInitialized;
    }

    function storage_totalShares() public view returns (Shares) {
        return vaultStorage.totalShares;
    }

    function storage_totalBorrows() public view returns (Owed) {
        return vaultStorage.totalBorrows;
    }

    function storage_accumulatedFees() public view returns (Shares) {
        return vaultStorage.accumulatedFees;
    }

    function storage_interestAccumulator() public view returns (uint256) {
        return vaultStorage.interestAccumulator;
    }

    function storage_configFlags() public view returns (Flags) {
        return vaultStorage.configFlags;
    }

    function cache_cash() public view returns (Assets) {
        return loadVault().cash;
    }

    //=============
    // custom
    //============

    function assetBalanceOfVault() public view returns (uint) {
        (IERC20 asset, , ) = ProxyUtils.metadata();
        return asset.balanceOf(address(this));
    }

    function assetBalanceOf(address account) public view returns (uint) {
        (IERC20 asset, , ) = ProxyUtils.metadata();
        return asset.balanceOf(account);
    }

    function evcAddress() public view returns (address) {
        return address(evc);
    }

    function getLoadVault() public view returns (VaultCache memory vaultCache) {
        return loadVault();
    }

    function toSharesDownExt(
        Assets amount,
        VaultCache memory vaultCache
    ) public pure returns (Shares) {
        return AssetsLib.toSharesDown(amount, vaultCache);
    }

    function UintToAssets(uint _num) public pure returns (Assets) {
        return TypesLib.toAssets(_num);
    }

    function shareBalanceOf(address account) public view returns (Shares) {
        return vaultStorage.users[account].getBalance();
    }
}

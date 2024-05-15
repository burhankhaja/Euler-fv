// SPDX-License-Identifier: GPL-2.0-or-later

pragma solidity ^0.8.0;

import {SafeERC20Lib} from "./lib/SafeERC20Lib.sol";
import {Base} from "./Base.sol";

import "./types/Types.sol";

/// @title AssetTransfers
/// @author Euler Labs (https://www.eulerlabs.com/)
/// @notice Transfer assets into and out of the vault
abstract contract AssetTransfers is Base {
    using TypesLib for uint256;
    using SafeERC20Lib for IERC20;

    function pullAssets(VaultCache memory vaultCache, address from, Assets amount) internal virtual {
        vaultCache.asset.safeTransferFrom(from, address(this), amount.toUint(), permit2);
        vaultStorage.cash = vaultCache.cash = vaultCache.cash + amount;
    }

    /// @dev If the `CFG_EVC_COMPATIBLE_ASSET` flag is set, the function will protect users against mistakenly sending the funds
    /// to EVC sub-accounts. Functions that push tokens out (`withdraw`, `redeem`, `borrow`) accept a `receiver` argument.
    /// If the user set one of their sub-accounts (not owner) as a receiver, funds would be lost, because a regular asset doesn't
    /// support EVC's sub-accounts. The private key to a sub-account (not owner) is not known, so user would not be able to move
    /// the funds out. The function will make a best effort to prevent this by checking if the receiver of the token
    /// is recognized by EVC as non-owner sub-account. In other words, if there is an account registered in EVC as owner matching the
    /// intended receiver, transfer will be prevented. There is guarantee however that EVC will have the owner registered.
    ///
    /// If the asset itself is compatible with EVC, it is safe to not set the flag and send the asset to a non-owner sub-account.
    /// the transfer will be prevented.
    function pushAssets(VaultCache memory vaultCache, address to, Assets amount) internal virtual {
        if (
            to == address(0)
                || (vaultCache.configFlags.isNotSet(CFG_EVC_COMPATIBLE_ASSET) && isKnownNonOwnerAccount(to))
        ) {
            revert E_BadAssetReceiver();
        }

        vaultStorage.cash = vaultCache.cash = vaultCache.cash - amount;
        vaultCache.asset.safeTransfer(to, amount.toUint());
    }
}

// SPDX-License-Identifier: GPL-2.0-or-later

pragma solidity ^0.8.0;

import "./BaseIRMLinearKink.sol";

contract IRMClassUSDT is BaseIRMLinearKink {
    constructor(bytes32 gitCommit_)
        BaseIRMLinearKink(
            gitCommit_,
            // Base=0% APY,  Kink(80%)=7% APY  Max=200% APY
            0,
            623991132,
            38032443588,
            3435973836
        )
    {}
}

// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.0;
import {ERC20} from "../../../lib/ethereum-vault-connector/lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";
import "../AbstractBaseHarness.sol";
import "../../../src/EVault/modules/Governance.sol";

contract GovernanceHarness is Governance, AbstractBaseHarness {
    constructor(Integrations memory integrations) Governance(integrations) {}

    function isGovernor() public view returns (bool) {
        return vaultStorage.governorAdmin == EVCAuthenticateGovernor();
    }
}

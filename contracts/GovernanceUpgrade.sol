
    // SPDX-License-Identifier: MIT
    pragma solidity ^0.8.0;
    
    import "./Governance.sol";
    
    contract GovernanceUpgrade is Governance {
        // Add new functions or override existing ones
        function newFeature() public pure returns (string memory) {
            return "Upgraded contract";
        }
    }
    
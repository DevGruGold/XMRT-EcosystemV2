// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Governance {
    address public constant DOMAIN_WALLET = 0x7099F848b614d0d510BeAB53b3bE409cbd720dF5;
    address public constant AI_LEADER = 0x77307DFbc436224d5e6f2048d2b6bDfA66998a15;
}


// Security enhancements
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// Add to contract definition: is ReentrancyGuard, Ownable
// Example modifier: onlyOwner

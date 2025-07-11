// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

contract XMRT is
    Initializable,
    ERC20Upgradeable,
    AccessControlUpgradeable,
    ReentrancyGuardUpgradeable,
    PausableUpgradeable,
    UUPSUpgradeable
{
    uint256 public constant MAX_SUPPLY = 21_000_000 * 10**18;
    uint256 public constant MIN_STAKE_PERIOD = 7 days;
    address public constant BURN_ADDRESS = 0x7099F848b614d0d510BeAB53b3bE409cbd720dF5;
    address public constant ADMIN = 0x7099F848b614d0d510BeAB53b3bE409cbd720dF5;
    address public constant ORACLE = 0x7099F848b614d0d510BeAB53b3bE409cbd720dF5;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");

    uint256 public totalStaked;

    struct UserStake {
        uint128 amount;
        uint64 timestamp;
    }
    mapping(address => UserStake) public userStakes;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);

    function initialize() public initializer {
        __ERC20_init("XMR Token", "XMRT");
        __AccessControl_init();
        __ReentrancyGuard_init();
        __Pausable_init();
        __UUPSUpgradeable_init();

        _mint(msg.sender, MAX_SUPPLY);
        _setupRole(DEFAULT_ADMIN_ROLE, ADMIN);
        _setupRole(ADMIN_ROLE, ADMIN);
        _setupRole(ORACLE_ROLE, ORACLE);
    }

    function _authorizeUpgrade(address) internal override onlyRole(ADMIN_ROLE) {}

    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot stake zero");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        _transfer(msg.sender, address(this), amount);
        userStakes[msg.sender].amount += uint128(amount);
        userStakes[msg.sender].timestamp = uint64(block.timestamp);
        totalStaked += amount;
        emit Staked(msg.sender, amount);
    }

    function unstake(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot unstake zero");
        require(userStakes[msg.sender].amount >= amount, "Insufficient staked");
        uint256 penalty = 0;
        if (block.timestamp < userStakes[msg.sender].timestamp + MIN_STAKE_PERIOD) {
            penalty = amount / 10;
            _burn(address(this), penalty);
            amount -= penalty;
        }
        userStakes[msg.sender].amount -= uint128(amount + penalty);
        totalStaked -= (amount + penalty);
        _transfer(address(this), msg.sender, amount);
        emit Unstaked(msg.sender, amount);
    }
}


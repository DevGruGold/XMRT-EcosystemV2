// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";

// Wormhole imports (conceptual - actual imports would depend on Wormhole SDK)
interface IWormholeRelayer {
    function sendPayloadToEvm(
        uint16 targetChain,
        address targetAddress,
        bytes memory payload,
        uint256 receiverValue,
        uint256 gasLimit
    ) external payable returns (uint64 sequence);
}

interface IWormholeReceiver {
    function receiveWormholeMessages(
        bytes memory payload,
        bytes[] memory additionalVaas,
        bytes32 sourceAddress,
        uint16 sourceChain,
        bytes32 deliveryHash
    ) external payable;
}

// LayerZero imports (conceptual - actual imports would depend on LayerZero SDK)
interface ILayerZeroEndpoint {
    function send(
        uint16 _dstChainId,
        bytes calldata _destination,
        bytes calldata _payload,
        address payable _refundAddress,
        address _zroPaymentAddress,
        bytes calldata _adapterParams
    ) external payable;
}

interface ILayerZeroReceiver {
    function lzReceive(
        uint16 _srcChainId,
        bytes calldata _srcAddress,
        uint64 _nonce,
        bytes calldata _payload
    ) external;
}

/**
 * @title XMRTCrossChain
 * @dev Enhanced XMRT token with cross-chain capabilities via Wormhole and LayerZero
 */
contract XMRTCrossChain is 
    Initializable,
    ERC20Upgradeable,
    ERC20PausableUpgradeable,
    AccessControlUpgradeable,
    UUPSUpgradeable,
    ReentrancyGuardUpgradeable,
    IWormholeReceiver,
    ILayerZeroReceiver
{
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");
    bytes32 public constant BRIDGE_ROLE = keccak256("BRIDGE_ROLE");

    uint256 public constant TOTAL_SUPPLY = 21_000_000 * 10**18;
    uint256 public constant MIN_STAKE_DURATION = 7 days;
    uint256 public constant EARLY_UNSTAKE_PENALTY = 10; // 10%

    // Cross-chain infrastructure
    IWormholeRelayer public wormholeRelayer;
    ILayerZeroEndpoint public layerZeroEndpoint;
    
    // Cross-chain configuration
    mapping(uint16 => bytes32) public trustedRemotes; // LayerZero chain ID => trusted remote address
    mapping(uint16 => address) public wormholePeers; // Wormhole chain ID => peer contract address
    
    // Staking data
    struct UserStake {
        uint128 amount;
        uint64 timestamp;
    }
    
    mapping(address => UserStake) public userStakes;
    uint256 public totalStaked;

    // Cross-chain governance
    struct CrossChainProposal {
        uint256 id;
        string description;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 deadline;
        bool executed;
        mapping(address => bool) hasVoted;
        mapping(uint16 => bool) chainVoted; // Track which chains have voted
    }
    
    mapping(uint256 => CrossChainProposal) public proposals;
    uint256 public proposalCount;

    // Events
    event Staked(address indexed user, uint256 amount, uint256 timestamp);
    event Unstaked(address indexed user, uint256 amount, uint256 penalty);
    event CrossChainMessageSent(uint16 indexed targetChain, bytes32 indexed messageHash);
    event CrossChainMessageReceived(uint16 indexed sourceChain, bytes32 indexed messageHash);
    event ProposalCreated(uint256 indexed proposalId, string description, uint256 deadline);
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support, uint16 chainId);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(
        address _wormholeRelayer,
        address _layerZeroEndpoint
    ) public initializer {
        __ERC20_init("XMRT Token", "XMRT");
        __ERC20Pausable_init();
        __AccessControl_init();
        __UUPSUpgradeable_init();
        __ReentrancyGuard_init();

        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(ORACLE_ROLE, msg.sender);

        wormholeRelayer = IWormholeRelayer(_wormholeRelayer);
        layerZeroEndpoint = ILayerZeroEndpoint(_layerZeroEndpoint);

        _mint(msg.sender, TOTAL_SUPPLY);
    }

    // Cross-chain configuration functions
    function setTrustedRemote(uint16 _chainId, bytes32 _trustedRemote) external onlyRole(ADMIN_ROLE) {
        trustedRemotes[_chainId] = _trustedRemote;
    }

    function setWormholePeer(uint16 _chainId, address _peer) external onlyRole(ADMIN_ROLE) {
        wormholePeers[_chainId] = _peer;
    }

    // Staking functions
    function stake(uint256 amount) external nonReentrant whenNotPaused {
        require(amount > 0, "Amount must be greater than 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");

        UserStake storage userStake = userStakes[msg.sender];
        
        if (userStake.amount > 0) {
            // Add to existing stake
            userStake.amount += uint128(amount);
        } else {
            // New stake
            userStake.amount = uint128(amount);
            userStake.timestamp = uint64(block.timestamp);
        }

        totalStaked += amount;
        _transfer(msg.sender, address(this), amount);

        emit Staked(msg.sender, amount, block.timestamp);
    }

    function unstake(uint256 amount) external nonReentrant whenNotPaused {
        UserStake storage userStake = userStakes[msg.sender];
        require(userStake.amount >= amount, "Insufficient staked amount");

        uint256 penalty = 0;
        if (block.timestamp < userStake.timestamp + MIN_STAKE_DURATION) {
            penalty = (amount * EARLY_UNSTAKE_PENALTY) / 100;
        }

        userStake.amount -= uint128(amount);
        totalStaked -= amount;

        uint256 amountToReturn = amount - penalty;
        
        if (penalty > 0) {
            _burn(address(this), penalty); // Burn penalty tokens
        }

        _transfer(address(this), msg.sender, amountToReturn);

        emit Unstaked(msg.sender, amount, penalty);
    }

    // Cross-chain governance functions
    function createCrossChainProposal(
        string memory description,
        uint256 duration,
        uint16[] memory targetChains
    ) external onlyRole(ORACLE_ROLE) {
        uint256 proposalId = proposalCount++;
        CrossChainProposal storage proposal = proposals[proposalId];
        
        proposal.id = proposalId;
        proposal.description = description;
        proposal.deadline = block.timestamp + duration;
        proposal.executed = false;

        // Send proposal to other chains via Wormhole
        bytes memory payload = abi.encode("CREATE_PROPOSAL", proposalId, description, proposal.deadline);
        
        for (uint i = 0; i < targetChains.length; i++) {
            if (wormholePeers[targetChains[i]] != address(0)) {
                wormholeRelayer.sendPayloadToEvm{value: msg.value / targetChains.length}(
                    targetChains[i],
                    wormholePeers[targetChains[i]],
                    payload,
                    0,
                    200000
                );
            }
        }

        emit ProposalCreated(proposalId, description, proposal.deadline);
    }

    function voteOnProposal(uint256 proposalId, bool support) external {
        CrossChainProposal storage proposal = proposals[proposalId];
        require(block.timestamp <= proposal.deadline, "Voting period ended");
        require(!proposal.hasVoted[msg.sender], "Already voted");
        require(userStakes[msg.sender].amount > 0, "Must have staked tokens to vote");

        proposal.hasVoted[msg.sender] = true;
        
        if (support) {
            proposal.votesFor += userStakes[msg.sender].amount;
        } else {
            proposal.votesAgainst += userStakes[msg.sender].amount;
        }

        emit VoteCast(proposalId, msg.sender, support, 0); // 0 for local chain
    }

    // Wormhole integration
    function receiveWormholeMessages(
        bytes memory payload,
        bytes[] memory,
        bytes32,
        uint16 sourceChain,
        bytes32
    ) external payable override {
        require(msg.sender == address(wormholeRelayer), "Only Wormhole relayer");
        
        (string memory messageType, uint256 proposalId, string memory description, uint256 deadline) = 
            abi.decode(payload, (string, uint256, string, uint256));

        if (keccak256(bytes(messageType)) == keccak256(bytes("CREATE_PROPOSAL"))) {
            // Handle cross-chain proposal creation
            CrossChainProposal storage proposal = proposals[proposalId];
            if (proposal.id == 0) { // New proposal
                proposal.id = proposalId;
                proposal.description = description;
                proposal.deadline = deadline;
                proposal.executed = false;
                
                if (proposalId >= proposalCount) {
                    proposalCount = proposalId + 1;
                }
            }
        }

        emit CrossChainMessageReceived(sourceChain, keccak256(payload));
    }

    // LayerZero integration
    function lzReceive(
        uint16 _srcChainId,
        bytes calldata _srcAddress,
        uint64,
        bytes calldata _payload
    ) external override {
        require(msg.sender == address(layerZeroEndpoint), "Only LayerZero endpoint");
        require(trustedRemotes[_srcChainId] == keccak256(_srcAddress), "Untrusted source");

        (string memory messageType, uint256 proposalId, uint256 votesFor, uint256 votesAgainst) = 
            abi.decode(_payload, (string, uint256, uint256, uint256));

        if (keccak256(bytes(messageType)) == keccak256(bytes("AGGREGATE_VOTES"))) {
            CrossChainProposal storage proposal = proposals[proposalId];
            if (!proposal.chainVoted[_srcChainId]) {
                proposal.votesFor += votesFor;
                proposal.votesAgainst += votesAgainst;
                proposal.chainVoted[_srcChainId] = true;
            }
        }

        emit CrossChainMessageReceived(_srcChainId, keccak256(_payload));
    }

    function sendVotesToChain(
        uint16 targetChainId,
        uint256 proposalId
    ) external payable onlyRole(ORACLE_ROLE) {
        CrossChainProposal storage proposal = proposals[proposalId];
        
        bytes memory payload = abi.encode(
            "AGGREGATE_VOTES",
            proposalId,
            proposal.votesFor,
            proposal.votesAgainst
        );

        layerZeroEndpoint.send{value: msg.value}(
            targetChainId,
            abi.encodePacked(trustedRemotes[targetChainId]),
            payload,
            payable(msg.sender),
            address(0),
            bytes("")
        );

        emit CrossChainMessageSent(targetChainId, keccak256(payload));
    }

    // Admin functions
    function pause() public onlyRole(ADMIN_ROLE) {
        _pause();
    }

    function unpause() public onlyRole(ADMIN_ROLE) {
        _unpause();
    }

    function _authorizeUpgrade(address newImplementation) internal onlyRole(ADMIN_ROLE) override {}

    // Required overrides
    function _update(address from, address to, uint256 value)
        internal
        override(ERC20Upgradeable, ERC20PausableUpgradeable)
    {
        super._update(from, to, value);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(AccessControlUpgradeable)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}


// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// LayerZero OFT imports (conceptual - actual imports would depend on LayerZero SDK)
interface ILayerZeroEndpoint {
    function send(
        uint16 _dstChainId,
        bytes calldata _destination,
        bytes calldata _payload,
        address payable _refundAddress,
        address _zroPaymentAddress,
        bytes calldata _adapterParams
    ) external payable;

    function receivePayload(
        uint16 _srcChainId,
        bytes calldata _srcAddress,
        address _dstAddress,
        uint64 _nonce,
        uint _gasLimit,
        bytes calldata _payload
    ) external;
}

interface ILayerZeroReceiver {
    function lzReceive(
        uint16 _srcChainId,
        bytes calldata _srcAddress,
        uint64 _nonce,
        bytes calldata _payload
    ) external;
}

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title XMRTLayerZeroOFT
 * @dev Omnichain Fungible Token implementation for XMRT using LayerZero
 */
contract XMRTLayerZeroOFT is ERC20, Ownable, ReentrancyGuard, ILayerZeroReceiver {
    ILayerZeroEndpoint public immutable lzEndpoint;
    
    // LayerZero configuration
    mapping(uint16 => bytes) public trustedRemoteLookup;
    mapping(uint16 => mapping(bytes => mapping(uint64 => bool))) public creditedPackets;
    
    // OFT configuration
    uint8 public immutable sharedDecimals;
    mapping(uint16 => uint256) public chainIdToFeeBps; // Fee in basis points (1/10000)
    
    // Events
    event SendToChain(uint16 indexed _dstChainId, address indexed _from, bytes indexed _toAddress, uint _amount);
    event ReceiveFromChain(uint16 indexed _srcChainId, address indexed _to, uint _amount);
    event SetTrustedRemote(uint16 _remoteChainId, bytes _path);
    event SetFeeBps(uint16 _dstChainId, uint256 _feeBps);

    constructor(
        string memory _name,
        string memory _symbol,
        uint8 _sharedDecimals,
        address _lzEndpoint
    ) ERC20(_name, _symbol) Ownable(msg.sender) {
        require(_lzEndpoint != address(0), "LayerZero endpoint cannot be zero address");
        lzEndpoint = ILayerZeroEndpoint(_lzEndpoint);
        sharedDecimals = _sharedDecimals;
    }

    // LayerZero configuration functions
    function setTrustedRemote(uint16 _remoteChainId, bytes calldata _path) external onlyOwner {
        trustedRemoteLookup[_remoteChainId] = _path;
        emit SetTrustedRemote(_remoteChainId, _path);
    }

    function setFeeBps(uint16 _dstChainId, uint256 _feeBps) external onlyOwner {
        require(_feeBps <= 10000, "Fee cannot exceed 100%");
        chainIdToFeeBps[_dstChainId] = _feeBps;
        emit SetFeeBps(_dstChainId, _feeBps);
    }

    function isTrustedRemote(uint16 _srcChainId, bytes calldata _srcAddress) public view returns (bool) {
        bytes memory trustedSource = trustedRemoteLookup[_srcChainId];
        return keccak256(trustedSource) == keccak256(_srcAddress);
    }

    // OFT Core functions
    function sendFrom(
        address _from,
        uint16 _dstChainId,
        bytes calldata _toAddress,
        uint _amount,
        address payable _refundAddress,
        address _zroPaymentAddress,
        bytes calldata _adapterParams
    ) public payable virtual {
        _send(_from, _dstChainId, _toAddress, _amount, _refundAddress, _zroPaymentAddress, _adapterParams);
    }

    function send(
        uint16 _dstChainId,
        bytes calldata _toAddress,
        uint _amount,
        address payable _refundAddress,
        address _zroPaymentAddress,
        bytes calldata _adapterParams
    ) public payable virtual {
        _send(msg.sender, _dstChainId, _toAddress, _amount, _refundAddress, _zroPaymentAddress, _adapterParams);
    }

    function _send(
        address _from,
        uint16 _dstChainId,
        bytes memory _toAddress,
        uint _amount,
        address payable _refundAddress,
        address _zroPaymentAddress,
        bytes memory _adapterParams
    ) internal virtual {
        require(_amount > 0, "Amount must be greater than zero");
        require(_toAddress.length > 0, "Invalid destination address");

        uint256 fee = (_amount * chainIdToFeeBps[_dstChainId]) / 10000;
        uint256 amountToSend = _amount - fee;

        // Burn tokens on source chain
        _burn(_from, _amount);

        // Send cross-chain message
        bytes memory payload = abi.encode(PT_SEND, _toAddress, amountToSend);
        
        lzEndpoint.send{value: msg.value}(
            _dstChainId,
            trustedRemoteLookup[_dstChainId],
            payload,
            _refundAddress,
            _zroPaymentAddress,
            _adapterParams
        );

        emit SendToChain(_dstChainId, _from, _toAddress, amountToSend);
    }

    // LayerZero receive function
    function lzReceive(
        uint16 _srcChainId,
        bytes calldata _srcAddress,
        uint64 _nonce,
        bytes calldata _payload
    ) public virtual override {
        require(msg.sender == address(lzEndpoint), "Only LayerZero endpoint");
        require(isTrustedRemote(_srcChainId, _srcAddress), "Untrusted remote");

        if (!creditedPackets[_srcChainId][_srcAddress][_nonce]) {
            creditedPackets[_srcChainId][_srcAddress][_nonce] = true;
            _nonblockingLzReceive(_srcChainId, _srcAddress, _nonce, _payload);
        }
    }

    function _nonblockingLzReceive(
        uint16 _srcChainId,
        bytes memory _srcAddress,
        uint64 _nonce,
        bytes memory _payload
    ) internal virtual {
        uint16 packetType;
        assembly {
            packetType := mload(add(_payload, 32))
        }

        if (packetType == PT_SEND) {
            _sendAck(_srcChainId, _srcAddress, _nonce, _payload);
        } else {
            revert("Unknown packet type");
        }
    }

    function _sendAck(
        uint16 _srcChainId,
        bytes memory,
        uint64,
        bytes memory _payload
    ) internal virtual {
        (, bytes memory toAddressBytes, uint256 amount) = abi.decode(_payload, (uint16, bytes, uint256));
        
        address to;
        assembly {
            to := mload(add(toAddressBytes, 20))
        }

        // Mint tokens on destination chain
        _mint(to, amount);

        emit ReceiveFromChain(_srcChainId, to, amount);
    }

    // Estimate fees for cross-chain transfer
    function estimateSendFee(
        uint16 _dstChainId,
        bytes calldata _toAddress,
        uint _amount,
        bool _useZro,
        bytes calldata _adapterParams
    ) public view virtual returns (uint nativeFee, uint zroFee) {
        bytes memory payload = abi.encode(PT_SEND, _toAddress, _amount);
        return lzEndpoint.estimateFees(_dstChainId, address(this), payload, _useZro, _adapterParams);
    }

    // Constants for packet types
    uint16 public constant PT_SEND = 0;

    // Admin functions for minting (only for initial distribution)
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }

    // Emergency functions
    function forceResumeReceive(uint16 _srcChainId, bytes calldata _srcAddress) external onlyOwner {
        lzEndpoint.forceResumeReceive(_srcChainId, _srcAddress);
    }

    // View functions
    function circulatingSupply() public view virtual returns (uint) {
        return totalSupply();
    }

    function token() public view virtual returns (address) {
        return address(this);
    }
}


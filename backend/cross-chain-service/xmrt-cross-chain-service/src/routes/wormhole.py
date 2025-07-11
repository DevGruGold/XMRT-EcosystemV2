from flask import Blueprint, request, jsonify
import os
import requests
from web3 import Web3
import json
from typing import Dict, Any, Optional

wormhole_bp = Blueprint('wormhole', __name__)

class WormholeService:
    def __init__(self):
        self.rpc_urls = {
            'ethereum': os.getenv('ETHEREUM_RPC_URL', 'https://rpc.ankr.com/eth'),
            'sepolia': os.getenv('SEPOLIA_RPC_URL', 'https://rpc.ankr.com/eth_sepolia'),
            'polygon': os.getenv('POLYGON_RPC_URL', 'https://rpc.ankr.com/polygon'),
            'bsc': os.getenv('BSC_RPC_URL', 'https://rpc.ankr.com/bsc'),
            'avalanche': os.getenv('AVALANCHE_RPC_URL', 'https://rpc.ankr.com/avalanche'),
        }
        
        # Wormhole Core Contract addresses (mainnet/testnet)
        self.core_contracts = {
            'ethereum': '0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B',
            'sepolia': '0x4a8bc80Ed5a4067f1CCf107057b8270E0cC11A78',
            'polygon': '0x7A4B5a56256163F07b2C80A7cA55aBE66c4ec4d7',
            'bsc': '0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B',
            'avalanche': '0x54a8e5f9c4CbA08F9943965859F6c34eAF03E26c',
        }
        
        # Wormhole Chain IDs
        self.chain_ids = {
            'ethereum': 2,
            'sepolia': 10002,
            'polygon': 5,
            'bsc': 4,
            'avalanche': 6,
        }
        
        self.web3_instances = {}
        self._initialize_web3_connections()
    
    def _initialize_web3_connections(self):
        """Initialize Web3 connections for supported chains"""
        for chain, rpc_url in self.rpc_urls.items():
            try:
                self.web3_instances[chain] = Web3(Web3.HTTPProvider(rpc_url))
                if self.web3_instances[chain].is_connected():
                    print(f"✅ Connected to {chain}")
                else:
                    print(f"❌ Failed to connect to {chain}")
            except Exception as e:
                print(f"❌ Error connecting to {chain}: {e}")
    
    def get_chain_info(self, chain_name: str) -> Dict[str, Any]:
        """Get chain information"""
        if chain_name not in self.web3_instances:
            return None
        
        web3 = self.web3_instances[chain_name]
        try:
            latest_block = web3.eth.get_block('latest')
            return {
                'chain_name': chain_name,
                'chain_id': web3.eth.chain_id,
                'wormhole_chain_id': self.chain_ids.get(chain_name),
                'latest_block': latest_block.number,
                'core_contract': self.core_contracts.get(chain_name),
                'connected': True
            }
        except Exception as e:
            return {
                'chain_name': chain_name,
                'connected': False,
                'error': str(e)
            }
    
    def estimate_bridge_fee(self, source_chain: str, target_chain: str, amount: int) -> Dict[str, Any]:
        """Estimate fees for cross-chain bridge transaction"""
        try:
            # This is a simplified fee estimation
            # In production, this would query actual Wormhole fee structures
            base_fee = 0.001  # ETH equivalent
            
            # Fee varies by target chain
            chain_multipliers = {
                'ethereum': 1.5,
                'polygon': 0.1,
                'bsc': 0.1,
                'avalanche': 0.2,
                'sepolia': 0.05
            }
            
            multiplier = chain_multipliers.get(target_chain, 1.0)
            estimated_fee = base_fee * multiplier
            
            return {
                'source_chain': source_chain,
                'target_chain': target_chain,
                'amount': amount,
                'estimated_fee_eth': estimated_fee,
                'estimated_fee_wei': int(estimated_fee * 10**18),
                'success': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_vaa_status(self, tx_hash: str, source_chain: str) -> Dict[str, Any]:
        """Get VAA (Verified Action Approval) status for a transaction"""
        try:
            # In production, this would query Wormhole's Guardian network
            # For now, we'll simulate the response
            return {
                'tx_hash': tx_hash,
                'source_chain': source_chain,
                'vaa_status': 'pending',  # pending, confirmed, failed
                'vaa_bytes': None,
                'guardian_signatures': 0,
                'required_signatures': 13,
                'estimated_confirmation_time': '5-15 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def submit_vaa(self, vaa_bytes: str, target_chain: str) -> Dict[str, Any]:
        """Submit VAA to target chain for execution"""
        try:
            # In production, this would submit the VAA to the target chain's core contract
            return {
                'vaa_bytes': vaa_bytes,
                'target_chain': target_chain,
                'submission_status': 'submitted',
                'tx_hash': '0x' + '0' * 64,  # Placeholder
                'success': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Initialize service
wormhole_service = WormholeService()

@wormhole_bp.route('/chains', methods=['GET'])
def get_supported_chains():
    """Get list of supported chains and their status"""
    chains_info = []
    for chain in wormhole_service.rpc_urls.keys():
        chain_info = wormhole_service.get_chain_info(chain)
        chains_info.append(chain_info)
    
    return jsonify({
        'supported_chains': chains_info,
        'total_chains': len(chains_info),
        'connected_chains': len([c for c in chains_info if c.get('connected', False)])
    })

@wormhole_bp.route('/chain/<chain_name>', methods=['GET'])
def get_chain_details(chain_name):
    """Get detailed information about a specific chain"""
    chain_info = wormhole_service.get_chain_info(chain_name)
    if not chain_info:
        return jsonify({'error': 'Chain not supported'}), 404
    
    return jsonify(chain_info)

@wormhole_bp.route('/estimate-fee', methods=['POST'])
def estimate_bridge_fee():
    """Estimate fees for cross-chain bridge transaction"""
    data = request.get_json()
    
    required_fields = ['source_chain', 'target_chain', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    result = wormhole_service.estimate_bridge_fee(
        data['source_chain'],
        data['target_chain'],
        data['amount']
    )
    
    return jsonify(result)

@wormhole_bp.route('/vaa-status/<tx_hash>', methods=['GET'])
def get_vaa_status(tx_hash):
    """Get VAA status for a transaction"""
    source_chain = request.args.get('source_chain', 'sepolia')
    result = wormhole_service.get_vaa_status(tx_hash, source_chain)
    return jsonify(result)

@wormhole_bp.route('/submit-vaa', methods=['POST'])
def submit_vaa():
    """Submit VAA to target chain"""
    data = request.get_json()
    
    if 'vaa_bytes' not in data or 'target_chain' not in data:
        return jsonify({'error': 'Missing vaa_bytes or target_chain'}), 400
    
    result = wormhole_service.submit_vaa(data['vaa_bytes'], data['target_chain'])
    return jsonify(result)

@wormhole_bp.route('/bridge-tokens', methods=['POST'])
def bridge_tokens():
    """Initiate cross-chain token bridge transaction"""
    data = request.get_json()
    
    required_fields = ['source_chain', 'target_chain', 'amount', 'recipient_address']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # In production, this would:
        # 1. Validate the transaction
        # 2. Lock tokens on source chain
        # 3. Emit Wormhole message
        # 4. Return transaction hash
        
        result = {
            'source_chain': data['source_chain'],
            'target_chain': data['target_chain'],
            'amount': data['amount'],
            'recipient': data['recipient_address'],
            'tx_hash': '0x' + '1' * 64,  # Placeholder
            'status': 'initiated',
            'estimated_completion': '5-15 minutes',
            'success': True
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@wormhole_bp.route('/governance/send-message', methods=['POST'])
def send_governance_message():
    """Send governance message across chains"""
    data = request.get_json()
    
    required_fields = ['proposal_id', 'message_type', 'target_chains', 'payload']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        results = []
        for target_chain in data['target_chains']:
            # In production, this would send actual governance messages
            result = {
                'target_chain': target_chain,
                'proposal_id': data['proposal_id'],
                'message_type': data['message_type'],
                'tx_hash': '0x' + '2' * 64,  # Placeholder
                'status': 'sent',
                'success': True
            }
            results.append(result)
        
        return jsonify({
            'governance_messages': results,
            'total_sent': len(results),
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@wormhole_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    connected_chains = 0
    total_chains = len(wormhole_service.rpc_urls)
    
    for chain in wormhole_service.rpc_urls.keys():
        if chain in wormhole_service.web3_instances:
            try:
                if wormhole_service.web3_instances[chain].is_connected():
                    connected_chains += 1
            except:
                pass
    
    return jsonify({
        'service': 'wormhole',
        'status': 'healthy' if connected_chains > 0 else 'degraded',
        'connected_chains': connected_chains,
        'total_chains': total_chains,
        'uptime_percentage': (connected_chains / total_chains) * 100 if total_chains > 0 else 0
    })


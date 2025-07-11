from flask import Blueprint, request, jsonify
import os
import requests
from web3 import Web3
import json
from typing import Dict, Any, Optional, List

layerzero_bp = Blueprint('layerzero', __name__)

class LayerZeroService:
    def __init__(self):
        self.rpc_urls = {
            'ethereum': os.getenv('ETHEREUM_RPC_URL', 'https://rpc.ankr.com/eth'),
            'sepolia': os.getenv('SEPOLIA_RPC_URL', 'https://rpc.ankr.com/eth_sepolia'),
            'polygon': os.getenv('POLYGON_RPC_URL', 'https://rpc.ankr.com/polygon'),
            'bsc': os.getenv('BSC_RPC_URL', 'https://rpc.ankr.com/bsc'),
            'avalanche': os.getenv('AVALANCHE_RPC_URL', 'https://rpc.ankr.com/avalanche'),
            'arbitrum': os.getenv('ARBITRUM_RPC_URL', 'https://rpc.ankr.com/arbitrum'),
            'optimism': os.getenv('OPTIMISM_RPC_URL', 'https://rpc.ankr.com/optimism'),
        }
        
        # LayerZero Endpoint addresses (V2)
        self.endpoint_addresses = {
            'ethereum': '0x1a44076050125825900e736c501f859c50fE728c',
            'sepolia': '0x6EDCE65403992e310A62460808c4b910D972f10f',
            'polygon': '0x1a44076050125825900e736c501f859c50fE728c',
            'bsc': '0x1a44076050125825900e736c501f859c50fE728c',
            'avalanche': '0x1a44076050125825900e736c501f859c50fE728c',
            'arbitrum': '0x1a44076050125825900e736c501f859c50fE728c',
            'optimism': '0x1a44076050125825900e736c501f859c50fE728c',
        }
        
        # LayerZero Chain IDs (Endpoint IDs)
        self.endpoint_ids = {
            'ethereum': 30101,
            'sepolia': 40161,
            'polygon': 30109,
            'bsc': 30102,
            'avalanche': 30106,
            'arbitrum': 30110,
            'optimism': 30111,
        }
        
        self.web3_instances = {}
        self._initialize_web3_connections()
    
    def _initialize_web3_connections(self):
        """Initialize Web3 connections for supported chains"""
        for chain, rpc_url in self.rpc_urls.items():
            try:
                self.web3_instances[chain] = Web3(Web3.HTTPProvider(rpc_url))
                if self.web3_instances[chain].is_connected():
                    print(f"✅ LayerZero connected to {chain}")
                else:
                    print(f"❌ LayerZero failed to connect to {chain}")
            except Exception as e:
                print(f"❌ LayerZero error connecting to {chain}: {e}")
    
    def get_endpoint_info(self, chain_name: str) -> Dict[str, Any]:
        """Get LayerZero endpoint information for a chain"""
        if chain_name not in self.web3_instances:
            return None
        
        web3 = self.web3_instances[chain_name]
        try:
            latest_block = web3.eth.get_block('latest')
            return {
                'chain_name': chain_name,
                'chain_id': web3.eth.chain_id,
                'endpoint_id': self.endpoint_ids.get(chain_name),
                'endpoint_address': self.endpoint_addresses.get(chain_name),
                'latest_block': latest_block.number,
                'connected': True,
                'gas_price': web3.eth.gas_price
            }
        except Exception as e:
            return {
                'chain_name': chain_name,
                'connected': False,
                'error': str(e)
            }
    
    def estimate_omnichain_fee(self, source_chain: str, target_chain: str, payload_size: int) -> Dict[str, Any]:
        """Estimate fees for omnichain message"""
        try:
            # Base fee calculation (simplified)
            base_fee = 0.0005  # ETH equivalent
            
            # Fee varies by target chain and payload size
            chain_multipliers = {
                'ethereum': 2.0,
                'polygon': 0.05,
                'bsc': 0.05,
                'avalanche': 0.1,
                'arbitrum': 0.3,
                'optimism': 0.3,
                'sepolia': 0.01
            }
            
            payload_multiplier = 1 + (payload_size / 1000)  # Increase fee based on payload size
            chain_multiplier = chain_multipliers.get(target_chain, 1.0)
            
            estimated_fee = base_fee * chain_multiplier * payload_multiplier
            
            return {
                'source_chain': source_chain,
                'target_chain': target_chain,
                'payload_size_bytes': payload_size,
                'estimated_fee_eth': estimated_fee,
                'estimated_fee_wei': int(estimated_fee * 10**18),
                'gas_limit': 200000 + (payload_size * 100),  # Estimated gas
                'success': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_message_status(self, tx_hash: str, source_chain: str) -> Dict[str, Any]:
        """Get status of omnichain message"""
        try:
            # In production, this would query LayerZero's message status
            return {
                'tx_hash': tx_hash,
                'source_chain': source_chain,
                'message_status': 'delivered',  # pending, delivered, failed
                'delivery_attempts': 1,
                'gas_used': 150000,
                'delivery_time': '30-60 seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_oft_config(self, token_address: str, chain_name: str) -> Dict[str, Any]:
        """Get OFT (Omnichain Fungible Token) configuration"""
        try:
            # In production, this would query the actual OFT contract
            return {
                'token_address': token_address,
                'chain_name': chain_name,
                'name': 'XMRT Token',
                'symbol': 'XMRT',
                'decimals': 18,
                'total_supply': '21000000000000000000000000',  # 21M tokens
                'oft_version': 'V2',
                'trusted_remotes': self._get_trusted_remotes(chain_name),
                'success': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_trusted_remotes(self, chain_name: str) -> List[Dict[str, Any]]:
        """Get trusted remote configurations for OFT"""
        trusted_remotes = []
        for chain, endpoint_id in self.endpoint_ids.items():
            if chain != chain_name:
                trusted_remotes.append({
                    'chain_name': chain,
                    'endpoint_id': endpoint_id,
                    'trusted': True,
                    'remote_address': '0x' + '0' * 40  # Placeholder
                })
        return trusted_remotes

# Initialize service
layerzero_service = LayerZeroService()

@layerzero_bp.route('/endpoints', methods=['GET'])
def get_supported_endpoints():
    """Get list of supported LayerZero endpoints"""
    endpoints_info = []
    for chain in layerzero_service.rpc_urls.keys():
        endpoint_info = layerzero_service.get_endpoint_info(chain)
        endpoints_info.append(endpoint_info)
    
    return jsonify({
        'supported_endpoints': endpoints_info,
        'total_endpoints': len(endpoints_info),
        'connected_endpoints': len([e for e in endpoints_info if e.get('connected', False)])
    })

@layerzero_bp.route('/endpoint/<chain_name>', methods=['GET'])
def get_endpoint_details(chain_name):
    """Get detailed information about a specific endpoint"""
    endpoint_info = layerzero_service.get_endpoint_info(chain_name)
    if not endpoint_info:
        return jsonify({'error': 'Endpoint not supported'}), 404
    
    return jsonify(endpoint_info)

@layerzero_bp.route('/estimate-fee', methods=['POST'])
def estimate_omnichain_fee():
    """Estimate fees for omnichain message"""
    data = request.get_json()
    
    required_fields = ['source_chain', 'target_chain']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    payload_size = data.get('payload_size', 100)  # Default 100 bytes
    
    result = layerzero_service.estimate_omnichain_fee(
        data['source_chain'],
        data['target_chain'],
        payload_size
    )
    
    return jsonify(result)

@layerzero_bp.route('/message-status/<tx_hash>', methods=['GET'])
def get_message_status(tx_hash):
    """Get omnichain message status"""
    source_chain = request.args.get('source_chain', 'sepolia')
    result = layerzero_service.get_message_status(tx_hash, source_chain)
    return jsonify(result)

@layerzero_bp.route('/send-message', methods=['POST'])
def send_omnichain_message():
    """Send omnichain message"""
    data = request.get_json()
    
    required_fields = ['source_chain', 'target_chain', 'payload', 'recipient']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # In production, this would:
        # 1. Validate the message
        # 2. Call LayerZero endpoint
        # 3. Return transaction hash
        
        result = {
            'source_chain': data['source_chain'],
            'target_chain': data['target_chain'],
            'recipient': data['recipient'],
            'payload_hash': '0x' + 'a' * 64,  # Placeholder
            'tx_hash': '0x' + 'b' * 64,  # Placeholder
            'status': 'sent',
            'estimated_delivery': '30-60 seconds',
            'success': True
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@layerzero_bp.route('/oft/transfer', methods=['POST'])
def transfer_oft():
    """Transfer OFT tokens across chains"""
    data = request.get_json()
    
    required_fields = ['source_chain', 'target_chain', 'amount', 'recipient']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # In production, this would call the OFT contract
        result = {
            'source_chain': data['source_chain'],
            'target_chain': data['target_chain'],
            'amount': data['amount'],
            'recipient': data['recipient'],
            'tx_hash': '0x' + 'c' * 64,  # Placeholder
            'status': 'initiated',
            'estimated_delivery': '30-60 seconds',
            'success': True
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@layerzero_bp.route('/oft/config/<token_address>', methods=['GET'])
def get_oft_config(token_address):
    """Get OFT configuration"""
    chain_name = request.args.get('chain', 'sepolia')
    result = layerzero_service.get_oft_config(token_address, chain_name)
    return jsonify(result)

@layerzero_bp.route('/governance/proposal', methods=['POST'])
def send_governance_proposal():
    """Send governance proposal across chains"""
    data = request.get_json()
    
    required_fields = ['proposal_id', 'title', 'description', 'target_chains']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        results = []
        for target_chain in data['target_chains']:
            # In production, this would send actual governance proposals
            result = {
                'target_chain': target_chain,
                'proposal_id': data['proposal_id'],
                'title': data['title'],
                'tx_hash': '0x' + 'd' * 64,  # Placeholder
                'status': 'sent',
                'success': True
            }
            results.append(result)
        
        return jsonify({
            'governance_proposals': results,
            'total_sent': len(results),
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@layerzero_bp.route('/governance/vote', methods=['POST'])
def aggregate_votes():
    """Aggregate votes from multiple chains"""
    data = request.get_json()
    
    required_fields = ['proposal_id', 'votes_data']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        total_votes_for = 0
        total_votes_against = 0
        chain_results = []
        
        for vote_data in data['votes_data']:
            total_votes_for += vote_data.get('votes_for', 0)
            total_votes_against += vote_data.get('votes_against', 0)
            chain_results.append({
                'chain': vote_data.get('chain'),
                'votes_for': vote_data.get('votes_for', 0),
                'votes_against': vote_data.get('votes_against', 0),
                'processed': True
            })
        
        result = {
            'proposal_id': data['proposal_id'],
            'total_votes_for': total_votes_for,
            'total_votes_against': total_votes_against,
            'chain_results': chain_results,
            'outcome': 'approved' if total_votes_for > total_votes_against else 'rejected',
            'success': True
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@layerzero_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    connected_endpoints = 0
    total_endpoints = len(layerzero_service.rpc_urls)
    
    for chain in layerzero_service.rpc_urls.keys():
        if chain in layerzero_service.web3_instances:
            try:
                if layerzero_service.web3_instances[chain].is_connected():
                    connected_endpoints += 1
            except:
                pass
    
    return jsonify({
        'service': 'layerzero',
        'status': 'healthy' if connected_endpoints > 0 else 'degraded',
        'connected_endpoints': connected_endpoints,
        'total_endpoints': total_endpoints,
        'uptime_percentage': (connected_endpoints / total_endpoints) * 100 if total_endpoints > 0 else 0
    })


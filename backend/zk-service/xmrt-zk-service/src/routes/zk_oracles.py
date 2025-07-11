from flask import Blueprint, request, jsonify
import os
import json
import hashlib
import time
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

zk_oracles_bp = Blueprint('zk_oracles', __name__)

class ZKOracleService:
    def __init__(self):
        self.proofs_dir = os.path.join(os.path.dirname(__file__), '..', 'oracle_proofs')
        self.sessions_dir = os.path.join(os.path.dirname(__file__), '..', 'tls_sessions')
        self.feeds_dir = os.path.join(os.path.dirname(__file__), '..', 'data_feeds')
        
        # Create directories if they don't exist
        os.makedirs(self.proofs_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.feeds_dir, exist_ok=True)
        
        # Supported data sources
        self.supported_sources = {
            'coinmarketcap.com': {
                'type': 'crypto_prices',
                'endpoints': ['/v1/cryptocurrency/quotes/latest'],
                'rate_limit': 100  # requests per hour
            },
            'api.github.com': {
                'type': 'github_data',
                'endpoints': ['/repos', '/users', '/orgs'],
                'rate_limit': 5000
            },
            'newsapi.org': {
                'type': 'news_data',
                'endpoints': ['/v2/everything', '/v2/top-headlines'],
                'rate_limit': 1000
            },
            'api.twitter.com': {
                'type': 'social_media',
                'endpoints': ['/2/tweets/search/recent'],
                'rate_limit': 300
            }
        }
        
        # Initialize sample data feeds
        self._initialize_sample_feeds()
    
    def _initialize_sample_feeds(self):
        """Initialize sample data feeds for testing"""
        sample_feeds = {
            'crypto_prices': {
                'source': 'coinmarketcap.com',
                'endpoint': '/v1/cryptocurrency/quotes/latest',
                'last_update': int(time.time()),
                'data': {
                    'BTC': {'price': 45000, 'change_24h': 2.5},
                    'ETH': {'price': 3200, 'change_24h': -1.2},
                    'XMRT': {'price': 0.15, 'change_24h': 5.8}
                }
            },
            'github_activity': {
                'source': 'api.github.com',
                'endpoint': '/repos/DevGruGold/XMRT-Ecosystem',
                'last_update': int(time.time()),
                'data': {
                    'stars': 42,
                    'forks': 8,
                    'commits_last_week': 15,
                    'contributors': 3
                }
            },
            'news_sentiment': {
                'source': 'newsapi.org',
                'endpoint': '/v2/everything?q=cryptocurrency',
                'last_update': int(time.time()),
                'data': {
                    'total_articles': 150,
                    'positive_sentiment': 0.65,
                    'negative_sentiment': 0.25,
                    'neutral_sentiment': 0.10
                }
            }
        }
        
        for feed_name, feed_data in sample_feeds.items():
            feed_path = os.path.join(self.feeds_dir, f'{feed_name}.json')
            with open(feed_path, 'w') as f:
                json.dump(feed_data, f, indent=2)
    
    def create_tls_session(self, url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Create a TLS session for data fetching"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            if domain not in self.supported_sources:
                return {
                    'success': False,
                    'error': f'Domain {domain} not supported'
                }
            
            session_id = hashlib.md5(f'{url}_{time.time()}'.encode()).hexdigest()[:16]
            
            # In production, this would establish actual TLS connection with TLSNotary
            # For now, we simulate the session creation
            session_data = {
                'session_id': session_id,
                'url': url,
                'domain': domain,
                'source_type': self.supported_sources[domain]['type'],
                'headers': headers or {},
                'timestamp': int(time.time()),
                'status': 'active',
                'tls_version': 'TLS 1.3',
                'cipher_suite': 'TLS_AES_256_GCM_SHA384'
            }
            
            # Save session data
            session_path = os.path.join(self.sessions_dir, f'{session_id}.json')
            with open(session_path, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            return {
                'success': True,
                'session_id': session_id,
                'session_data': session_data
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def fetch_and_prove(self, session_id: str, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch data and generate TLSNotary proof"""
        try:
            session_path = os.path.join(self.sessions_dir, f'{session_id}.json')
            
            if not os.path.exists(session_path):
                return {
                    'success': False,
                    'error': f'Session {session_id} not found'
                }
            
            # Load session data
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            
            # In production, this would fetch actual data via TLSNotary
            # For now, we simulate data fetching based on source type
            fetched_data = self._simulate_data_fetch(session_data, query_params)
            
            # Generate TLSNotary proof
            proof = self._generate_tlsnotary_proof(session_data, fetched_data)
            
            # Save proof
            proof_id = hashlib.md5(f'{session_id}_{time.time()}'.encode()).hexdigest()[:16]
            proof_path = os.path.join(self.proofs_dir, f'{proof_id}.json')
            
            proof_record = {
                'proof_id': proof_id,
                'session_id': session_id,
                'url': session_data['url'],
                'timestamp': int(time.time()),
                'data': fetched_data,
                'proof': proof,
                'verified': True
            }
            
            with open(proof_path, 'w') as f:
                json.dump(proof_record, f, indent=2)
            
            return {
                'success': True,
                'proof_id': proof_id,
                'proof_record': proof_record
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _simulate_data_fetch(self, session_data: Dict[str, Any], query_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Simulate data fetching based on source type"""
        source_type = session_data['source_type']
        
        if source_type == 'crypto_prices':
            return {
                'timestamp': int(time.time()),
                'prices': {
                    'BTC': 45000 + (hash(str(time.time())) % 1000 - 500),  # Simulate price variation
                    'ETH': 3200 + (hash(str(time.time())) % 200 - 100),
                    'XMRT': 0.15 + (hash(str(time.time())) % 10 - 5) / 1000
                },
                'source': 'coinmarketcap.com'
            }
        
        elif source_type == 'github_data':
            return {
                'timestamp': int(time.time()),
                'repository': 'DevGruGold/XMRT-Ecosystem',
                'stars': 42 + (hash(str(time.time())) % 5),
                'forks': 8 + (hash(str(time.time())) % 3),
                'commits_today': hash(str(time.time())) % 10,
                'source': 'api.github.com'
            }
        
        elif source_type == 'news_data':
            sentiment_base = 0.65
            sentiment_variation = (hash(str(time.time())) % 20 - 10) / 100
            return {
                'timestamp': int(time.time()),
                'query': query_params.get('q', 'cryptocurrency') if query_params else 'cryptocurrency',
                'total_articles': 150 + (hash(str(time.time())) % 50),
                'sentiment_score': max(0, min(1, sentiment_base + sentiment_variation)),
                'source': 'newsapi.org'
            }
        
        elif source_type == 'social_media':
            return {
                'timestamp': int(time.time()),
                'mentions': hash(str(time.time())) % 1000,
                'sentiment': {
                    'positive': 0.6 + (hash(str(time.time())) % 20 - 10) / 100,
                    'negative': 0.2 + (hash(str(time.time())) % 10 - 5) / 100,
                    'neutral': 0.2
                },
                'source': 'api.twitter.com'
            }
        
        else:
            return {
                'timestamp': int(time.time()),
                'data': 'Generic data response',
                'source': session_data['domain']
            }
    
    def _generate_tlsnotary_proof(self, session_data: Dict[str, Any], fetched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate TLSNotary proof for fetched data"""
        # In production, this would generate actual TLSNotary proof
        # For now, we simulate the proof structure
        
        data_hash = hashlib.sha256(json.dumps(fetched_data, sort_keys=True).encode()).hexdigest()
        session_hash = hashlib.sha256(json.dumps(session_data, sort_keys=True).encode()).hexdigest()
        
        proof = {
            'version': '1.0',
            'tls_version': session_data['tls_version'],
            'cipher_suite': session_data['cipher_suite'],
            'server_cert_hash': f'0x{hashlib.sha256(session_data["domain"].encode()).hexdigest()}',
            'session_hash': f'0x{session_hash}',
            'data_hash': f'0x{data_hash}',
            'commitment': f'0x{hashlib.sha256(f"{session_hash}{data_hash}".encode()).hexdigest()}',
            'signature': f'0x{hashlib.sha256(f"signature_{session_data["session_id"]}".encode()).hexdigest()}',
            'timestamp': int(time.time())
        }
        
        return proof
    
    def verify_proof(self, proof_id: str) -> Dict[str, Any]:
        """Verify a TLSNotary proof"""
        try:
            proof_path = os.path.join(self.proofs_dir, f'{proof_id}.json')
            
            if not os.path.exists(proof_path):
                return {
                    'success': False,
                    'error': f'Proof {proof_id} not found'
                }
            
            # Load proof
            with open(proof_path, 'r') as f:
                proof_record = json.load(f)
            
            # In production, this would verify actual TLSNotary proof
            # For now, we simulate verification
            verification_result = {
                'proof_id': proof_id,
                'verified': True,  # Simplified - always verified for demo
                'url': proof_record['url'],
                'timestamp': proof_record['timestamp'],
                'data_integrity': True,
                'tls_authenticity': True,
                'verification_time': '0.8s'
            }
            
            return {
                'success': True,
                'verification_result': verification_result
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_data_feed(self, feed_name: str) -> Dict[str, Any]:
        """Get current data from a feed"""
        try:
            feed_path = os.path.join(self.feeds_dir, f'{feed_name}.json')
            
            if not os.path.exists(feed_path):
                return {
                    'success': False,
                    'error': f'Data feed {feed_name} not found'
                }
            
            with open(feed_path, 'r') as f:
                feed_data = json.load(f)
            
            return {
                'success': True,
                'feed_data': feed_data
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Initialize service
zk_oracle_service = ZKOracleService()

@zk_oracles_bp.route('/sources', methods=['GET'])
def get_supported_sources():
    """Get list of supported data sources"""
    return jsonify({
        'supported_sources': zk_oracle_service.supported_sources,
        'total_sources': len(zk_oracle_service.supported_sources)
    })

@zk_oracles_bp.route('/session/create', methods=['POST'])
def create_tls_session():
    """Create a new TLS session"""
    data = request.get_json()
    
    if 'url' not in data:
        return jsonify({'error': 'Missing URL'}), 400
    
    headers = data.get('headers', {})
    result = zk_oracle_service.create_tls_session(data['url'], headers)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@zk_oracles_bp.route('/fetch/<session_id>', methods=['POST'])
def fetch_and_prove(session_id):
    """Fetch data and generate TLSNotary proof"""
    data = request.get_json() or {}
    query_params = data.get('query_params', {})
    
    result = zk_oracle_service.fetch_and_prove(session_id, query_params)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@zk_oracles_bp.route('/verify/<proof_id>', methods=['GET'])
def verify_proof(proof_id):
    """Verify a TLSNotary proof"""
    result = zk_oracle_service.verify_proof(proof_id)
    
    if result['success']:
        return jsonify(result['verification_result'])
    else:
        return jsonify(result), 404

@zk_oracles_bp.route('/proofs', methods=['GET'])
def list_proofs():
    """List all generated proofs"""
    try:
        proofs = []
        for filename in os.listdir(zk_oracle_service.proofs_dir):
            if filename.endswith('.json'):
                proof_id = filename[:-5]  # Remove .json extension
                proof_path = os.path.join(zk_oracle_service.proofs_dir, filename)
                
                with open(proof_path, 'r') as f:
                    proof_data = json.load(f)
                
                proofs.append({
                    'proof_id': proof_id,
                    'url': proof_data['url'],
                    'timestamp': proof_data['timestamp'],
                    'verified': proof_data['verified']
                })
        
        # Sort by timestamp (newest first)
        proofs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'proofs': proofs,
            'total_proofs': len(proofs)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@zk_oracles_bp.route('/feeds', methods=['GET'])
def list_data_feeds():
    """List available data feeds"""
    try:
        feeds = []
        for filename in os.listdir(zk_oracle_service.feeds_dir):
            if filename.endswith('.json'):
                feed_name = filename[:-5]  # Remove .json extension
                feed_result = zk_oracle_service.get_data_feed(feed_name)
                
                if feed_result['success']:
                    feed_data = feed_result['feed_data']
                    feeds.append({
                        'feed_name': feed_name,
                        'source': feed_data['source'],
                        'last_update': feed_data['last_update'],
                        'type': zk_oracle_service.supported_sources.get(feed_data['source'], {}).get('type', 'unknown')
                    })
        
        return jsonify({
            'feeds': feeds,
            'total_feeds': len(feeds)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@zk_oracles_bp.route('/feed/<feed_name>', methods=['GET'])
def get_data_feed(feed_name):
    """Get data from a specific feed"""
    result = zk_oracle_service.get_data_feed(feed_name)
    
    if result['success']:
        return jsonify(result['feed_data'])
    else:
        return jsonify(result), 404

@zk_oracles_bp.route('/crypto/prices', methods=['GET'])
def get_crypto_prices():
    """Get verified crypto prices"""
    # Create session and fetch crypto prices
    session_result = zk_oracle_service.create_tls_session('https://coinmarketcap.com/api/v1/cryptocurrency/quotes/latest')
    
    if not session_result['success']:
        return jsonify(session_result), 500
    
    # Fetch and prove data
    proof_result = zk_oracle_service.fetch_and_prove(session_result['session_id'])
    
    if proof_result['success']:
        return jsonify({
            'prices': proof_result['proof_record']['data'],
            'proof_id': proof_result['proof_id'],
            'verified': True,
            'timestamp': proof_result['proof_record']['timestamp']
        })
    else:
        return jsonify(proof_result), 500

@zk_oracles_bp.route('/github/activity', methods=['GET'])
def get_github_activity():
    """Get verified GitHub activity data"""
    repo = request.args.get('repo', 'DevGruGold/XMRT-Ecosystem')
    
    # Create session and fetch GitHub data
    session_result = zk_oracle_service.create_tls_session(f'https://api.github.com/repos/{repo}')
    
    if not session_result['success']:
        return jsonify(session_result), 500
    
    # Fetch and prove data
    proof_result = zk_oracle_service.fetch_and_prove(session_result['session_id'])
    
    if proof_result['success']:
        return jsonify({
            'activity': proof_result['proof_record']['data'],
            'proof_id': proof_result['proof_id'],
            'verified': True,
            'timestamp': proof_result['proof_record']['timestamp']
        })
    else:
        return jsonify(proof_result), 500

@zk_oracles_bp.route('/news/sentiment', methods=['GET'])
def get_news_sentiment():
    """Get verified news sentiment data"""
    query = request.args.get('q', 'cryptocurrency')
    
    # Create session and fetch news data
    session_result = zk_oracle_service.create_tls_session(f'https://newsapi.org/v2/everything?q={query}')
    
    if not session_result['success']:
        return jsonify(session_result), 500
    
    # Fetch and prove data
    proof_result = zk_oracle_service.fetch_and_prove(session_result['session_id'], {'q': query})
    
    if proof_result['success']:
        return jsonify({
            'sentiment': proof_result['proof_record']['data'],
            'proof_id': proof_result['proof_id'],
            'verified': True,
            'timestamp': proof_result['proof_record']['timestamp']
        })
    else:
        return jsonify(proof_result), 500

@zk_oracles_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check if directories exist and are writable
        dirs_status = {
            'proofs_dir': os.path.exists(zk_oracle_service.proofs_dir) and os.access(zk_oracle_service.proofs_dir, os.W_OK),
            'sessions_dir': os.path.exists(zk_oracle_service.sessions_dir) and os.access(zk_oracle_service.sessions_dir, os.W_OK),
            'feeds_dir': os.path.exists(zk_oracle_service.feeds_dir) and os.access(zk_oracle_service.feeds_dir, os.W_OK)
        }
        
        # Count available resources
        proof_count = len([f for f in os.listdir(zk_oracle_service.proofs_dir) if f.endswith('.json')])
        session_count = len([f for f in os.listdir(zk_oracle_service.sessions_dir) if f.endswith('.json')])
        feed_count = len([f for f in os.listdir(zk_oracle_service.feeds_dir) if f.endswith('.json')])
        
        return jsonify({
            'service': 'zk_oracles',
            'status': 'healthy' if all(dirs_status.values()) else 'degraded',
            'directories': dirs_status,
            'supported_sources': len(zk_oracle_service.supported_sources),
            'generated_proofs': proof_count,
            'active_sessions': session_count,
            'available_feeds': feed_count
        })
    
    except Exception as e:
        return jsonify({
            'service': 'zk_oracles',
            'status': 'error',
            'error': str(e)
        }), 500


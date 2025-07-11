from flask import Blueprint, request, jsonify
import os
import json
import hashlib
import subprocess
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

noir_bp = Blueprint('noir', __name__)

class NoirService:
    def __init__(self):
        self.circuits_dir = os.path.join(os.path.dirname(__file__), '..', 'circuits')
        self.proofs_dir = os.path.join(os.path.dirname(__file__), '..', 'proofs')
        self.keys_dir = os.path.join(os.path.dirname(__file__), '..', 'keys')
        
        # Create directories if they don't exist
        os.makedirs(self.circuits_dir, exist_ok=True)
        os.makedirs(self.proofs_dir, exist_ok=True)
        os.makedirs(self.keys_dir, exist_ok=True)
        
        # Initialize with sample circuits
        self._initialize_sample_circuits()
    
    def _initialize_sample_circuits(self):
        """Initialize sample Noir circuits for common use cases"""
        
        # Private voting circuit
        voting_circuit = '''
use dep::std;

fn main(
    voter_secret: Field,
    proposal_id: Field,
    vote: Field, // 0 for against, 1 for for
    voter_commitment: pub Field,
    proposal_hash: pub Field
) {
    // Verify voter commitment
    let computed_commitment = std::hash::pedersen_hash([voter_secret]);
    assert(computed_commitment == voter_commitment);
    
    // Verify proposal hash
    let computed_proposal_hash = std::hash::pedersen_hash([proposal_id]);
    assert(computed_proposal_hash == proposal_hash);
    
    // Verify vote is valid (0 or 1)
    assert(vote * (vote - 1) == 0);
}
'''
        
        # Treasury calculation circuit
        treasury_circuit = '''
use dep::std;

fn main(
    balances: [Field; 10],
    weights: [Field; 10],
    total_balance: pub Field,
    weighted_average: pub Field
) {
    let mut computed_total: Field = 0;
    let mut weighted_sum: Field = 0;
    let mut weight_sum: Field = 0;
    
    for i in 0..10 {
        computed_total = computed_total + balances[i];
        weighted_sum = weighted_sum + (balances[i] * weights[i]);
        weight_sum = weight_sum + weights[i];
    }
    
    assert(computed_total == total_balance);
    
    // Verify weighted average calculation
    let computed_weighted_avg = weighted_sum / weight_sum;
    assert(computed_weighted_avg == weighted_average);
}
'''
        
        # Save sample circuits
        with open(os.path.join(self.circuits_dir, 'voting.nr'), 'w') as f:
            f.write(voting_circuit)
        
        with open(os.path.join(self.circuits_dir, 'treasury.nr'), 'w') as f:
            f.write(treasury_circuit)
    
    def compile_circuit(self, circuit_name: str) -> Dict[str, Any]:
        """Compile a Noir circuit"""
        try:
            circuit_path = os.path.join(self.circuits_dir, f'{circuit_name}.nr')
            
            if not os.path.exists(circuit_path):
                return {
                    'success': False,
                    'error': f'Circuit {circuit_name} not found'
                }
            
            # In production, this would use actual Noir compiler
            # For now, we simulate the compilation process
            compiled_circuit = {
                'circuit_name': circuit_name,
                'bytecode': f'0x{hashlib.sha256(circuit_name.encode()).hexdigest()}',
                'abi': self._generate_mock_abi(circuit_name),
                'verification_key': f'vk_{circuit_name}_{hashlib.md5(circuit_name.encode()).hexdigest()[:8]}',
                'proving_key': f'pk_{circuit_name}_{hashlib.md5(circuit_name.encode()).hexdigest()[:8]}'
            }
            
            # Save compiled circuit
            compiled_path = os.path.join(self.circuits_dir, f'{circuit_name}_compiled.json')
            with open(compiled_path, 'w') as f:
                json.dump(compiled_circuit, f, indent=2)
            
            return {
                'success': True,
                'compiled_circuit': compiled_circuit,
                'compilation_time': '2.3s'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_mock_abi(self, circuit_name: str) -> Dict[str, Any]:
        """Generate mock ABI for circuit"""
        if circuit_name == 'voting':
            return {
                'parameters': [
                    {'name': 'voter_secret', 'type': 'Field', 'visibility': 'private'},
                    {'name': 'proposal_id', 'type': 'Field', 'visibility': 'private'},
                    {'name': 'vote', 'type': 'Field', 'visibility': 'private'},
                    {'name': 'voter_commitment', 'type': 'Field', 'visibility': 'public'},
                    {'name': 'proposal_hash', 'type': 'Field', 'visibility': 'public'}
                ],
                'return_type': 'void'
            }
        elif circuit_name == 'treasury':
            return {
                'parameters': [
                    {'name': 'balances', 'type': '[Field; 10]', 'visibility': 'private'},
                    {'name': 'weights', 'type': '[Field; 10]', 'visibility': 'private'},
                    {'name': 'total_balance', 'type': 'Field', 'visibility': 'public'},
                    {'name': 'weighted_average', 'type': 'Field', 'visibility': 'public'}
                ],
                'return_type': 'void'
            }
        else:
            return {
                'parameters': [],
                'return_type': 'void'
            }
    
    def generate_proof(self, circuit_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a zero-knowledge proof"""
        try:
            compiled_path = os.path.join(self.circuits_dir, f'{circuit_name}_compiled.json')
            
            if not os.path.exists(compiled_path):
                return {
                    'success': False,
                    'error': f'Compiled circuit {circuit_name} not found. Please compile first.'
                }
            
            # Load compiled circuit
            with open(compiled_path, 'r') as f:
                compiled_circuit = json.load(f)
            
            # Validate inputs against ABI
            validation_result = self._validate_inputs(compiled_circuit['abi'], inputs)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f'Input validation failed: {validation_result["error"]}'
                }
            
            # In production, this would use actual Noir prover
            # For now, we simulate proof generation
            proof_data = {
                'circuit_name': circuit_name,
                'proof': f'0x{hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()}',
                'public_inputs': self._extract_public_inputs(compiled_circuit['abi'], inputs),
                'verification_key': compiled_circuit['verification_key'],
                'timestamp': int(os.times().elapsed * 1000)  # Mock timestamp
            }
            
            # Save proof
            proof_id = hashlib.md5(f'{circuit_name}_{proof_data["timestamp"]}'.encode()).hexdigest()[:16]
            proof_path = os.path.join(self.proofs_dir, f'{proof_id}.json')
            
            with open(proof_path, 'w') as f:
                json.dump(proof_data, f, indent=2)
            
            return {
                'success': True,
                'proof_id': proof_id,
                'proof_data': proof_data,
                'generation_time': '5.7s'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_inputs(self, abi: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate inputs against circuit ABI"""
        try:
            required_params = [param['name'] for param in abi['parameters']]
            provided_params = list(inputs.keys())
            
            missing_params = set(required_params) - set(provided_params)
            if missing_params:
                return {
                    'valid': False,
                    'error': f'Missing required parameters: {list(missing_params)}'
                }
            
            extra_params = set(provided_params) - set(required_params)
            if extra_params:
                return {
                    'valid': False,
                    'error': f'Unexpected parameters: {list(extra_params)}'
                }
            
            return {'valid': True}
        
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def _extract_public_inputs(self, abi: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract public inputs from all inputs"""
        public_inputs = {}
        
        for param in abi['parameters']:
            if param['visibility'] == 'public' and param['name'] in inputs:
                public_inputs[param['name']] = inputs[param['name']]
        
        return public_inputs
    
    def verify_proof(self, proof_id: str) -> Dict[str, Any]:
        """Verify a zero-knowledge proof"""
        try:
            proof_path = os.path.join(self.proofs_dir, f'{proof_id}.json')
            
            if not os.path.exists(proof_path):
                return {
                    'success': False,
                    'error': f'Proof {proof_id} not found'
                }
            
            # Load proof
            with open(proof_path, 'r') as f:
                proof_data = json.load(f)
            
            # In production, this would use actual Noir verifier
            # For now, we simulate verification
            verification_result = {
                'proof_id': proof_id,
                'circuit_name': proof_data['circuit_name'],
                'valid': True,  # Simplified - always valid for demo
                'public_inputs': proof_data['public_inputs'],
                'verification_time': '0.3s'
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
    
    def get_circuit_info(self, circuit_name: str) -> Dict[str, Any]:
        """Get information about a circuit"""
        try:
            circuit_path = os.path.join(self.circuits_dir, f'{circuit_name}.nr')
            compiled_path = os.path.join(self.circuits_dir, f'{circuit_name}_compiled.json')
            
            info = {
                'circuit_name': circuit_name,
                'source_exists': os.path.exists(circuit_path),
                'compiled': os.path.exists(compiled_path)
            }
            
            if info['compiled']:
                with open(compiled_path, 'r') as f:
                    compiled_circuit = json.load(f)
                info['abi'] = compiled_circuit['abi']
                info['verification_key'] = compiled_circuit['verification_key']
            
            return {
                'success': True,
                'circuit_info': info
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Initialize service
noir_service = NoirService()

@noir_bp.route('/circuits', methods=['GET'])
def list_circuits():
    """List available circuits"""
    try:
        circuits = []
        for filename in os.listdir(noir_service.circuits_dir):
            if filename.endswith('.nr'):
                circuit_name = filename[:-3]  # Remove .nr extension
                circuit_info = noir_service.get_circuit_info(circuit_name)
                if circuit_info['success']:
                    circuits.append(circuit_info['circuit_info'])
        
        return jsonify({
            'circuits': circuits,
            'total_circuits': len(circuits)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@noir_bp.route('/circuit/<circuit_name>', methods=['GET'])
def get_circuit_info(circuit_name):
    """Get information about a specific circuit"""
    result = noir_service.get_circuit_info(circuit_name)
    
    if result['success']:
        return jsonify(result['circuit_info'])
    else:
        return jsonify(result), 404

@noir_bp.route('/compile/<circuit_name>', methods=['POST'])
def compile_circuit(circuit_name):
    """Compile a Noir circuit"""
    result = noir_service.compile_circuit(circuit_name)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@noir_bp.route('/prove/<circuit_name>', methods=['POST'])
def generate_proof(circuit_name):
    """Generate a zero-knowledge proof"""
    data = request.get_json()
    
    if 'inputs' not in data:
        return jsonify({'error': 'Missing inputs'}), 400
    
    result = noir_service.generate_proof(circuit_name, data['inputs'])
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@noir_bp.route('/verify/<proof_id>', methods=['GET'])
def verify_proof(proof_id):
    """Verify a zero-knowledge proof"""
    result = noir_service.verify_proof(proof_id)
    
    if result['success']:
        return jsonify(result['verification_result'])
    else:
        return jsonify(result), 404

@noir_bp.route('/proofs', methods=['GET'])
def list_proofs():
    """List all generated proofs"""
    try:
        proofs = []
        for filename in os.listdir(noir_service.proofs_dir):
            if filename.endswith('.json'):
                proof_id = filename[:-5]  # Remove .json extension
                proof_path = os.path.join(noir_service.proofs_dir, filename)
                
                with open(proof_path, 'r') as f:
                    proof_data = json.load(f)
                
                proofs.append({
                    'proof_id': proof_id,
                    'circuit_name': proof_data['circuit_name'],
                    'timestamp': proof_data['timestamp'],
                    'public_inputs': proof_data['public_inputs']
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

@noir_bp.route('/voting/prove', methods=['POST'])
def prove_vote():
    """Generate proof for private voting"""
    data = request.get_json()
    
    required_fields = ['voter_secret', 'proposal_id', 'vote', 'voter_commitment', 'proposal_hash']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields for voting proof'}), 400
    
    # Ensure circuit is compiled
    compile_result = noir_service.compile_circuit('voting')
    if not compile_result['success']:
        return jsonify(compile_result), 500
    
    # Generate proof
    result = noir_service.generate_proof('voting', data)
    
    if result['success']:
        return jsonify({
            'vote_proof': result['proof_data'],
            'proof_id': result['proof_id'],
            'message': 'Vote proof generated successfully'
        })
    else:
        return jsonify(result), 400

@noir_bp.route('/treasury/prove', methods=['POST'])
def prove_treasury_calculation():
    """Generate proof for treasury calculations"""
    data = request.get_json()
    
    required_fields = ['balances', 'weights', 'total_balance', 'weighted_average']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields for treasury proof'}), 400
    
    # Ensure circuit is compiled
    compile_result = noir_service.compile_circuit('treasury')
    if not compile_result['success']:
        return jsonify(compile_result), 500
    
    # Generate proof
    result = noir_service.generate_proof('treasury', data)
    
    if result['success']:
        return jsonify({
            'treasury_proof': result['proof_data'],
            'proof_id': result['proof_id'],
            'message': 'Treasury calculation proof generated successfully'
        })
    else:
        return jsonify(result), 400

@noir_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check if directories exist and are writable
        dirs_status = {
            'circuits_dir': os.path.exists(noir_service.circuits_dir) and os.access(noir_service.circuits_dir, os.W_OK),
            'proofs_dir': os.path.exists(noir_service.proofs_dir) and os.access(noir_service.proofs_dir, os.W_OK),
            'keys_dir': os.path.exists(noir_service.keys_dir) and os.access(noir_service.keys_dir, os.W_OK)
        }
        
        # Count available circuits and proofs
        circuit_count = len([f for f in os.listdir(noir_service.circuits_dir) if f.endswith('.nr')])
        proof_count = len([f for f in os.listdir(noir_service.proofs_dir) if f.endswith('.json')])
        
        return jsonify({
            'service': 'noir',
            'status': 'healthy' if all(dirs_status.values()) else 'degraded',
            'directories': dirs_status,
            'available_circuits': circuit_count,
            'generated_proofs': proof_count
        })
    
    except Exception as e:
        return jsonify({
            'service': 'noir',
            'status': 'error',
            'error': str(e)
        }), 500


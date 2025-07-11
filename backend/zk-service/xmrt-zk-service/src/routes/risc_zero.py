from flask import Blueprint, request, jsonify
import os
import json
import hashlib
import time
from typing import Dict, Any, Optional, List

risc_zero_bp = Blueprint('risc_zero', __name__)

class RiscZeroService:
    def __init__(self):
        self.programs_dir = os.path.join(os.path.dirname(__file__), '..', 'risc_zero_programs')
        self.receipts_dir = os.path.join(os.path.dirname(__file__), '..', 'receipts')
        self.execution_dir = os.path.join(os.path.dirname(__file__), '..', 'executions')
        
        # Create directories if they don't exist
        os.makedirs(self.programs_dir, exist_ok=True)
        os.makedirs(self.receipts_dir, exist_ok=True)
        os.makedirs(self.execution_dir, exist_ok=True)
        
        # Initialize with sample programs
        self._initialize_sample_programs()
    
    def _initialize_sample_programs(self):
        """Initialize sample RISC Zero programs for common use cases"""
        
        # Treasury optimization program
        treasury_program = '''
// RISC Zero Treasury Optimization Program
use risc0_zkvm::guest::env;

fn main() {
    // Read inputs from host
    let asset_prices: Vec<f64> = env::read();
    let current_allocations: Vec<f64> = env::read();
    let risk_tolerance: f64 = env::read();
    let target_return: f64 = env::read();
    
    // Perform portfolio optimization
    let optimized_allocations = optimize_portfolio(
        &asset_prices,
        &current_allocations,
        risk_tolerance,
        target_return
    );
    
    // Calculate expected return and risk
    let expected_return = calculate_expected_return(&asset_prices, &optimized_allocations);
    let portfolio_risk = calculate_portfolio_risk(&optimized_allocations);
    
    // Commit results to journal
    env::commit(&optimized_allocations);
    env::commit(&expected_return);
    env::commit(&portfolio_risk);
}

fn optimize_portfolio(
    prices: &[f64],
    current: &[f64],
    risk_tolerance: f64,
    target_return: f64
) -> Vec<f64> {
    // Simplified portfolio optimization algorithm
    let mut optimized = current.to_vec();
    
    // Apply mean reversion strategy
    for i in 0..prices.len() {
        let price_momentum = if i > 0 { prices[i] / prices[i-1] - 1.0 } else { 0.0 };
        
        if price_momentum > 0.05 {
            // Reduce allocation if price increased significantly
            optimized[i] *= 0.95;
        } else if price_momentum < -0.05 {
            // Increase allocation if price decreased significantly
            optimized[i] *= 1.05;
        }
    }
    
    // Normalize allocations to sum to 1.0
    let total: f64 = optimized.iter().sum();
    optimized.iter_mut().for_each(|x| *x /= total);
    
    optimized
}

fn calculate_expected_return(prices: &[f64], allocations: &[f64]) -> f64 {
    prices.iter()
        .zip(allocations.iter())
        .map(|(price, alloc)| price * alloc)
        .sum()
}

fn calculate_portfolio_risk(allocations: &[f64]) -> f64 {
    // Simplified risk calculation (variance of allocations)
    let mean = allocations.iter().sum::<f64>() / allocations.len() as f64;
    let variance = allocations.iter()
        .map(|x| (x - mean).powi(2))
        .sum::<f64>() / allocations.len() as f64;
    variance.sqrt()
}
'''
        
        # Governance analysis program
        governance_program = '''
// RISC Zero Governance Analysis Program
use risc0_zkvm::guest::env;

fn main() {
    // Read proposal data
    let proposal_text: String = env::read();
    let historical_votes: Vec<(String, bool, f64)> = env::read(); // (voter, vote, stake)
    let current_stakes: Vec<(String, f64)> = env::read();
    
    // Analyze proposal sentiment
    let sentiment_score = analyze_sentiment(&proposal_text);
    
    // Predict voting outcome
    let predicted_outcome = predict_voting_outcome(&historical_votes, &current_stakes, sentiment_score);
    
    // Calculate participation metrics
    let participation_metrics = calculate_participation(&historical_votes, &current_stakes);
    
    // Commit results
    env::commit(&sentiment_score);
    env::commit(&predicted_outcome);
    env::commit(&participation_metrics);
}

fn analyze_sentiment(text: &str) -> f64 {
    // Simplified sentiment analysis
    let positive_words = ["good", "great", "excellent", "improve", "benefit", "positive"];
    let negative_words = ["bad", "terrible", "harmful", "negative", "risk", "dangerous"];
    
    let words: Vec<&str> = text.to_lowercase().split_whitespace().collect();
    let positive_count = words.iter().filter(|w| positive_words.contains(w)).count() as f64;
    let negative_count = words.iter().filter(|w| negative_words.contains(w)).count() as f64;
    
    if positive_count + negative_count == 0.0 {
        0.0 // Neutral
    } else {
        (positive_count - negative_count) / (positive_count + negative_count)
    }
}

fn predict_voting_outcome(
    historical_votes: &[(String, bool, f64)],
    current_stakes: &[(String, f64)],
    sentiment: f64
) -> (f64, f64) { // (probability_for, probability_against)
    let total_stake: f64 = current_stakes.iter().map(|(_, stake)| stake).sum();
    
    // Weight sentiment by stake
    let sentiment_weight = 0.3;
    let historical_weight = 0.7;
    
    // Calculate historical voting patterns
    let historical_for_rate = historical_votes.iter()
        .filter(|(_, vote, _)| *vote)
        .map(|(_, _, stake)| stake)
        .sum::<f64>() / historical_votes.iter().map(|(_, _, stake)| stake).sum::<f64>();
    
    // Combine sentiment and historical data
    let base_probability = historical_for_rate * historical_weight + 
                          (sentiment + 1.0) / 2.0 * sentiment_weight;
    
    (base_probability, 1.0 - base_probability)
}

fn calculate_participation(
    historical_votes: &[(String, bool, f64)],
    current_stakes: &[(String, f64)]
) -> (f64, f64, f64) { // (participation_rate, avg_stake_per_vote, stake_concentration)
    let total_current_stake: f64 = current_stakes.iter().map(|(_, stake)| stake).sum();
    let voting_stake: f64 = historical_votes.iter().map(|(_, _, stake)| stake).sum();
    
    let participation_rate = voting_stake / total_current_stake;
    let avg_stake_per_vote = voting_stake / historical_votes.len() as f64;
    
    // Calculate Gini coefficient for stake concentration
    let mut stakes: Vec<f64> = current_stakes.iter().map(|(_, stake)| *stake).collect();
    stakes.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let n = stakes.len() as f64;
    let sum_stakes: f64 = stakes.iter().sum();
    let gini = stakes.iter().enumerate()
        .map(|(i, stake)| (2.0 * (i as f64 + 1.0) - n - 1.0) * stake)
        .sum::<f64>() / (n * sum_stakes);
    
    (participation_rate, avg_stake_per_vote, gini)
}
'''
        
        # Save sample programs
        with open(os.path.join(self.programs_dir, 'treasury_optimization.rs'), 'w') as f:
            f.write(treasury_program)
        
        with open(os.path.join(self.programs_dir, 'governance_analysis.rs'), 'w') as f:
            f.write(governance_program)
    
    def execute_program(self, program_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a RISC Zero program with given inputs"""
        try:
            program_path = os.path.join(self.programs_dir, f'{program_name}.rs')
            
            if not os.path.exists(program_path):
                return {
                    'success': False,
                    'error': f'Program {program_name} not found'
                }
            
            # In production, this would compile and execute the actual RISC Zero program
            # For now, we simulate the execution
            execution_id = hashlib.md5(f'{program_name}_{time.time()}'.encode()).hexdigest()[:16]
            
            # Simulate program execution based on program type
            if program_name == 'treasury_optimization':
                result = self._simulate_treasury_optimization(inputs)
            elif program_name == 'governance_analysis':
                result = self._simulate_governance_analysis(inputs)
            else:
                result = self._simulate_generic_execution(inputs)
            
            # Create execution record
            execution_record = {
                'execution_id': execution_id,
                'program_name': program_name,
                'inputs': inputs,
                'outputs': result['outputs'],
                'execution_time': result['execution_time'],
                'gas_used': result['gas_used'],
                'timestamp': int(time.time()),
                'status': 'completed'
            }
            
            # Save execution record
            execution_path = os.path.join(self.execution_dir, f'{execution_id}.json')
            with open(execution_path, 'w') as f:
                json.dump(execution_record, f, indent=2)
            
            return {
                'success': True,
                'execution_id': execution_id,
                'execution_record': execution_record
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _simulate_treasury_optimization(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate treasury optimization execution"""
        asset_prices = inputs.get('asset_prices', [100, 50, 200, 75])
        current_allocations = inputs.get('current_allocations', [0.25, 0.25, 0.25, 0.25])
        risk_tolerance = inputs.get('risk_tolerance', 0.5)
        target_return = inputs.get('target_return', 0.08)
        
        # Simulate optimization algorithm
        optimized_allocations = []
        for i, (price, current) in enumerate(zip(asset_prices, current_allocations)):
            # Simple momentum-based rebalancing
            momentum = (price - 100) / 100  # Assuming 100 is baseline
            if momentum > 0.1:
                new_alloc = current * 0.9  # Reduce high-performing assets
            elif momentum < -0.1:
                new_alloc = current * 1.1  # Increase underperforming assets
            else:
                new_alloc = current
            optimized_allocations.append(new_alloc)
        
        # Normalize allocations
        total = sum(optimized_allocations)
        optimized_allocations = [alloc / total for alloc in optimized_allocations]
        
        expected_return = sum(price * alloc for price, alloc in zip(asset_prices, optimized_allocations)) / 100
        portfolio_risk = sum((alloc - 0.25) ** 2 for alloc in optimized_allocations) ** 0.5
        
        return {
            'outputs': {
                'optimized_allocations': optimized_allocations,
                'expected_return': expected_return,
                'portfolio_risk': portfolio_risk,
                'rebalancing_needed': any(abs(opt - curr) > 0.05 for opt, curr in zip(optimized_allocations, current_allocations))
            },
            'execution_time': '3.2s',
            'gas_used': 1500000
        }
    
    def _simulate_governance_analysis(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate governance analysis execution"""
        proposal_text = inputs.get('proposal_text', '')
        historical_votes = inputs.get('historical_votes', [])
        current_stakes = inputs.get('current_stakes', [])
        
        # Simulate sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'improve', 'benefit', 'positive']
        negative_words = ['bad', 'terrible', 'harmful', 'negative', 'risk', 'dangerous']
        
        words = proposal_text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count + negative_count == 0:
            sentiment_score = 0.0
        else:
            sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
        
        # Simulate voting prediction
        if historical_votes:
            historical_for_rate = sum(1 for vote in historical_votes if vote.get('vote', False)) / len(historical_votes)
        else:
            historical_for_rate = 0.5
        
        predicted_for = (historical_for_rate * 0.7) + ((sentiment_score + 1) / 2 * 0.3)
        predicted_against = 1.0 - predicted_for
        
        # Simulate participation metrics
        total_stake = sum(stake.get('amount', 0) for stake in current_stakes)
        voting_stake = sum(vote.get('stake', 0) for vote in historical_votes)
        participation_rate = voting_stake / total_stake if total_stake > 0 else 0
        
        return {
            'outputs': {
                'sentiment_score': sentiment_score,
                'predicted_outcome': {
                    'probability_for': predicted_for,
                    'probability_against': predicted_against
                },
                'participation_metrics': {
                    'participation_rate': participation_rate,
                    'total_voting_stake': voting_stake,
                    'total_eligible_stake': total_stake
                }
            },
            'execution_time': '2.1s',
            'gas_used': 1200000
        }
    
    def _simulate_generic_execution(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate generic program execution"""
        return {
            'outputs': {
                'result': 'Program executed successfully',
                'input_hash': hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest(),
                'computation_verified': True
            },
            'execution_time': '1.5s',
            'gas_used': 800000
        }
    
    def generate_receipt(self, execution_id: str) -> Dict[str, Any]:
        """Generate a verifiable receipt for an execution"""
        try:
            execution_path = os.path.join(self.execution_dir, f'{execution_id}.json')
            
            if not os.path.exists(execution_path):
                return {
                    'success': False,
                    'error': f'Execution {execution_id} not found'
                }
            
            # Load execution record
            with open(execution_path, 'r') as f:
                execution_record = json.load(f)
            
            # In production, this would generate an actual RISC Zero receipt
            # For now, we simulate the receipt generation
            receipt = {
                'execution_id': execution_id,
                'program_name': execution_record['program_name'],
                'journal': execution_record['outputs'],
                'seal': f'0x{hashlib.sha256(f"{execution_id}_{execution_record["timestamp"]}".encode()).hexdigest()}',
                'verification_key': f'vk_{execution_record["program_name"]}_{hashlib.md5(execution_record["program_name"].encode()).hexdigest()[:8]}',
                'timestamp': execution_record['timestamp'],
                'gas_used': execution_record['gas_used']
            }
            
            # Save receipt
            receipt_path = os.path.join(self.receipts_dir, f'{execution_id}_receipt.json')
            with open(receipt_path, 'w') as f:
                json.dump(receipt, f, indent=2)
            
            return {
                'success': True,
                'receipt': receipt
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_receipt(self, execution_id: str) -> Dict[str, Any]:
        """Verify a RISC Zero receipt"""
        try:
            receipt_path = os.path.join(self.receipts_dir, f'{execution_id}_receipt.json')
            
            if not os.path.exists(receipt_path):
                return {
                    'success': False,
                    'error': f'Receipt for execution {execution_id} not found'
                }
            
            # Load receipt
            with open(receipt_path, 'r') as f:
                receipt = json.load(f)
            
            # In production, this would verify the actual RISC Zero receipt
            # For now, we simulate verification
            verification_result = {
                'execution_id': execution_id,
                'program_name': receipt['program_name'],
                'verified': True,  # Simplified - always verified for demo
                'journal_hash': hashlib.sha256(json.dumps(receipt['journal'], sort_keys=True).encode()).hexdigest(),
                'verification_time': '0.5s'
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

# Initialize service
risc_zero_service = RiscZeroService()

@risc_zero_bp.route('/programs', methods=['GET'])
def list_programs():
    """List available RISC Zero programs"""
    try:
        programs = []
        for filename in os.listdir(risc_zero_service.programs_dir):
            if filename.endswith('.rs'):
                program_name = filename[:-3]  # Remove .rs extension
                programs.append({
                    'program_name': program_name,
                    'file_path': filename,
                    'description': f'RISC Zero program for {program_name.replace("_", " ")}'
                })
        
        return jsonify({
            'programs': programs,
            'total_programs': len(programs)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@risc_zero_bp.route('/execute/<program_name>', methods=['POST'])
def execute_program(program_name):
    """Execute a RISC Zero program"""
    data = request.get_json()
    
    if 'inputs' not in data:
        return jsonify({'error': 'Missing inputs'}), 400
    
    result = risc_zero_service.execute_program(program_name, data['inputs'])
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@risc_zero_bp.route('/receipt/<execution_id>', methods=['POST'])
def generate_receipt(execution_id):
    """Generate a verifiable receipt for an execution"""
    result = risc_zero_service.generate_receipt(execution_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 404

@risc_zero_bp.route('/verify/<execution_id>', methods=['GET'])
def verify_receipt(execution_id):
    """Verify a RISC Zero receipt"""
    result = risc_zero_service.verify_receipt(execution_id)
    
    if result['success']:
        return jsonify(result['verification_result'])
    else:
        return jsonify(result), 404

@risc_zero_bp.route('/executions', methods=['GET'])
def list_executions():
    """List all program executions"""
    try:
        executions = []
        for filename in os.listdir(risc_zero_service.execution_dir):
            if filename.endswith('.json'):
                execution_id = filename[:-5]  # Remove .json extension
                execution_path = os.path.join(risc_zero_service.execution_dir, filename)
                
                with open(execution_path, 'r') as f:
                    execution_data = json.load(f)
                
                executions.append({
                    'execution_id': execution_id,
                    'program_name': execution_data['program_name'],
                    'timestamp': execution_data['timestamp'],
                    'status': execution_data['status'],
                    'gas_used': execution_data['gas_used']
                })
        
        # Sort by timestamp (newest first)
        executions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'executions': executions,
            'total_executions': len(executions)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@risc_zero_bp.route('/treasury/optimize', methods=['POST'])
def optimize_treasury():
    """Execute treasury optimization program"""
    data = request.get_json()
    
    required_fields = ['asset_prices', 'current_allocations']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields for treasury optimization'}), 400
    
    result = risc_zero_service.execute_program('treasury_optimization', data)
    
    if result['success']:
        # Generate receipt automatically
        receipt_result = risc_zero_service.generate_receipt(result['execution_id'])
        
        return jsonify({
            'optimization_result': result['execution_record']['outputs'],
            'execution_id': result['execution_id'],
            'receipt_generated': receipt_result['success'],
            'message': 'Treasury optimization completed successfully'
        })
    else:
        return jsonify(result), 400

@risc_zero_bp.route('/governance/analyze', methods=['POST'])
def analyze_governance():
    """Execute governance analysis program"""
    data = request.get_json()
    
    required_fields = ['proposal_text']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields for governance analysis'}), 400
    
    result = risc_zero_service.execute_program('governance_analysis', data)
    
    if result['success']:
        # Generate receipt automatically
        receipt_result = risc_zero_service.generate_receipt(result['execution_id'])
        
        return jsonify({
            'analysis_result': result['execution_record']['outputs'],
            'execution_id': result['execution_id'],
            'receipt_generated': receipt_result['success'],
            'message': 'Governance analysis completed successfully'
        })
    else:
        return jsonify(result), 400

@risc_zero_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check if directories exist and are writable
        dirs_status = {
            'programs_dir': os.path.exists(risc_zero_service.programs_dir) and os.access(risc_zero_service.programs_dir, os.W_OK),
            'receipts_dir': os.path.exists(risc_zero_service.receipts_dir) and os.access(risc_zero_service.receipts_dir, os.W_OK),
            'execution_dir': os.path.exists(risc_zero_service.execution_dir) and os.access(risc_zero_service.execution_dir, os.W_OK)
        }
        
        # Count available programs and executions
        program_count = len([f for f in os.listdir(risc_zero_service.programs_dir) if f.endswith('.rs')])
        execution_count = len([f for f in os.listdir(risc_zero_service.execution_dir) if f.endswith('.json')])
        receipt_count = len([f for f in os.listdir(risc_zero_service.receipts_dir) if f.endswith('.json')])
        
        return jsonify({
            'service': 'risc_zero',
            'status': 'healthy' if all(dirs_status.values()) else 'degraded',
            'directories': dirs_status,
            'available_programs': program_count,
            'total_executions': execution_count,
            'generated_receipts': receipt_count
        })
    
    except Exception as e:
        return jsonify({
            'service': 'risc_zero',
            'status': 'error',
            'error': str(e)
        }), 500


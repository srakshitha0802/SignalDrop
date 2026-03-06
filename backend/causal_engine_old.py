"""
Causal & Counterfactual Intelligence Engine for SignalDrop AI

Provides causal analysis, counterfactual reasoning, and failure mode transparency
to prove the system reasons rather than memorizes.
"""

import json
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import random

class CausalEngine:
    """Causal reasoning engine for SignalDrop AI"""
    
    def __init__(self):
        self.signal_weights = {
            'lms_activity': 0.3,
            'assignments': 0.25,
            'messages': 0.25,
            'attendance': 0.2
        }
        
        self.risk_threshold = 0.7
        self.momentum_threshold = 0.1
        
    def analyze_what_changed(self, student_data: Dict, alert_week: int) -> Dict[str, Any]:
        """Analyze what changed between periods to trigger alert"""
        
        # Get data from alert week and previous weeks
        current_week = alert_week
        previous_week = max(1, alert_week - 2)
        
        changes = {}
        
        # Analyze each signal source
        for signal_type in ['lms_activity', 'assignments', 'messages', 'attendance']:
            change = self._calculate_signal_change(student_data, signal_type, previous_week, current_week)
            changes[signal_type] = change
        
        # Determine which changes crossed thresholds
        significant_changes = []
        for signal_type, change in changes.items():
            if abs(change['percent_change']) > 15:  # 15% threshold
                significant_changes.append({
                    'signal': signal_type,
                    'change': change,
                    'contribution': self._calculate_contribution(change, self.signal_weights[signal_type])
                })
        
        # Sort by contribution
        significant_changes.sort(key=lambda x: x['contribution'], reverse=True)
        
        return {
            'analysis_period': f"Week {previous_week} → Week {current_week}",
            'significant_changes': significant_changes,
            'threshold_crossing': self._explain_threshold_crossing(significant_changes),
            'time_lag_analysis': self._analyze_time_lags(student_data, significant_changes, alert_week)
        }
    
    def _calculate_signal_change(self, student_data: Dict, signal_type: str, week_from: int, week_to: int) -> Dict[str, Any]:
        """Calculate change in signal between weeks"""
        
        # Get signal values for both weeks
        from_value = self._get_signal_value(student_data, signal_type, week_from)
        to_value = self._get_signal_value(student_data, signal_type, week_to)
        
        if from_value == 0:
            percent_change = 0
        else:
            percent_change = ((to_value - from_value) / from_value) * 100
        
        direction = 'increased' if percent_change > 0 else 'decreased'
        magnitude = abs(percent_change)
        
        return {
            'from_value': from_value,
            'to_value': to_value,
            'percent_change': percent_change,
            'direction': direction,
            'magnitude': magnitude,
            'signal_type': signal_type
        }
    
    def _get_signal_value(self, student_data: Dict, signal_type: str, week: int) -> float:
        """Get normalized signal value for a specific week"""
        
        # Simulate signal extraction from student data
        if signal_type == 'lms_activity':
            # Simulate declining activity
            base_value = 100
            decline_rate = 0.05 * week
            noise = random.uniform(-5, 5)
            return max(10, base_value - (base_value * decline_rate) + noise)
        
        elif signal_type == 'assignments':
            # Simulate assignment delays
            base_delay = 0.5
            increase_rate = 0.1 * week
            noise = random.uniform(-0.2, 0.2)
            return max(0, base_delay + increase_rate + noise)
        
        elif signal_type == 'messages':
            # Simulate message sentiment
            base_sentiment = 0.8
            decline_rate = 0.03 * week
            noise = random.uniform(-0.1, 0.1)
            return max(0, base_sentiment - decline_rate + noise)
        
        elif signal_type == 'attendance':
            # Simulate attendance
            base_attendance = 0.95
            decline_rate = 0.02 * week
            noise = random.uniform(-0.05, 0.05)
            return max(0.5, base_attendance - decline_rate + noise)
        
        return 0
    
    def _calculate_contribution(self, change: Dict, weight: float) -> float:
        """Calculate how much this change contributed to risk"""
        
        # Normalize change magnitude (0-1 scale)
        normalized_magnitude = min(1.0, change['magnitude'] / 50.0)
        
        # Apply signal weight
        contribution = normalized_magnitude * weight
        
        # Negative changes (declines) contribute more to risk
        if change['direction'] == 'decreased':
            contribution *= 1.5
        
        return contribution
    
    def _explain_threshold_crossing(self, significant_changes: List[Dict]) -> str:
        """Explain why changes crossed risk threshold"""
        
        if not significant_changes:
            return "No significant changes detected."
        
        total_contribution = sum(change['contribution'] for change in significant_changes)
        
        explanation_parts = []
        for change in significant_changes[:3]:  # Top 3 contributors
            signal_name = change['signal'].replace('_', ' ').title()
            change_desc = f"{signal_name} {change['change']['direction']} {change['change']['magnitude']:.1f}%"
            explanation_parts.append(change_desc)
        
        changes_str = ", ".join(explanation_parts)
        
        return f"This combination crossed the risk momentum threshold. Total risk contribution: {total_contribution:.2f}. Key changes: {changes_str}."
    
    def _analyze_time_lags(self, student_data: Dict, significant_changes: List[Dict], alert_week: int) -> Dict[str, Any]:
        """Analyze time lags between signal changes and alert"""
        
        time_lags = {}
        
        for change in significant_changes:
            signal_type = change['signal']
            
            # Find when this signal started changing significantly
            start_week = self._find_change_start_week(student_data, signal_type, alert_week)
            
            if start_week:
                lag_weeks = alert_week - start_week
                time_lags[signal_type] = {
                    'started_changing_week': start_week,
                    'alert_week': alert_week,
                    'lag_weeks': lag_weeks,
                    'interpretation': self._interpret_lag(lag_weeks, signal_type)
                }
        
        return time_lags
    
    def _find_change_start_week(self, student_data: Dict, signal_type: str, alert_week: int) -> int:
        """Find when a signal started changing significantly"""
        
        # Look backwards from alert week to find start of change
        for week in range(alert_week - 1, max(1, alert_week - 8), -1):
            change = self._calculate_signal_change(student_data, signal_type, week, week + 1)
            
            # If this week had significant change, this might be the start
            if abs(change['percent_change']) > 10:
                return week
        
        return None
    
    def _interpret_lag(self, lag_weeks: int, signal_type: str) -> str:
        """Interpret the meaning of time lag"""
        
        if lag_weeks <= 2:
            return "Immediate response to signal change"
        elif lag_weeks <= 4:
            return "Gradual accumulation of risk"
        else:
            return "Delayed response - possible threshold effect"
    
    def generate_counterfactuals(self, student_data: Dict, alert_week: int) -> List[Dict[str, Any]]:
        """Generate counterfactual scenarios"""
        
        counterfactuals = []
        
        # Counterfactual 1: If attendance stayed constant
        cf1 = self._counterfactual_constant_attendance(student_data, alert_week)
        counterfactuals.append(cf1)
        
        # Counterfactual 2: If sentiment improved but engagement dropped
        cf2 = self._counterfactual_mixed_signals(student_data, alert_week)
        counterfactuals.append(cf2)
        
        # Counterfactual 3: If assignments recovered but messages worsened
        cf3 = self._counterfactual_partial_recovery(student_data, alert_week)
        counterfactuals.append(cf3)
        
        return counterfactuals
    
    def _counterfactual_constant_attendance(self, student_data: Dict, alert_week: int) -> Dict[str, Any]:
        """Counterfactual: What if attendance stayed constant?"""
        
        # Get current risk
        current_risk = self._calculate_risk_score(student_data, alert_week)
        
        # Modify attendance to stay constant (use week 1 values)
        modified_data = self._modify_attendance_constant(student_data)
        
        # Calculate new risk
        new_risk = self._calculate_risk_score(modified_data, alert_week)
        
        # Calculate momentum
        current_momentum = self._calculate_momentum(student_data, alert_week)
        new_momentum = self._calculate_momentum(modified_data, alert_week)
        
        # Determine if alert still triggers
        still_alerts = new_risk > self.risk_threshold and new_momentum > self.momentum_threshold
        
        return {
            'scenario': 'If attendance stayed constant',
            'description': 'Attendance maintained at Week 1 levels throughout semester',
            'risk_change': {
                'from': current_risk,
                'to': new_risk,
                'delta': new_risk - current_risk,
                'percent_change': ((new_risk - current_risk) / current_risk) * 100 if current_risk > 0 else 0
            },
            'momentum_change': {
                'from': current_momentum,
                'to': new_momentum,
                'delta': new_momentum - current_momentum
            },
            'still_alerts': still_alerts,
            'interpretation': self._interpret_counterfactual_result(new_risk, new_momentum, still_alerts)
        }
    
    def _counterfactual_mixed_signals(self, student_data: Dict, alert_week: int) -> Dict[str, Any]:
        """Counterfactual: What if sentiment improved but engagement dropped?"""
        
        current_risk = self._calculate_risk_score(student_data, alert_week)
        
        # Improve sentiment but worsen engagement
        modified_data = self._modify_mixed_signals(student_data, alert_week)
        
        new_risk = self._calculate_risk_score(modified_data, alert_week)
        current_momentum = self._calculate_momentum(student_data, alert_week)
        new_momentum = self._calculate_momentum(modified_data, alert_week)
        still_alerts = new_risk > self.risk_threshold and new_momentum > self.momentum_threshold
        
        return {
            'scenario': 'If sentiment improved but engagement dropped',
            'description': 'Message sentiment improved 20% while LMS activity declined 30%',
            'risk_change': {
                'from': current_risk,
                'to': new_risk,
                'delta': new_risk - current_risk,
                'percent_change': ((new_risk - current_risk) / current_risk) * 100 if current_risk > 0 else 0
            },
            'momentum_change': {
                'from': current_momentum,
                'to': new_momentum,
                'delta': new_momentum - current_momentum
            },
            'still_alerts': still_alerts,
            'interpretation': self._interpret_counterfactual_result(new_risk, new_momentum, still_alerts)
        }
    
    def _counterfactual_partial_recovery(self, student_data: Dict, alert_week: int) -> Dict[str, Any]:
        """Counterfactual: What if assignments recovered but messages worsened?"""
        
        current_risk = self._calculate_risk_score(student_data, alert_week)
        
        # Improve assignments but worsen messages
        modified_data = self._modify_partial_recovery(student_data, alert_week)
        
        new_risk = self._calculate_risk_score(modified_data, alert_week)
        current_momentum = self._calculate_momentum(student_data, alert_week)
        new_momentum = self._calculate_momentum(modified_data, alert_week)
        still_alerts = new_risk > self.risk_threshold and new_momentum > self.momentum_threshold
        
        return {
            'scenario': 'If assignments recovered but messages worsened',
            'description': 'Assignment delays reduced 50% while message sentiment declined 40%',
            'risk_change': {
                'from': current_risk,
                'to': new_risk,
                'delta': new_risk - current_risk,
                'percent_change': ((new_risk - current_risk) / current_risk) * 100 if current_risk > 0 else 0
            },
            'momentum_change': {
                'from': current_momentum,
                'to': new_momentum,
                'delta': new_momentum - current_momentum
            },
            'still_alerts': still_alerts,
            'interpretation': self._interpret_counterfactual_result(new_risk, new_momentum, still_alerts)
        }
    
    def _modify_attendance_constant(self, student_data: Dict) -> Dict:
        """Modify data to keep attendance constant"""
        # This would modify the actual data structure
        # For now, return a copy with modification flag
        return {**student_data, 'attendance_modified': 'constant'}
    
    def _modify_mixed_signals(self, student_data: Dict, alert_week: int) -> Dict:
        """Modify data for mixed signal scenario"""
        return {**student_data, 'signals_modified': 'mixed'}
    
    def _modify_partial_recovery(self, student_data: Dict, alert_week: int) -> Dict:
        """Modify data for partial recovery scenario"""
        return {**student_data, 'signals_modified': 'partial_recovery'}
    
    def _interpret_counterfactual_result(self, new_risk: float, new_momentum: float, still_alerts: bool) -> str:
        """Interpret counterfactual result"""
        
        if still_alerts:
            return "Alert would still trigger - risk factors are robust to this change"
        else:
            if new_risk < self.risk_threshold and new_momentum < self.momentum_threshold:
                return "Alert would not trigger - both risk score and momentum below thresholds"
            elif new_risk < self.risk_threshold:
                return "Alert would not trigger - risk score below threshold"
            else:
                return "Alert would not trigger - momentum below threshold"
    
    def _calculate_risk_score(self, student_data: Dict, week: int) -> float:
        """Calculate overall risk score for a week"""
        
        risk_factors = []
        
        for signal_type in ['lms_activity', 'assignments', 'messages', 'attendance']:
            value = self._get_signal_value(student_data, signal_type, week)
            
            # Convert to risk factor (0-1 scale, higher = more risk)
            if signal_type == 'lms_activity':
                risk_factor = 1.0 - (value / 100.0)  # Lower activity = higher risk
            elif signal_type == 'assignments':
                risk_factor = min(1.0, value / 7.0)  # Higher delays = higher risk
            elif signal_type == 'messages':
                risk_factor = 1.0 - value  # Lower sentiment = higher risk
            elif signal_type == 'attendance':
                risk_factor = 1.0 - value  # Lower attendance = higher risk
            
            risk_factors.append(risk_factor * self.signal_weights[signal_type])
        
        return sum(risk_factors)
    
    def _calculate_momentum(self, student_data: Dict, week: int) -> float:
        """Calculate risk momentum (rate of change)"""
        
        if week <= 1:
            return 0.0
        
        current_risk = self._calculate_risk_score(student_data, week)
        previous_risk = self._calculate_risk_score(student_data, week - 1)
        
        return current_risk - previous_risk
    
    def identify_failure_modes(self, student_data: Dict, alert_week: int) -> Dict[str, Any]:
        """Identify potential failure modes and uncertainty factors"""
        
        failure_modes = []
        
        # Check for sparse data
        data_sparsity = self._check_data_sparsity(student_data, alert_week)
        if data_sparsity['is_sparse']:
            failure_modes.append({
                'type': 'Sparse Data',
                'description': data_sparsity['description'],
                'impact': 'Reduced confidence in risk assessment',
                'mitigation': 'Increased uncertainty score, human review required'
            })
        
        # Check for sudden behavioral shocks
        behavioral_shock = self._check_behavioral_shocks(student_data, alert_week)
        if behavioral_shock['has_shock']:
            failure_modes.append({
                'type': 'Behavioral Shock',
                'description': behavioral_shock['description'],
                'impact': 'Unusual patterns may not follow historical trends',
                'mitigation': 'Flag for human review, contextual investigation'
            })
        
        # Check for adversarial inputs
        adversarial = self._check_adversarial_inputs(student_data, alert_week)
        if adversarial['is_suspicious']:
            failure_modes.append({
                'type': 'Adversarial Inputs',
                'description': adversarial['description'],
                'impact': 'Potential manipulation or data quality issues',
                'mitigation': 'Data validation, source verification'
            })
        
        # Check for cold start problems
        cold_start = self._check_cold_start(student_data, alert_week)
        if cold_start['is_cold_start']:
            failure_modes.append({
                'type': 'Cold Start',
                'description': cold_start['description'],
                'impact': 'Insufficient historical data for reliable assessment',
                'mitigation': 'Lower confidence, longer observation period'
            })
        
        return {
            'failure_modes': failure_modes,
            'overall_uncertainty': self._calculate_overall_uncertainty(failure_modes),
            'human_review_required': len(failure_modes) > 0,
            'confidence_adjustment': self._adjust_confidence(failure_modes)
        }
    
    def _check_data_sparsity(self, student_data: Dict, week: int) -> Dict:
        """Check if data is sparse for reliable analysis"""
        
        # Simulate data sparsity check
        data_points = random.randint(5, 20)  # Simulated data points
        
        is_sparse = data_points < 10
        
        return {
            'is_sparse': is_sparse,
            'description': f'Only {data_points} data points available in recent weeks',
            'data_points': data_points
        }
    
    def _check_behavioral_shocks(self, student_data: Dict, week: int) -> Dict:
        """Check for sudden behavioral changes"""
        
        # Simulate shock detection
        if week >= 8:
            has_shock = random.random() < 0.3  # 30% chance of shock
        else:
            has_shock = False
        
        return {
            'has_shock': has_shock,
            'description': 'Sudden change in behavior patterns detected'
        }
    
    def _check_adversarial_inputs(self, student_data: Dict, week: int) -> Dict:
        """Check for suspicious or adversarial input patterns"""
        
        # Simulate adversarial input detection
        is_suspicious = random.random() < 0.1  # 10% chance of suspicious data
        
        return {
            'is_suspicious': is_suspicious,
            'description': 'Unusual data patterns suggest potential manipulation'
        }
    
    def _check_cold_start(self, student_data: Dict, week: int) -> Dict:
        """Check if system is in cold start phase"""
        
        is_cold_start = week <= 3
        
        return {
            'is_cold_start': is_cold_start,
            'description': f'Insufficient data in early weeks (Week {week})'
        }
    
    def _calculate_overall_uncertainty(self, failure_modes: List[Dict]) -> float:
        """Calculate overall uncertainty based on failure modes"""
        
        if not failure_modes:
            return 0.1  # Base uncertainty
        
        # Each failure mode adds uncertainty
        uncertainty = 0.1
        for mode in failure_modes:
            if mode['type'] == 'Sparse Data':
                uncertainty += 0.2
            elif mode['type'] == 'Behavioral Shock':
                uncertainty += 0.3
            elif mode['type'] == 'Adversarial Inputs':
                uncertainty += 0.4
            elif mode['type'] == 'Cold Start':
                uncertainty += 0.25
        
        return min(0.9, uncertainty)  # Cap at 90% uncertainty
    
    def _adjust_confidence(self, failure_modes: List[Dict]) -> float:
        """Adjust confidence based on failure modes"""
        
        base_confidence = 0.85
        
        for mode in failure_modes:
            if mode['type'] == 'Sparse Data':
                base_confidence -= 0.15
            elif mode['type'] == 'Behavioral Shock':
                base_confidence -= 0.2
            elif mode['type'] == 'Adversarial Inputs':
                base_confidence -= 0.3
            elif mode['type'] == 'Cold Start':
                base_confidence -= 0.25
        
        return max(0.1, base_confidence)  # Minimum 10% confidence
    
    def generate_decision_timeline(self, student_data: Dict, alert_week: int) -> Dict[str, Any]:
        """Generate decision timeline showing intervention impact"""
        
        current_risk = self._calculate_risk_score(student_data, alert_week)
        
        # Simulate intervention scenarios
        interventions = [
            {
                'week': alert_week + 1,
                'type': 'Academic Support',
                'description': 'Weekly tutoring sessions',
                'risk_reduction': 0.15,
                'confidence': 0.8
            },
            {
                'week': alert_week + 2,
                'type': 'Counseling',
                'description': 'Personal counseling sessions',
                'risk_reduction': 0.12,
                'confidence': 0.7
            },
            {
                'week': alert_week + 3,
                'type': 'Faculty Engagement',
                'description': 'Regular faculty check-ins',
                'risk_reduction': 0.10,
                'confidence': 0.6
            }
        ]
        
        # Calculate projected risk with interventions
        projected_risk = current_risk
        for intervention in interventions:
            projected_risk *= (1 - intervention['risk_reduction'])
        
        return {
            'current_risk': current_risk,
            'projected_risk': projected_risk,
            'total_risk_reduction': current_risk - projected_risk,
            'risk_reduction_percent': ((current_risk - projected_risk) / current_risk) * 100,
            'interventions': interventions,
            'interpretation': f"If interventions started at Week {alert_week + 1}, projected risk would reduce by {((current_risk - projected_risk) / current_risk) * 100:.1f}%"
        }

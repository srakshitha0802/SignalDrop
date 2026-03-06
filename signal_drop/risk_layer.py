"""
Risk Scoring Layer - Risk Momentum Calculation and Tracking

Generates risk momentum scores, tracks temporal changes, and
provides confidence estimation for early-warning alerts.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import IsolationForest
import logging

logger = logging.getLogger(__name__)

class RiskScorer:
    """Calculates risk momentum scores and tracks temporal changes."""
    
    def __init__(self, momentum_window: int = 14, anomaly_contamination: float = 0.1):
        self.momentum_window = momentum_window  # days for momentum calculation
        self.anomaly_contamination = anomaly_contamination
        self.risk_history = {}  # Store historical risk scores
        self.scalers = {}
        self.anomaly_detectors = {}
        
        # Risk component weights
        self.risk_weights = {
            'engagement_decay': 0.25,
            'academic_decline': 0.20,
            'communication_shift': 0.20,
            'attendance_decline': 0.15,
            'temporal_drift': 0.10,
            'narrative_shift': 0.10
        }
    
    def calculate_risk_momentum(self, student_id: str, student_profile: Dict,
                              temporal_embeddings: Dict, narrative_analysis: Dict,
                              temporal_drift: Dict) -> Dict[str, Any]:
        """Calculate comprehensive risk momentum score for a student."""
        
        # Calculate individual risk components
        risk_components = self._calculate_risk_components(
            student_profile, temporal_embeddings, narrative_analysis, temporal_drift
        )
        
        # Calculate weighted risk score
        risk_score = self._calculate_weighted_risk_score(risk_components)
        
        # Calculate momentum (change over time)
        momentum = self._calculate_momentum(student_id, risk_score)
        
        # Determine confidence level
        confidence = self._calculate_confidence(risk_components, temporal_drift)
        
        # Store in history
        self._update_risk_history(student_id, risk_score, momentum, risk_components)
        
        return {
            "student_id": student_id,
            "risk_score": risk_score,
            "risk_momentum": momentum,
            "confidence": confidence,
            "risk_components": risk_components,
            "risk_level": self._determine_risk_level(risk_score, momentum),
            "timestamp": datetime.now()
        }
    
    def _calculate_risk_components(self, student_profile: Dict, temporal_embeddings: Dict,
                                 narrative_analysis: Dict, temporal_drift: Dict) -> Dict[str, float]:
        """Calculate individual risk components."""
        
        components = {}
        
        # Engagement decay component
        components['engagement_decay'] = self._calculate_engagement_decay_risk(student_profile)
        
        # Academic decline component
        components['academic_decline'] = self._calculate_academic_decline_risk(student_profile)
        
        # Communication shift component
        components['communication_shift'] = self._calculate_communication_shift_risk(student_profile)
        
        # Attendance decline component
        components['attendance_decline'] = self._calculate_attendance_decline_risk(student_profile)
        
        # Temporal drift component
        components['temporal_drift'] = self._calculate_temporal_drift_risk(temporal_drift)
        
        # Narrative shift component
        components['narrative_shift'] = self._calculate_narrative_shift_risk(narrative_analysis)
        
        return components
    
    def _calculate_engagement_decay_risk(self, student_profile: Dict) -> float:
        """Calculate engagement decay risk component."""
        
        lms_data = student_profile.get('lms_activity', {})
        if not lms_data:
            return 0.5  # Neutral risk for missing data
        
        risk_factors = []
        
        # Activity frequency decline
        activity_7d = lms_data.get('activity_frequency_7d', 0)
        activity_14d = lms_data.get('activity_frequency_14d', 0)
        activity_30d = lms_data.get('activity_frequency_30d', 0)
        
        if activity_14d > 0:
            decay_7_14 = 1 - (activity_7d / activity_14d)
            risk_factors.append(decay_7_14)
        
        if activity_30d > 0:
            decay_14_30 = 1 - (activity_14d / activity_30d)
            risk_factors.append(decay_14_30)
        
        # Session gap increase
        avg_gap = lms_data.get('avg_session_gap_hours', 0)
        if avg_gap > 48:  # More than 2 days between sessions
            gap_risk = min(avg_gap / 168, 1.0)  # Normalize by week
            risk_factors.append(gap_risk)
        
        # Low recent activity
        if activity_7d <= 1:
            risk_factors.append(0.8)
        elif activity_7d <= 3:
            risk_factors.append(0.4)
        
        return np.mean(risk_factors) if risk_factors else 0.0
    
    def _calculate_academic_decline_risk(self, student_profile: Dict) -> float:
        """Calculate academic decline risk component."""
        
        assign_data = student_profile.get('assignments', {})
        if not assign_data:
            return 0.5
        
        risk_factors = []
        
        # Late submission rate
        late_rate = assign_data.get('late_submission_rate', 0)
        recent_late_rate = assign_data.get('recent_late_rate', 0)
        
        risk_factors.append(late_rate)
        
        # Recent increase in late submissions
        if recent_late_rate > late_rate + 0.1:
            risk_factors.append(0.7)
        
        # Assignment quality indicators
        avg_text_length = assign_data.get('avg_text_length', 0)
        if avg_text_length < 50:  # Very short submissions
            risk_factors.append(0.6)
        elif avg_text_length < 100:
            risk_factors.append(0.3)
        
        # Average delay
        avg_delay = assign_data.get('avg_delay_hours', 0)
        if avg_delay > 72:  # More than 3 days late on average
            delay_risk = min(avg_delay / 168, 1.0)  # Normalize by week
            risk_factors.append(delay_risk)
        
        return np.mean(risk_factors) if risk_factors else 0.0
    
    def _calculate_communication_shift_risk(self, student_profile: Dict) -> float:
        """Calculate communication shift risk component."""
        
        msg_data = student_profile.get('messages', {})
        if not msg_data:
            return 0.3  # Slightly elevated risk for no communication data
        
        risk_factors = []
        
        # Sentiment decline
        if msg_data.get('recent_sentiment_decline', False):
            risk_factors.append(0.7)
        
        # Low sentiment ratio
        sentiment_ratio = msg_data.get('avg_sentiment_ratio', 1)
        if sentiment_ratio < 0.5:
            risk_factors.append(0.8)
        elif sentiment_ratio < 0.7:
            risk_factors.append(0.4)
        
        # Negative sentiment indicators
        total_messages = msg_data.get('total_messages', 1)
        negative_ratio = msg_data.get('negative_sentiment_total', 0) / total_messages
        if negative_ratio > 0.3:
            risk_factors.append(0.6)
        elif negative_ratio > 0.15:
            risk_factors.append(0.3)
        
        # Communication frequency
        if total_messages == 0:
            risk_factors.append(0.5)
        elif total_messages < 5:  # Very low communication
            risk_factors.append(0.3)
        
        return np.mean(risk_factors) if risk_factors else 0.0
    
    def _calculate_attendance_decline_risk(self, student_profile: Dict) -> float:
        """Calculate attendance decline risk component."""
        
        att_data = student_profile.get('attendance', {})
        if not att_data:
            return 0.5
        
        risk_factors = []
        
        # Overall attendance rate
        attendance_rate = att_data.get('attendance_rate', 1)
        if attendance_rate < 0.7:
            risk_factors.append(0.8)
        elif attendance_rate < 0.85:
            risk_factors.append(0.4)
        
        # Recent attendance decline
        recent_rate = att_data.get('recent_attendance_rate', attendance_rate)
        if recent_rate < attendance_rate - 0.15:
            risk_factors.append(0.7)
        
        # Absent rate
        absent_rate = att_data.get('absent_rate', 0)
        if absent_rate > 0.2:
            risk_factors.append(0.6)
        elif absent_rate > 0.1:
            risk_factors.append(0.3)
        
        # Late rate
        late_rate = att_data.get('late_rate', 0)
        if late_rate > 0.15:
            risk_factors.append(0.4)
        
        return np.mean(risk_factors) if risk_factors else 0.0
    
    def _calculate_temporal_drift_risk(self, temporal_drift: Dict) -> float:
        """Calculate temporal drift risk component."""
        
        if not temporal_drift:
            return 0.0
        
        drift_score = temporal_drift.get('drift_score', 0.0)
        
        # Amplify drift score for risk assessment
        return min(drift_score * 1.5, 1.0)
    
    def _calculate_narrative_shift_risk(self, narrative_analysis: Dict) -> float:
        """Calculate narrative shift risk component."""
        
        if not narrative_analysis:
            return 0.0
        
        risk_factors = []
        
        # Trajectory-based risk
        trajectory = narrative_analysis.get('engagement_trajectory', 'stable')
        trajectory_risk = {
            'declining': 0.8,
            'volatile': 0.6,
            'stable': 0.2,
            'improving': 0.1
        }
        risk_factors.append(trajectory_risk.get(trajectory, 0.3))
        
        # Risk indicators count
        risk_indicators = narrative_analysis.get('risk_indicators', [])
        indicator_risk = min(len(risk_indicators) * 0.2, 1.0)
        risk_factors.append(indicator_risk)
        
        # Confidence inverse (lower confidence = higher risk)
        confidence = narrative_analysis.get('confidence_score', 0.5)
        confidence_risk = 1 - confidence
        risk_factors.append(confidence_risk * 0.5)  # Weight this less
        
        return np.mean(risk_factors) if risk_factors else 0.0
    
    def _calculate_weighted_risk_score(self, risk_components: Dict[str, float]) -> float:
        """Calculate weighted risk score from components."""
        
        total_score = 0.0
        total_weight = 0.0
        
        for component, score in risk_components.items():
            if component in self.risk_weights:
                weight = self.risk_weights[component]
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_momentum(self, student_id: str, current_risk_score: float) -> str:
        """Calculate risk momentum (change over time)."""
        
        if student_id not in self.risk_history:
            return "stable"
        
        history = self.risk_history[student_id]
        if len(history) < 2:
            return "stable"
        
        # Get recent scores
        recent_scores = [entry['risk_score'] for entry in list(history)[-self.momentum_window:]]
        
        if len(recent_scores) < 2:
            return "stable"
        
        # Calculate trend
        x = np.arange(len(recent_scores))
        slope = np.polyfit(x, recent_scores, 1)[0]
        
        # Determine momentum
        if slope > 0.02:  # Increasing risk
            return "increasing"
        elif slope < -0.02:  # Decreasing risk
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_confidence(self, risk_components: Dict[str, float], 
                            temporal_drift: Dict) -> str:
        """Calculate confidence level for risk assessment."""
        
        # Base confidence on data completeness
        component_count = len([v for v in risk_components.values() if v > 0])
        max_components = len(self.risk_weights)
        data_completeness = component_count / max_components
        
        # Adjust for temporal drift detection
        drift_confidence = 1.0
        if temporal_drift:
            drift_confidence = temporal_drift.get('drift_score', 0.0)
        
        # Calculate overall confidence
        overall_confidence = (data_completeness + drift_confidence) / 2
        
        # Convert to confidence level
        if overall_confidence > 0.7:
            return "high"
        elif overall_confidence > 0.4:
            return "medium"
        else:
            return "low"
    
    def _determine_risk_level(self, risk_score: float, momentum: str) -> str:
        """Determine overall risk level."""
        
        # Adjust risk score based on momentum
        adjusted_score = risk_score
        if momentum == "increasing":
            adjusted_score = min(risk_score + 0.1, 1.0)
        elif momentum == "decreasing":
            adjusted_score = max(risk_score - 0.1, 0.0)
        
        if adjusted_score > 0.7:
            return "high"
        elif adjusted_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _update_risk_history(self, student_id: str, risk_score: float, 
                           momentum: str, risk_components: Dict[str, float]):
        """Update risk history for momentum tracking."""
        
        if student_id not in self.risk_history:
            self.risk_history[student_id] = []
        
        entry = {
            'timestamp': datetime.now(),
            'risk_score': risk_score,
            'momentum': momentum,
            'risk_components': risk_components
        }
        
        self.risk_history[student_id].append(entry)
        
        # Keep only recent history (last 90 days)
        cutoff_date = datetime.now() - timedelta(days=90)
        self.risk_history[student_id] = [
            entry for entry in self.risk_history[student_id] 
            if entry['timestamp'] > cutoff_date
        ]
    
    def detect_anomalies(self, student_profiles: Dict[str, Dict]) -> Dict[str, Dict]:
        """Detect anomalous behavior patterns across students."""
        
        # Prepare feature matrix
        features = []
        student_ids = []
        
        for student_id, profile in student_profiles.items():
            feature_vector = self._extract_anomaly_features(profile)
            features.append(feature_vector)
            student_ids.append(student_id)
        
        if not features:
            return {}
        
        features = np.array(features)
        
        # Fit anomaly detector
        detector = IsolationForest(contamination=self.anomaly_contamination, random_state=42)
        anomaly_labels = detector.fit_predict(features)
        anomaly_scores = detector.decision_function(features)
        
        # Compile results
        anomalies = {}
        for i, (student_id, label, score) in enumerate(zip(student_ids, anomaly_labels, anomaly_scores)):
            if label == -1:  # Anomaly detected
                anomalies[student_id] = {
                    'anomaly_score': float(score),
                    'severity': 'high' if score < -0.5 else 'medium',
                    'features': dict(zip(self._get_anomaly_feature_names(), features[i]))
                }
        
        return anomalies
    
    def _extract_anomaly_features(self, student_profile: Dict) -> List[float]:
        """Extract features for anomaly detection."""
        
        features = []
        
        # LMS features
        lms_data = student_profile.get('lms_activity', {})
        features.extend([
            lms_data.get('activity_frequency_7d', 0),
            lms_data.get('activity_frequency_14d', 0),
            lms_data.get('avg_session_gap_hours', 0)
        ])
        
        # Assignment features
        assign_data = student_profile.get('assignments', {})
        features.extend([
            assign_data.get('late_submission_rate', 0),
            assign_data.get('avg_delay_hours', 0),
            assign_data.get('avg_text_length', 0)
        ])
        
        # Message features
        msg_data = student_profile.get('messages', {})
        features.extend([
            msg_data.get('total_messages', 0),
            msg_data.get('avg_sentiment_ratio', 1),
            msg_data.get('negative_sentiment_total', 0)
        ])
        
        # Attendance features
        att_data = student_profile.get('attendance', {})
        features.extend([
            att_data.get('attendance_rate', 1),
            att_data.get('absent_rate', 0),
            att_data.get('late_rate', 0)
        ])
        
        return features
    
    def _get_anomaly_feature_names(self) -> List[str]:
        """Get feature names for anomaly detection."""
        return [
            'lms_activity_7d', 'lms_activity_14d', 'lms_avg_gap',
            'assign_late_rate', 'assign_avg_delay', 'assign_text_length',
            'msg_total', 'msg_sentiment_ratio', 'msg_negative_total',
            'att_rate', 'att_absent_rate', 'att_late_rate'
        ]
    
    def get_risk_timeline(self, student_id: str, days: int = 30) -> List[Dict]:
        """Get risk timeline for a student."""
        
        if student_id not in self.risk_history:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_history = [
            entry for entry in self.risk_history[student_id]
            if entry['timestamp'] > cutoff_date
        ]
        
        return [
            {
                'date': entry['timestamp'].strftime('%Y-%m-%d'),
                'risk_score': entry['risk_score'],
                'momentum': entry['momentum']
            }
            for entry in recent_history
        ]

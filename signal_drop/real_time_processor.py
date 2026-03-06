"""
Real-Time Processor for SignalDrop AI

Advanced real-time processing capabilities:
- Streaming data processing with Apache Kafka-style architecture
- Real-time risk scoring with sliding windows
- Adaptive thresholding with concept drift detection
- Incremental learning and model updates
- Real-time alert generation with prioritization
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator
from datetime import datetime, timedelta
from collections import deque, defaultdict
import logging
import json
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time

logger = logging.getLogger(__name__)

class AlertPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class DataSource(Enum):
    LMS_ACTIVITY = "lms_activity"
    ASSIGNMENTS = "assignments"
    MESSAGES = "messages"
    ATTENDANCE = "attendance"

@dataclass
class DataEvent:
    """Real-time data event."""
    student_id: str
    source: DataSource
    timestamp: datetime
    data: Dict[str, Any]
    event_id: str = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = f"{self.student_id}_{self.source.value}_{int(self.timestamp.timestamp())}"

@dataclass
class RiskAlert:
    """Real-time risk alert."""
    student_id: str
    risk_score: float
    risk_level: str
    priority: AlertPriority
    timestamp: datetime
    explanation: str
    key_signals: List[str]
    confidence: float
    alert_id: str = None
    
    def __post_init__(self):
        if self.alert_id is None:
            self.alert_id = f"alert_{self.student_id}_{int(self.timestamp.timestamp())}"

class ConceptDriftDetector:
    """Detects concept drift in real-time data streams."""
    
    def __init__(self, window_size: int = 1000, drift_threshold: float = 0.1):
        self.window_size = window_size
        self.drift_threshold = drift_threshold
        self.reference_window = deque(maxlen=window_size)
        self.current_window = deque(maxlen=window_size)
        self.drift_detected = False
        self.drift_history = []
        
    def add_sample(self, features: np.ndarray, prediction: float):
        """Add new sample for drift detection."""
        sample = {
            'features': features,
            'prediction': prediction,
            'timestamp': datetime.now()
        }
        
        self.current_window.append(sample)
        
        # Check for drift when windows are full
        if len(self.current_window) == self.window_size:
            self._check_drift()
    
    def _check_drift(self):
        """Check for concept drift between windows."""
        if len(self.reference_window) == 0:
            # First window becomes reference
            self.reference_window = deque(self.current_window, maxlen=self.window_size)
            return
        
        # Calculate distribution differences
        ref_predictions = [s['prediction'] for s in self.reference_window]
        curr_predictions = [s['prediction'] for s in self.current_window]
        
        # Simple drift detection based on prediction distribution
        ref_mean = np.mean(ref_predictions)
        curr_mean = np.mean(curr_predictions)
        
        drift_magnitude = abs(ref_mean - curr_mean)
        
        if drift_magnitude > self.drift_threshold:
            self.drift_detected = True
            self.drift_history.append({
                'timestamp': datetime.now(),
                'drift_magnitude': drift_magnitude,
                'ref_mean': ref_mean,
                'curr_mean': curr_mean
            })
            
            # Update reference window
            self.reference_window = deque(self.current_window, maxlen=self.window_size)
            
            logger.warning(f"Concept drift detected: magnitude={drift_magnitude:.3f}")
    
    def is_drift_detected(self) -> bool:
        """Check if drift was recently detected."""
        return self.drift_detected
    
    def reset_drift_flag(self):
        """Reset drift detection flag."""
        self.drift_detected = False

class SlidingWindowProcessor:
    """Sliding window processor for real-time feature extraction."""
    
    def __init__(self, window_sizes: List[int] = [7, 14, 30]):
        self.window_sizes = sorted(window_sizes)
        self.data_windows = defaultdict(lambda: defaultdict(deque))
        
    def add_event(self, event: DataEvent):
        """Add event to sliding windows."""
        student_id = event.student_id
        source = event.source
        
        # Add to all relevant windows
        for window_size in self.window_sizes:
            window_key = f"{source}_{window_size}d"
            self.data_windows[student_id][window_key].append(event)
            
            # Remove old events outside window
            cutoff_time = datetime.now() - timedelta(days=window_size)
            while (self.data_windows[student_id][window_key] and 
                   self.data_windows[student_id][window_key][0].timestamp < cutoff_time):
                self.data_windows[student_id][window_key].popleft()
    
    def get_window_features(self, student_id: str, source: DataSource, 
                          window_size: int) -> Dict[str, Any]:
        """Extract features from sliding window."""
        window_key = f"{source}_{window_size}d"
        
        if student_id not in self.data_windows or window_key not in self.data_windows[student_id]:
            return {}
        
        events = list(self.data_windows[student_id][window_key])
        
        if not events:
            return {}
        
        # Extract features based on source type
        if source == DataSource.LMS_ACTIVITY:
            return self._extract_lms_features(events)
        elif source == DataSource.ASSIGNMENTS:
            return self._extract_assignment_features(events)
        elif source == DataSource.MESSAGES:
            return self._extract_message_features(events)
        elif source == DataSource.ATTENDANCE:
            return self._extract_attendance_features(events)
        
        return {}
    
    def _extract_lms_features(self, events: List[DataEvent]) -> Dict[str, Any]:
        """Extract LMS activity features."""
        if not events:
            return {}
        
        # Aggregate metrics
        login_counts = [e.data.get('login_count', 0) for e in events]
        content_views = [e.data.get('content_views', 0) for e in events]
        session_durations = [e.data.get('avg_session_duration_minutes', 0) for e in events]
        
        features = {
            'total_logins': sum(login_counts),
            'avg_logins_per_day': np.mean(login_counts),
            'total_content_views': sum(content_views),
            'avg_content_views_per_day': np.mean(content_views),
            'avg_session_duration': np.mean(session_durations),
            'total_sessions': len(events),
            'last_activity': max(e.timestamp for e in events).isoformat(),
            'activity_frequency': len(events) / max(1, (max(e.timestamp for e in events) - min(e.timestamp for e in events)).days)
        }
        
        return features
    
    def _extract_assignment_features(self, events: List[DataEvent]) -> Dict[str, Any]:
        """Extract assignment features."""
        if not events:
            return {}
        
        submitted = [e for e in events if e.data.get('assignment_submitted') == 'yes']
        delays = [e.data.get('submission_delay_days', 0) for e in submitted if e.data.get('submission_delay_days') is not None]
        
        features = {
            'total_assignments': len(events),
            'submitted_assignments': len(submitted),
            'submission_rate': len(submitted) / len(events) if events else 0,
            'avg_delay_days': np.mean(delays) if delays else 0,
            'max_delay_days': max(delays) if delays else 0,
            'last_submission': max(e.timestamp for e in submitted).isoformat() if submitted else None
        }
        
        return features
    
    def _extract_message_features(self, events: List[DataEvent]) -> Dict[str, Any]:
        """Extract message features."""
        if not events:
            return {}
        
        message_lengths = [len(e.data.get('message_text', '')) for e in events]
        
        features = {
            'total_messages': len(events),
            'avg_message_length': np.mean(message_lengths),
            'messages_per_day': len(events) / max(1, (max(e.timestamp for e in events) - min(e.timestamp for e in events)).days),
            'last_message': max(e.timestamp for e in events).isoformat()
        }
        
        return features
    
    def _extract_attendance_features(self, events: List[DataEvent]) -> Dict[str, Any]:
        """Extract attendance features."""
        if not events:
            return {}
        
        attendance_rates = [e.data.get('attendance_percentage', 0) for e in events]
        
        features = {
            'total_days': len(events),
            'avg_attendance_rate': np.mean(attendance_rates),
            'min_attendance_rate': min(attendance_rates),
            'max_attendance_rate': max(attendance_rates),
            'last_attendance': max(e.timestamp for e in events).isoformat()
        }
        
        return features

class AdaptiveThresholdManager:
    """Manages adaptive thresholds for real-time alerting."""
    
    def __init__(self, initial_threshold: float = 0.5, adaptation_rate: float = 0.1):
        self.initial_threshold = initial_threshold
        self.current_threshold = initial_threshold
        self.adaptation_rate = adaptation_rate
        self.threshold_history = []
        self.false_positive_rate = 0.0
        self.true_positive_rate = 0.0
        
    def update_threshold(self, predicted_risks: List[float], 
                        actual_outcomes: Optional[List[bool]] = None):
        """Update threshold based on performance feedback."""
        
        if actual_outcomes is None:
            return
        
        # Calculate current performance metrics
        predictions = [risk > self.current_threshold for risk in predicted_risks]
        
        if len(actual_outcomes) != len(predictions):
            return
        
        # Calculate TPR and FPR
        tp = sum(1 for p, a in zip(predictions, actual_outcomes) if p and a)
        fp = sum(1 for p, a in zip(predictions, actual_outcomes) if p and not a)
        fn = sum(1 for p, a in zip(predictions, actual_outcomes) if not p and a)
        tn = sum(1 for p, a in zip(predictions, actual_outcomes) if not p and not a)
        
        self.true_positive_rate = tp / (tp + fn) if (tp + fn) > 0 else 0
        self.false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        # Adaptive threshold adjustment
        if self.false_positive_rate > 0.3:  # Too many false positives
            self.current_threshold += self.adaptation_rate
        elif self.true_positive_rate < 0.7:  # Missing too many true cases
            self.current_threshold -= self.adaptation_rate
        
        # Keep threshold in reasonable range
        self.current_threshold = max(0.1, min(0.9, self.current_threshold))
        
        self.threshold_history.append({
            'timestamp': datetime.now(),
            'threshold': self.current_threshold,
            'tpr': self.true_positive_rate,
            'fpr': self.false_positive_rate
        })
    
    def get_threshold(self) -> float:
        """Get current adaptive threshold."""
        return self.current_threshold
    
    def should_alert(self, risk_score: float) -> bool:
        """Determine if alert should be generated."""
        return risk_score > self.current_threshold

class RealTimeProcessor:
    """Main real-time processor for SignalDrop AI."""
    
    def __init__(self, alert_callback: Optional[Callable[[RiskAlert], None]] = None):
        self.alert_callback = alert_callback
        self.is_running = False
        
        # Components
        self.sliding_window = SlidingWindowProcessor()
        self.drift_detector = ConceptDriftDetector()
        self.threshold_manager = AdaptiveThresholdManager()
        
        # Data storage
        self.event_buffer = deque(maxlen=10000)
        self.alert_buffer = deque(maxlen=1000)
        self.student_profiles = defaultdict(dict)
        
        # Processing threads
        self.processing_thread = None
        self.alert_thread = None
        
        # Statistics
        self.stats = {
            'events_processed': 0,
            'alerts_generated': 0,
            'processing_time_avg': 0.0,
            'last_update': datetime.now()
        }
        
    async def start_processing(self):
        """Start real-time processing."""
        if self.is_running:
            logger.warning("Real-time processor already running")
            return
        
        self.is_running = True
        logger.info("Starting real-time processor")
        
        # Start processing threads
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.alert_thread = threading.Thread(target=self._alert_loop, daemon=True)
        
        self.processing_thread.start()
        self.alert_thread.start()
    
    def stop_processing(self):
        """Stop real-time processing."""
        self.is_running = False
        logger.info("Stopping real-time processor")
        
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        if self.alert_thread:
            self.alert_thread.join(timeout=5)
    
    def add_event(self, event: DataEvent):
        """Add new event to processing queue."""
        self.event_buffer.append(event)
        self.stats['events_processed'] += 1
    
    def _processing_loop(self):
        """Main processing loop for events."""
        while self.is_running:
            try:
                # Process events from buffer
                while self.event_buffer and self.is_running:
                    event = self.event_buffer.popleft()
                    self._process_event(event)
                
                # Small delay to prevent CPU spinning
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
    
    def _process_event(self, event: DataEvent):
        """Process individual event."""
        start_time = time.time()
        
        # Add to sliding window
        self.sliding_window.add_event(event)
        
        # Update student profile
        self._update_student_profile(event)
        
        # Check for concept drift
        features = self._extract_event_features(event)
        if features is not None:
            # Simple risk prediction for drift detection
            risk_score = self._quick_risk_assessment(event.student_id, features)
            self.drift_detector.add_sample(features, risk_score)
        
        # Update processing statistics
        processing_time = time.time() - start_time
        self.stats['processing_time_avg'] = (
            self.stats['processing_time_avg'] * 0.9 + processing_time * 0.1
        )
        self.stats['last_update'] = datetime.now()
    
    def _update_student_profile(self, event: DataEvent):
        """Update student profile with new event."""
        student_id = event.student_id
        source = event.source
        
        if source not in self.student_profiles[student_id]:
            self.student_profiles[student_id][source] = {
                'events': [],
                'last_update': None
            }
        
        self.student_profiles[student_id][source]['events'].append(event)
        self.student_profiles[student_id][source]['last_update'] = event.timestamp
    
    def _extract_event_features(self, event: DataEvent) -> Optional[np.ndarray]:
        """Extract features from event for drift detection."""
        try:
            # Simple feature extraction based on event type
            if event.source == DataSource.LMS_ACTIVITY:
                features = np.array([
                    event.data.get('login_count', 0),
                    event.data.get('content_views', 0),
                    event.data.get('avg_session_duration_minutes', 0)
                ])
            elif event.source == DataSource.ASSIGNMENTS:
                features = np.array([
                    1.0 if event.data.get('assignment_submitted') == 'yes' else 0.0,
                    event.data.get('submission_delay_days', 0),
                    len(event.data.get('short_text_submission', ''))
                ])
            elif event.source == DataSource.MESSAGES:
                features = np.array([
                    len(event.data.get('message_text', '')),
                    1.0  # Placeholder for sentiment
                ])
            elif event.source == DataSource.ATTENDANCE:
                features = np.array([
                    event.data.get('attendance_percentage', 0)
                ])
            else:
                return None
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None
    
    def _quick_risk_assessment(self, student_id: str, features: np.ndarray) -> float:
        """Quick risk assessment for drift detection."""
        # Simplified risk assessment
        # In practice, would use trained model
        
        # Get recent features from sliding window
        recent_features = []
        for source in DataSource:
            for window_size in [7, 14]:  # Check recent windows
                window_features = self.sliding_window.get_window_features(
                    student_id, source, window_size
                )
                if window_features:
                    # Convert to numeric features
                    numeric_features = []
                    for key, value in window_features.items():
                        if isinstance(value, (int, float)):
                            numeric_features.append(value)
                    if numeric_features:
                        recent_features.extend(numeric_features)
        
        if recent_features:
            # Simple risk calculation
            risk_score = np.mean(recent_features) / 100.0  # Normalize
            return np.clip(risk_score, 0.0, 1.0)
        
        return 0.1  # Default low risk
    
    def _alert_loop(self):
        """Alert generation loop."""
        while self.is_running:
            try:
                # Check for students needing alerts
                self._check_for_alerts()
                
                # Small delay
                time.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in alert loop: {e}")
    
    def _check_for_alerts(self):
        """Check for students requiring alerts."""
        current_time = datetime.now()
        
        # Check each student with recent activity
        for student_id in list(self.student_profiles.keys()):
            # Get comprehensive risk assessment
            risk_assessment = self._comprehensive_risk_assessment(student_id)
            
            if risk_assessment and self.threshold_manager.should_alert(risk_assessment['risk_score']):
                # Generate alert
                alert = self._generate_alert(student_id, risk_assessment, current_time)
                
                # Add to alert buffer
                self.alert_buffer.append(alert)
                self.stats['alerts_generated'] += 1
                
                # Call alert callback
                if self.alert_callback:
                    self.alert_callback(alert)
    
    def _comprehensive_risk_assessment(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Comprehensive risk assessment for student."""
        try:
            # Collect features from all sources and windows
            all_features = {}
            
            for source in DataSource:
                for window_size in [7, 14, 30]:
                    features = self.sliding_window.get_window_features(
                        student_id, source, window_size
                    )
                    if features:
                        key = f"{source.value}_{window_size}d"
                        all_features[key] = features
            
            if not all_features:
                return None
            
            # Calculate risk score (simplified)
            risk_factors = []
            
            # LMS activity risk
            lms_features = all_features.get('lms_activity_7d', {})
            if lms_features:
                activity_risk = 1.0 - (lms_features.get('activity_frequency', 0) / 10.0)
                risk_factors.append(activity_risk)
            
            # Assignment risk
            assign_features = all_features.get('assignments_14d', {})
            if assign_features:
                submission_risk = 1.0 - assign_features.get('submission_rate', 1.0)
                risk_factors.append(submission_risk)
            
            # Attendance risk
            att_features = all_features.get('attendance_30d', {})
            if att_features:
                attendance_risk = 1.0 - (att_features.get('avg_attendance_rate', 100.0) / 100.0)
                risk_factors.append(attendance_risk)
            
            # Overall risk score
            risk_score = np.mean(risk_factors) if risk_factors else 0.1
            
            return {
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'features': all_features,
                'assessment_time': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error in risk assessment for {student_id}: {e}")
            return None
    
    def _generate_alert(self, student_id: str, risk_assessment: Dict[str, Any], 
                       timestamp: datetime) -> RiskAlert:
        """Generate risk alert."""
        
        risk_score = risk_assessment['risk_score']
        
        # Determine risk level and priority
        if risk_score > 0.8:
            risk_level = "critical"
            priority = AlertPriority.CRITICAL
        elif risk_score > 0.6:
            risk_level = "high"
            priority = AlertPriority.HIGH
        elif risk_score > 0.4:
            risk_level = "medium"
            priority = AlertPriority.MEDIUM
        else:
            risk_level = "low"
            priority = AlertPriority.LOW
        
        # Generate explanation
        explanation = self._generate_alert_explanation(student_id, risk_assessment)
        
        # Identify key signals
        key_signals = self._identify_key_signals(risk_assessment)
        
        # Calculate confidence
        confidence = self._calculate_alert_confidence(risk_assessment)
        
        alert = RiskAlert(
            student_id=student_id,
            risk_score=risk_score,
            risk_level=risk_level,
            priority=priority,
            timestamp=timestamp,
            explanation=explanation,
            key_signals=key_signals,
            confidence=confidence
        )
        
        return alert
    
    def _generate_alert_explanation(self, student_id: str, 
                                   risk_assessment: Dict[str, Any]) -> str:
        """Generate explanation for alert."""
        
        risk_score = risk_assessment['risk_score']
        features = risk_assessment.get('features', {})
        
        explanation_parts = [f"Student {student_id} shows elevated risk (score: {risk_score:.2f})"]
        
        # Add specific indicators
        lms_features = features.get('lms_activity_7d', {})
        if lms_features.get('activity_frequency', 0) < 2:
            explanation_parts.append("Low recent LMS activity")
        
        assign_features = features.get('assignments_14d', {})
        if assign_features.get('submission_rate', 1.0) < 0.7:
            explanation_parts.append("Low assignment submission rate")
        
        att_features = features.get('attendance_30d', {})
        if att_features.get('avg_attendance_rate', 100) < 80:
            explanation_parts.append("Declining attendance pattern")
        
        return ". ".join(explanation_parts) + "."
    
    def _identify_key_signals(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Identify key risk signals."""
        signals = []
        features = risk_assessment.get('features', {})
        
        # Check each source for concerning patterns
        if 'lms_activity_7d' in features:
            lms_feat = features['lms_activity_7d']
            if lms_feat.get('activity_frequency', 0) < 2:
                signals.append("Low LMS activity (7-day window)")
        
        if 'assignments_14d' in features:
            assign_feat = features['assignments_14d']
            if assign_feat.get('submission_rate', 1.0) < 0.7:
                signals.append("Assignment submission issues (14-day window)")
        
        if 'attendance_30d' in features:
            att_feat = features['attendance_30d']
            if att_feat.get('avg_attendance_rate', 100) < 80:
                signals.append("Attendance decline (30-day window)")
        
        return signals
    
    def _calculate_alert_confidence(self, risk_assessment: Dict[str, Any]) -> float:
        """Calculate confidence in alert."""
        
        # Base confidence on data availability
        features = risk_assessment.get('features', {})
        available_sources = len([k for k in features.keys() if '7d' in k or '14d' in k])
        max_sources = 4  # LMS, assignments, messages, attendance
        
        data_confidence = available_sources / max_sources
        
        # Adjust based on risk score consistency
        risk_factors = risk_assessment.get('risk_factors', [])
        if risk_factors:
            factor_variance = np.var(risk_factors)
            consistency_confidence = 1.0 - min(factor_variance, 1.0)
        else:
            consistency_confidence = 0.5
        
        # Overall confidence
        confidence = (data_confidence + consistency_confidence) / 2
        
        return np.clip(confidence, 0.0, 1.0)
    
    def get_recent_alerts(self, limit: int = 100) -> List[RiskAlert]:
        """Get recent alerts."""
        return list(self.alert_buffer)[-limit:]
    
    def get_student_status(self, student_id: str) -> Dict[str, Any]:
        """Get current status for specific student."""
        
        status = {
            'student_id': student_id,
            'last_activity': None,
            'current_risk': None,
            'recent_events': [],
            'data_sources': list(self.student_profiles.get(student_id, {}).keys())
        }
        
        # Get last activity
        for source_data in self.student_profiles.get(student_id, {}).values():
            if source_data['events']:
                last_event = max(source_data['events'], key=lambda e: e.timestamp)
                if status['last_activity'] is None or last_event.timestamp > status['last_activity']:
                    status['last_activity'] = last_event.timestamp
        
        # Get current risk assessment
        risk_assessment = self._comprehensive_risk_assessment(student_id)
        if risk_assessment:
            status['current_risk'] = risk_assessment['risk_score']
        
        # Get recent events
        for source in DataSource:
            for window_size in [7]:  # Recent events only
                events = list(self.sliding_window.data_windows[student_id].get(f"{source}_{window_size}d", []))
                status['recent_events'].extend(events)
        
        # Sort events by timestamp
        status['recent_events'].sort(key=lambda e: e.timestamp, reverse=True)
        status['recent_events'] = status['recent_events'][:10]  # Last 10 events
        
        return status
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        
        stats = self.stats.copy()
        stats.update({
            'is_running': self.is_running,
            'buffer_sizes': {
                'event_buffer': len(self.event_buffer),
                'alert_buffer': len(self.alert_buffer)
            },
            'student_count': len(self.student_profiles),
            'current_threshold': self.threshold_manager.get_threshold(),
            'drift_detected': self.drift_detector.is_drift_detected(),
            'drift_history_count': len(self.drift_detector.drift_history)
        })
        
        return stats

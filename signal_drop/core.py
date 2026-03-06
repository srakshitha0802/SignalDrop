"""
Core System - SignalDrop AI Main Interface

Integrates all layers to provide the complete early-warning risk detection system.
"""

from .data_layer import DataProcessor
from .representation_layer import TemporalEmbedding
from .reasoning_layer import GenAIReasoner
from .risk_layer import RiskScorer
from .explainability_layer import ExplainabilityEngine
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import json

logger = logging.getLogger(__name__)

class SignalDropSystem:
    """Main SignalDrop AI system for early-warning risk detection."""
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-3.5-turbo"):
        """Initialize the SignalDrop system."""
        self.data_processor = DataProcessor()
        self.temporal_embedding = TemporalEmbedding()
        self.reasoner = GenAIReasoner(model_name=model_name, api_key=api_key)
        self.risk_scorer = RiskScorer()
        self.explainability_engine = ExplainabilityEngine(model_name=model_name, api_key=api_key)
        
        # Store historical data for temporal analysis
        self.student_histories = {}
        
    def process_student_data(self, raw_data: Dict[str, List[Dict]], 
                           student_id: str = None) -> List[Dict[str, Any]]:
        """Process raw student data and generate early-warning alerts."""
        
        # Process raw data through data layer
        processed_data = self._process_raw_data(raw_data)
        
        # Generate alerts for each student
        alerts = []
        for sid, profile in processed_data.items():
            if student_id and sid != student_id:
                continue
                
            try:
                alert = self._generate_student_alert(sid, profile)
                if alert:
                    alerts.append(alert)
            except Exception as e:
                logger.error(f"Error generating alert for student {sid}: {e}")
        
        return alerts
    
    def _process_raw_data(self, raw_data: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """Process raw data through the data layer."""
        
        # Process each data source
        lms_df = self.data_processor.process_lms_activity(raw_data.get('lms_activity', []))
        assignment_df = self.data_processor.process_assignment_submissions(raw_data.get('assignments', []))
        message_df = self.data_processor.process_student_messages(raw_data.get('messages', []))
        attendance_df = self.data_processor.process_attendance_records(raw_data.get('attendance', []))
        
        # Aggregate signals by student
        student_profiles = self.data_processor.aggregate_student_signals(
            lms_df, assignment_df, message_df, attendance_df
        )
        
        return student_profiles
    
    def _generate_student_alert(self, student_id: str, student_profile: Dict) -> Optional[Dict[str, Any]]:
        """Generate a comprehensive alert for a single student."""
        
        # Extract temporal features
        temporal_features = self.temporal_embedding.extract_temporal_features(student_profile)
        
        # Create temporal embeddings
        temporal_embeddings = self.temporal_embedding.create_temporal_windows(
            temporal_features, student_id
        )
        
        # Get historical embeddings for drift detection
        historical_embeddings = self.student_histories.get(student_id, [])
        
        # Detect temporal drift
        temporal_drift = self.temporal_embedding.detect_temporal_drift(
            temporal_embeddings, historical_embeddings
        )
        
        # Extract narrative using GenAI reasoning
        narrative_analysis = self.reasoner.extract_student_narrative(
            student_profile, temporal_embeddings
        )
        
        # Calculate risk momentum
        risk_assessment = self.risk_scorer.calculate_risk_momentum(
            student_id, student_profile, temporal_embeddings, narrative_analysis, temporal_drift
        )
        
        # Generate explanation
        explanation = self.explainability_engine.generate_explanation(
            student_id, risk_assessment, student_profile, narrative_analysis
        )
        
        # Store current embeddings for future drift detection
        if student_id not in self.student_histories:
            self.student_histories[student_id] = []
        self.student_histories[student_id].append(temporal_embeddings)
        
        # Keep only recent history (last 10 time points)
        if len(self.student_histories[student_id]) > 10:
            self.student_histories[student_id] = self.student_histories[student_id][-10:]
        
        # Return alert if risk is above threshold
        if risk_assessment['risk_score'] > 0.3:  # Adjustable threshold
            return {
                "student_id": student_id,
                "risk_momentum": risk_assessment['risk_momentum'],
                "confidence": explanation['confidence'],
                "key_signals": explanation['key_signals'],
                "explanation": explanation['explanation'],
                "risk_score": risk_assessment['risk_score'],
                "risk_level": risk_assessment['risk_level'],
                "timestamp": explanation['timestamp'],
                "uncertainty": explanation['uncertainty'],
                "actionable_insights": explanation['actionable_insights'],
                "limitations": explanation['limitations']
            }
        
        return None
    
    def get_risk_timeline(self, student_id: str, days: int = 30) -> List[Dict]:
        """Get risk timeline for a specific student."""
        return self.risk_scorer.get_risk_timeline(student_id, days)
    
    def detect_anomalies(self, raw_data: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """Detect anomalous patterns across all students."""
        processed_data = self._process_raw_data(raw_data)
        return self.risk_scorer.detect_anomalies(processed_data)
    
    def cluster_weak_signals(self, raw_data: Dict[str, List[Dict]]) -> Dict[str, List[str]]:
        """Cluster weak signals across multiple students."""
        processed_data = self._process_raw_data(raw_data)
        return self.reasoner.cluster_weak_signals(processed_data)
    
    def get_student_profile_summary(self, student_id: str, raw_data: Dict[str, List[Dict]]) -> Dict:
        """Get comprehensive profile summary for a student."""
        processed_data = self._process_raw_data(raw_data)
        
        if student_id not in processed_data:
            return {"error": f"Student {student_id} not found in data"}
        
        profile = processed_data[student_id]
        
        # Generate temporal features and embeddings
        temporal_features = self.temporal_embedding.extract_temporal_features(profile)
        temporal_embeddings = self.temporal_embedding.create_temporal_windows(
            temporal_features, student_id
        )
        
        # Get narrative analysis
        narrative_analysis = self.reasoner.extract_student_narrative(
            profile, temporal_embeddings
        )
        
        # Get risk assessment
        historical_embeddings = self.student_histories.get(student_id, [])
        temporal_drift = self.temporal_embedding.detect_temporal_drift(
            temporal_embeddings, historical_embeddings
        )
        
        risk_assessment = self.risk_scorer.calculate_risk_momentum(
            student_id, profile, temporal_embeddings, narrative_analysis, temporal_drift
        )
        
        return {
            "student_id": student_id,
            "profile": profile,
            "temporal_features": temporal_features,
            "narrative_analysis": narrative_analysis,
            "risk_assessment": risk_assessment,
            "temporal_drift": temporal_drift
        }
    
    def export_alerts_json(self, alerts: List[Dict], filename: str = None) -> str:
        """Export alerts to JSON format."""
        if filename is None:
            filename = f"signal_drop_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(alerts, f, indent=2, default=str)
        
        return filename
    
    def get_system_statistics(self, raw_data: Dict[str, List[Dict]]) -> Dict:
        """Get system-wide statistics."""
        processed_data = self._process_raw_data(raw_data)
        
        stats = {
            "total_students": len(processed_data),
            "data_source_coverage": {},
            "risk_distribution": {"low": 0, "medium": 0, "high": 0},
            "momentum_distribution": {"increasing": 0, "stable": 0, "decreasing": 0},
            "confidence_distribution": {"low": 0, "medium": 0, "high": 0}
        }
        
        # Data source coverage
        data_sources = ['lms_activity', 'assignments', 'messages', 'attendance']
        for source in data_sources:
            coverage = sum(1 for profile in processed_data.values() if profile.get(source))
            stats["data_source_coverage"][source] = {
                "coverage": coverage,
                "percentage": coverage / len(processed_data) * 100 if processed_data else 0
            }
        
        # Generate alerts to get risk distribution
        alerts = self.process_student_data(raw_data)
        for alert in alerts:
            risk_level = alert.get('risk_level', 'low')
            momentum = alert.get('risk_momentum', 'stable')
            confidence = alert.get('confidence', 'low')
            
            stats["risk_distribution"][risk_level] += 1
            stats["momentum_distribution"][momentum] += 1
            stats["confidence_distribution"][confidence] += 1
        
        return stats

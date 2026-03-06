"""
Representation Layer - Temporal Embeddings and Signal Fusion

Creates temporal embeddings for each student using sliding windows
and fuses multi-modal signals for comprehensive representation.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
import logging

logger = logging.getLogger(__name__)

class TemporalEmbedding:
    """Creates temporal embeddings for student risk detection."""
    
    def __init__(self, embedding_dim: int = 64, windows: List[int] = [7, 14, 30]):
        self.embedding_dim = embedding_dim
        self.windows = windows  # Sliding window sizes in days
        self.scalers = {}
        self.pca_models = {}
        self.feature_names = []
        
    def extract_temporal_features(self, student_profile: Dict, current_date: datetime = None) -> Dict[str, float]:
        """Extract temporal features from student profile."""
        if current_date is None:
            current_date = datetime.now()
        
        features = {}
        
        # LMS Activity Features
        lms_data = student_profile.get('lms_activity', {})
        if lms_data:
            features.update({
                'lms_total_sessions': lms_data.get('total_sessions', 0),
                'lms_avg_gap_hours': lms_data.get('avg_session_gap_hours', 0),
                'lms_weekend_ratio': lms_data.get('weekend_activity_ratio', 0),
                'lms_peak_hour': lms_data.get('peak_activity_hour', 14),
                'lms_activity_7d': lms_data.get('activity_frequency_7d', 0),
                'lms_activity_14d': lms_data.get('activity_frequency_14d', 0),
                'lms_activity_30d': lms_data.get('activity_frequency_30d', 0)
            })
            
            # Activity decay features
            if lms_data.get('activity_frequency_14d', 0) > 0:
                features['lms_decay_7_14'] = lms_data.get('activity_frequency_7d', 0) / lms_data.get('activity_frequency_14d', 1)
            if lms_data.get('activity_frequency_30d', 0) > 0:
                features['lms_decay_14_30'] = lms_data.get('activity_frequency_14d', 0) / lms_data.get('activity_frequency_30d', 1)
        
        # Assignment Features
        assignment_data = student_profile.get('assignments', {})
        if assignment_data:
            features.update({
                'assign_total': assignment_data.get('total_assignments', 0),
                'assign_late_rate': assignment_data.get('late_submission_rate', 0),
                'assign_avg_delay': assignment_data.get('avg_delay_hours', 0),
                'assign_avg_text_length': assignment_data.get('avg_text_length', 0),
                'assign_avg_word_count': assignment_data.get('avg_word_count', 0),
                'assign_recent_late_rate': assignment_data.get('recent_late_rate', 0)
            })
            
            # Assignment quality decay
            if assignment_data.get('avg_text_length', 0) > 0:
                features['assign_quality_ratio'] = assignment_data.get('recent_late_rate', 0) / (assignment_data.get('late_submission_rate', 1) + 0.01)
        
        # Message Features
        message_data = student_profile.get('messages', {})
        if message_data:
            features.update({
                'msg_total': message_data.get('total_messages', 0),
                'msg_avg_length': message_data.get('avg_message_length', 0),
                'msg_avg_words': message_data.get('avg_word_count', 0),
                'msg_negative_total': message_data.get('negative_sentiment_total', 0),
                'msg_positive_total': message_data.get('positive_sentiment_total', 0),
                'msg_sentiment_ratio': message_data.get('avg_sentiment_ratio', 1),
                'msg_sentiment_decline': int(message_data.get('recent_sentiment_decline', False))
            })
            
            # Sentiment trend features
            if message_data.get('total_messages', 0) > 0:
                features['msg_neg_ratio'] = message_data.get('negative_sentiment_total', 0) / message_data.get('total_messages', 1)
                features['msg_pos_ratio'] = message_data.get('positive_sentiment_total', 0) / message_data.get('total_messages', 1)
        
        # Attendance Features
        attendance_data = student_profile.get('attendance', {})
        if attendance_data:
            features.update({
                'att_total_days': attendance_data.get('total_days', 0),
                'att_rate': attendance_data.get('attendance_rate', 0),
                'att_late_rate': attendance_data.get('late_rate', 0),
                'att_absent_rate': attendance_data.get('absent_rate', 0),
                'att_recent_rate': attendance_data.get('recent_attendance_rate', 0)
            })
            
            # Attendance decay
            if attendance_data.get('attendance_rate', 0) > 0:
                features['_att_decay_ratio'] = attendance_data.get('recent_attendance_rate', 0) / attendance_data.get('attendance_rate', 1)
        
        # Recency features (days since last activity)
        for activity_type, last_activity_key in [('lms', 'last_activity'), 
                                                ('assign', 'last_submission'),
                                                ('msg', 'last_message'),
                                                ('att', 'last_attendance')]:
            data = student_profile.get(activity_type, {})
            if last_activity_key in data and data[last_activity_key]:
                days_since = (current_date - data[last_activity_key]).days
                features[f'{activity_type}_days_since_last'] = days_since
        
        return features
    
    def create_temporal_windows(self, features: Dict[str, float], 
                               student_id: str) -> Dict[int, np.ndarray]:
        """Create temporal embeddings for different window sizes."""
        window_embeddings = {}
        
        # Convert features to vector
        feature_vector = np.array(list(features.values()))
        feature_names = list(features.keys())
        
        # Store feature names for explainability
        if not self.feature_names:
            self.feature_names = feature_names
        
        # Normalize features
        if student_id not in self.scalers:
            self.scalers[student_id] = StandardScaler()
            normalized_features = self.scalers[student_id].fit_transform(feature_vector.reshape(1, -1)).flatten()
        else:
            normalized_features = self.scalers[student_id].transform(feature_vector.reshape(1, -1)).flatten()
        
        # Create embeddings for each window size
        for window in self.windows:
            # Create window-specific features by applying temporal weighting
            window_features = self._apply_temporal_weighting(normalized_features, window, features)
            
            # Reduce dimensionality if needed
            if len(window_features) > self.embedding_dim:
                if student_id not in self.pca_models:
                    self.pca_models[student_id] = PCA(n_components=self.embedding_dim)
                    # Fit on dummy data to initialize
                    dummy_data = np.random.randn(10, len(window_features))
                    self.pca_models[student_id].fit(dummy_data)
                
                # Reshape for PCA
                window_features_reshaped = window_features.reshape(1, -1)
                if window_features_reshaped.shape[1] >= self.embedding_dim:
                    window_features = self.pca_models[student_id].transform(window_features_reshaped).flatten()
                else:
                    # Pad if not enough features
                    padding = np.zeros(self.embedding_dim - len(window_features))
                    window_features = np.concatenate([window_features, padding])
            else:
                # Pad if not enough features
                padding = np.zeros(self.embedding_dim - len(window_features))
                window_features = np.concatenate([window_features, padding])
            
            window_embeddings[window] = window_features
        
        return window_embeddings
    
    def _apply_temporal_weighting(self, features: np.ndarray, window: int, 
                                 raw_features: Dict[str, float]) -> np.ndarray:
        """Apply temporal weighting based on window size."""
        weighted_features = features.copy()
        
        # Apply exponential decay based on recency
        for i, (feature_name, value) in enumerate(zip(self.feature_names, features)):
            if 'days_since_last' in feature_name:
                # Higher weight for more recent activity
                decay_factor = np.exp(-value / window)  # Normalize by window size
                weighted_features[i] *= (1 + decay_factor)
            
            elif 'decay' in feature_name:
                # Emphasize decay features for longer windows
                if window >= 14:
                    weighted_features[i] *= 1.5
            
            elif 'recent' in feature_name:
                # Emphasize recent features for shorter windows
                if window <= 7:
                    weighted_features[i] *= 1.3
        
        return weighted_features
    
    def compute_temporal_similarity(self, embeddings_1: Dict[int, np.ndarray], 
                                   embeddings_2: Dict[int, np.ndarray]) -> float:
        """Compute similarity between temporal embeddings across all windows."""
        similarities = []
        
        for window in self.windows:
            if window in embeddings_1 and window in embeddings_2:
                # Compute cosine similarity
                emb1 = embeddings_1[window]
                emb2 = embeddings_2[window]
                
                # Handle zero vectors
                norm1 = np.linalg.norm(emb1)
                norm2 = np.linalg.norm(emb2)
                
                if norm1 > 0 and norm2 > 0:
                    similarity = np.dot(emb1, emb2) / (norm1 * norm2)
                    similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    def detect_temporal_drift(self, current_embeddings: Dict[int, np.ndarray],
                             historical_embeddings: List[Dict[int, np.ndarray]],
                             threshold: float = 0.3) -> Dict[str, Any]:
        """Detect temporal drift in student behavior patterns."""
        if not historical_embeddings:
            return {"drift_detected": False, "drift_score": 0.0, "drift_windows": []}
        
        drift_scores = {}
        drift_windows = []
        
        for window in self.windows:
            if window in current_embeddings:
                window_scores = []
                for hist_emb in historical_embeddings:
                    if window in hist_emb:
                        similarity = self.compute_temporal_similarity(
                            {window: current_embeddings[window]},
                            {window: hist_emb[window]}
                        )
                        window_scores.append(similarity)
                
                if window_scores:
                    # Drift is inverse of average similarity
                    avg_similarity = np.mean(window_scores)
                    drift_score = 1.0 - avg_similarity
                    drift_scores[window] = drift_score
                    
                    if drift_score > threshold:
                        drift_windows.append(window)
        
        overall_drift = np.mean(list(drift_scores.values())) if drift_scores else 0.0
        
        return {
            "drift_detected": overall_drift > threshold,
            "drift_score": overall_drift,
            "drift_windows": drift_windows,
            "window_drift_scores": drift_scores
        }
    
    def get_feature_importance(self, student_id: str, window: int) -> Dict[str, float]:
        """Get feature importance for explainability."""
        if student_id not in self.scalers or window not in self.windows:
            return {}
        
        # Get the most recent features for this student
        # This is a simplified version - in practice, you'd store feature histories
        scaler = self.scalers[student_id]
        
        # Create importance based on feature variance and temporal relevance
        importance = {}
        
        for i, feature_name in enumerate(self.feature_names):
            # Base importance from feature statistics
            if hasattr(scaler, 'scale_') and i < len(scaler.scale_):
                base_importance = 1.0 / (scaler.scale_[i] + 1e-6)
            else:
                base_importance = 1.0
            
            # Temporal weighting
            if 'days_since_last' in feature_name:
                temporal_weight = 1.5  # High importance for recency
            elif 'decay' in feature_name:
                temporal_weight = 1.3  # Medium importance for decay
            elif 'recent' in feature_name:
                temporal_weight = 1.2  # Slightly higher for recent
            else:
                temporal_weight = 1.0
            
            importance[feature_name] = base_importance * temporal_weight
        
        # Normalize importance scores
        total_importance = sum(importance.values())
        if total_importance > 0:
            importance = {k: v / total_importance for k, v in importance.items()}
        
        return importance

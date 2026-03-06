"""
Advanced Reasoning Layer for SignalDrop AI

Implements cutting-edge GenAI reasoning capabilities including:
- Multi-modal attention mechanisms
- Causal inference for root cause analysis
- Contrastive learning for pattern recognition
- Meta-learning for adaptation to new institutions
- Graph neural networks for social influence modeling
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import networkx as nx
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
import logging

logger = logging.getLogger(__name__)

class MultiModalAttention(nn.Module):
    """Advanced multi-modal attention mechanism for signal fusion."""
    
    def __init__(self, feature_dims: Dict[str, int], hidden_dim: int = 128):
        super().__init__()
        self.feature_dims = feature_dims
        self.hidden_dim = hidden_dim
        
        # Modality-specific encoders
        self.encoders = nn.ModuleDict()
        for modality, dim in feature_dims.items():
            self.encoders[modality] = nn.Sequential(
                nn.Linear(dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_dim, hidden_dim)
            )
        
        # Cross-modal attention
        self.attention = nn.MultiheadAttention(hidden_dim, num_heads=8, dropout=0.1)
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim * len(feature_dims), hidden_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim * 2, hidden_dim)
        )
        
    def forward(self, features: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Forward pass with multi-modal attention."""
        
        # Encode each modality
        encoded_features = []
        for modality, feature_tensor in features.items():
            if modality in self.encoders:
                encoded = self.encoders[modality](feature_tensor)
                encoded_features.append(encoded)
        
        if not encoded_features:
            return torch.zeros(1, self.hidden_dim)
        
        # Stack for attention
        stacked = torch.stack(encoded_features, dim=1)  # [batch, modalities, hidden]
        
        # Apply self-attention across modalities
        attended, _ = self.attention(stacked, stacked, stacked)
        
        # Flatten and fuse
        flattened = attended.view(attended.size(0), -1)
        fused = self.fusion(flattened)
        
        return fused

class CausalInferenceEngine:
    """Advanced causal inference for root cause analysis."""
    
    def __init__(self):
        self.causal_graph = None
        self.intervention_effects = {}
        
    def build_causal_graph(self, student_data: Dict[str, Dict]) -> nx.DiGraph:
        """Build causal graph from student data."""
        
        G = nx.DiGraph()
        
        # Add nodes for different factors
        factors = [
            'engagement', 'academic_performance', 'social_connection',
            'external_stress', 'time_management', 'motivation',
            'support_system', 'financial_stability'
        ]
        
        for factor in factors:
            G.add_node(factor, type='latent')
        
        # Add data source nodes
        data_sources = ['lms_activity', 'assignments', 'messages', 'attendance']
        for source in data_sources:
            G.add_node(source, type='observed')
        
        # Add causal edges based on domain knowledge
        causal_edges = [
            ('external_stress', 'engagement'),
            ('external_stress', 'time_management'),
            ('financial_stability', 'external_stress'),
            ('support_system', 'motivation'),
            ('motivation', 'engagement'),
            ('engagement', 'academic_performance'),
            ('social_connection', 'engagement'),
            ('time_management', 'academic_performance'),
            ('engagement', 'lms_activity'),
            ('academic_performance', 'assignments'),
            ('social_connection', 'messages'),
            ('engagement', 'attendance')
        ]
        
        G.add_edges_from(causal_edges)
        
        self.causal_graph = G
        return G
    
    def estimate_causal_effects(self, student_data: Dict[str, Dict]) -> Dict[str, float]:
        """Estimate causal effects using do-calculus principles."""
        
        if self.causal_graph is None:
            self.build_causal_graph(student_data)
        
        effects = {}
        
        # Simplified causal effect estimation
        for student_id, profile in student_data.items():
            student_effects = {}
            
            # Estimate effect of engagement on outcomes
            engagement_level = self._extract_engagement_level(profile)
            academic_outcome = self._extract_academic_outcome(profile)
            
            # Simple causal effect (in practice, would use more sophisticated methods)
            causal_effect = self._compute_causal_effect(engagement_level, academic_outcome)
            student_effects['engagement_on_academic'] = causal_effect
            
            # Estimate effect of external stress
            stress_level = self._extract_stress_level(profile)
            stress_effect = self._compute_stress_effect(stress_level, engagement_level)
            student_effects['stress_on_engagement'] = stress_effect
            
            effects[student_id] = student_effects
        
        return effects
    
    def _extract_engagement_level(self, profile: Dict) -> float:
        """Extract engagement level from student profile."""
        lms_data = profile.get('lms_activity', {})
        return lms_data.get('activity_frequency_7d', 0) / 10.0  # Normalize
    
    def _extract_academic_outcome(self, profile: Dict) -> float:
        """Extract academic outcome from student profile."""
        assign_data = profile.get('assignments', {})
        return 1.0 - assign_data.get('late_submission_rate', 0)  # Inverse of late rate
    
    def _extract_stress_level(self, profile: Dict) -> float:
        """Extract stress level from student profile."""
        msg_data = profile.get('messages', {})
        return 1.0 - msg_data.get('avg_sentiment_ratio', 1.0)  # Inverse of sentiment
    
    def _compute_causal_effect(self, treatment: float, outcome: float) -> float:
        """Compute simplified causal effect."""
        # In practice, would use propensity scores, instrumental variables, etc.
        return outcome - treatment * 0.3  # Simplified causal model
    
    def _compute_stress_effect(self, stress: float, engagement: float) -> float:
        """Compute stress effect on engagement."""
        return -stress * 0.5  # Negative effect of stress

class ContrastiveLearningModel:
    """Contrastive learning for robust pattern recognition."""
    
    def __init__(self, input_dim: int, projection_dim: int = 64):
        self.input_dim = input_dim
        self.projection_dim = projection_dim
        
        # Encoder network
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, projection_dim)
        )
        
        # Projection head for contrastive learning
        self.projection_head = nn.Sequential(
            nn.Linear(projection_dim, projection_dim),
            nn.ReLU(),
            nn.Linear(projection_dim, projection_dim)
        )
    
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to representation."""
        return self.encoder(x)
    
    def project(self, z: torch.Tensor) -> torch.Tensor:
        """Project representation for contrastive learning."""
        return self.projection_head(z)
    
    def contrastive_loss(self, z1: torch.Tensor, z2: torch.Tensor, 
                        temperature: float = 0.1) -> torch.Tensor:
        """Compute contrastive loss."""
        z1_proj = F.normalize(self.project(z1), dim=1)
        z2_proj = F.normalize(self.project(z2), dim=1)
        
        # Compute similarity matrix
        similarity = torch.mm(z1_proj, z2_proj.t()) / temperature
        
        # Positive pairs are on diagonal
        labels = torch.arange(z1_proj.size(0))
        
        return F.cross_entropy(similarity, labels)

class MetaLearningAdapter:
    """Meta-learning for rapid adaptation to new institutions."""
    
    def __init__(self, base_model_dim: int, meta_lr: float = 0.01):
        self.base_model_dim = base_model_dim
        self.meta_lr = meta_lr
        
        # Meta-parameters for adaptation
        self.meta_weights = torch.randn(base_model_dim, base_model_dim) * 0.01
        self.meta_bias = torch.zeros(base_model_dim)
        
        # Task-specific adaptation history
        self.adaptation_history = []
        
    def adapt_to_institution(self, base_features: torch.Tensor, 
                           institution_data: Dict[str, Dict]) -> torch.Tensor:
        """Adapt model to new institution using meta-learning."""
        
        # Extract institution-specific patterns
        institution_features = self._extract_institution_features(institution_data)
        
        # Compute adaptation weights
        adaptation_weights = self._compute_adaptation_weights(institution_features)
        
        # Apply adaptation to base features
        adapted_features = torch.mm(base_features, self.meta_weights) + self.meta_bias
        adapted_features = adapted_features * adaptation_weights.unsqueeze(0)
        
        # Store adaptation for future meta-learning
        self.adaptation_history.append({
            'institution_features': institution_features,
            'adaptation_weights': adaptation_weights,
            'performance': self._evaluate_adaptation(adapted_features, institution_data)
        })
        
        return adapted_features
    
    def _extract_institution_features(self, institution_data: Dict[str, Dict]) -> torch.Tensor:
        """Extract institution-level features."""
        features = []
        
        # Aggregate statistics across all students
        all_profiles = list(institution_data.values())
        
        # Average engagement patterns
        avg_engagement = np.mean([self._compute_engagement(p) for p in all_profiles])
        features.append(avg_engagement)
        
        # Engagement variance
        engagement_var = np.var([self._compute_engagement(p) for p in all_profiles])
        features.append(engagement_var)
        
        # Communication patterns
        avg_communication = np.mean([self._compute_communication(p) for p in all_profiles])
        features.append(avg_communication)
        
        # Academic performance distribution
        avg_performance = np.mean([self._compute_performance(p) for p in all_profiles])
        features.append(avg_performance)
        
        return torch.tensor(features, dtype=torch.float32)
    
    def _compute_adaptation_weights(self, institution_features: torch.Tensor) -> torch.Tensor:
        """Compute adaptation weights based on institution characteristics."""
        
        # Simple linear combination (in practice, would use learned meta-model)
        weights = torch.sigmoid(torch.sum(institution_features * self.meta_weights.mean(dim=0)))
        
        # Create per-feature adaptation weights
        adaptation_weights = torch.ones(self.base_model_dim) * weights
        
        return adaptation_weights
    
    def _compute_engagement(self, profile: Dict) -> float:
        """Compute engagement score from profile."""
        lms_data = profile.get('lms_activity', {})
        return lms_data.get('activity_frequency_7d', 0) / 10.0
    
    def _compute_communication(self, profile: Dict) -> float:
        """Compute communication score from profile."""
        msg_data = profile.get('messages', {})
        return msg_data.get('total_messages', 0) / 20.0
    
    def _compute_performance(self, profile: Dict) -> float:
        """Compute performance score from profile."""
        assign_data = profile.get('assignments', {})
        return 1.0 - assign_data.get('late_submission_rate', 0)
    
    def _evaluate_adaptation(self, adapted_features: torch.Tensor, 
                           institution_data: Dict[str, Dict]) -> float:
        """Evaluate adaptation performance."""
        # Simplified evaluation (in practice, would use validation set)
        return torch.mean(adapted_features).item()

class SocialInfluenceAnalyzer:
    """Graph neural network for social influence modeling."""
    
    def __init__(self, node_dim: int, hidden_dim: int = 64):
        self.node_dim = node_dim
        self.hidden_dim = hidden_dim
        
        # Graph neural network layers
        self.gnn_layers = nn.ModuleList([
            nn.Linear(node_dim, hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Linear(hidden_dim, hidden_dim)
        ])
        
        # Influence prediction head
        self.influence_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
    def build_social_graph(self, student_data: Dict[str, Dict], 
                         message_data: List[Dict]) -> nx.Graph:
        """Build social interaction graph from communication data."""
        
        G = nx.Graph()
        
        # Add nodes with features
        for student_id, profile in student_data.items():
            features = self._extract_student_features(profile)
            G.add_node(student_id, features=features)
        
        # Add edges based on communication patterns
        communication_pairs = self._extract_communication_pairs(message_data)
        
        for student1, student2, strength in communication_pairs:
            if G.has_node(student1) and G.has_node(student2):
                G.add_edge(student1, student2, weight=strength)
        
        return G
    
    def analyze_influence_propagation(self, graph: nx.Graph, 
                                    at_risk_students: List[str]) -> Dict[str, float]:
        """Analyze how risk propagates through social network."""
        
        influence_scores = {}
        
        # Compute influence using graph neural network
        for student_id in graph.nodes():
            student_features = torch.tensor(graph.nodes[student_id]['features'], 
                                         dtype=torch.float32).unsqueeze(0)
            
            # Get neighbors
            neighbors = list(graph.neighbors(student_id))
            
            if neighbors:
                # Aggregate neighbor features
                neighbor_features = []
                for neighbor in neighbors:
                    neighbor_feat = torch.tensor(graph.nodes[neighbor]['features'], 
                                                dtype=torch.float32).unsqueeze(0)
                    neighbor_features.append(neighbor_feat)
                
                neighbor_tensor = torch.cat(neighbor_features, dim=0)
                
                # Compute influence
                combined_features = torch.cat([student_features, neighbor_tensor.mean(dim=0, keepdim=True)], dim=1)
                influence = self.influence_head(combined_features)
                influence_scores[student_id] = influence.item()
            else:
                influence_scores[student_id] = 0.0
        
        return influence_scores
    
    def _extract_student_features(self, profile: Dict) -> List[float]:
        """Extract student features for graph representation."""
        features = []
        
        # Engagement features
        lms_data = profile.get('lms_activity', {})
        features.append(lms_data.get('activity_frequency_7d', 0) / 10.0)
        features.append(lms_data.get('avg_session_gap_hours', 0) / 100.0)
        
        # Academic features
        assign_data = profile.get('assignments', {})
        features.append(assign_data.get('late_submission_rate', 0))
        features.append(assign_data.get('avg_text_length', 0) / 200.0)
        
        # Communication features
        msg_data = profile.get('messages', {})
        features.append(msg_data.get('total_messages', 0) / 20.0)
        features.append(msg_data.get('avg_sentiment_ratio', 1.0))
        
        # Attendance features
        att_data = profile.get('attendance', {})
        features.append(att_data.get('attendance_rate', 1.0))
        
        return features
    
    def _extract_communication_pairs(self, message_data: List[Dict]) -> List[Tuple[str, str, float]]:
        """Extract communication pairs and interaction strength."""
        # Simplified: in practice, would analyze actual message content and reply patterns
        pairs = []
        
        # Group messages by week
        weekly_messages = {}
        for msg in message_data:
            week = msg.get('week', 1)
            if week not in weekly_messages:
                weekly_messages[week] = []
            weekly_messages[week].append(msg)
        
        # Find students who communicated in same week (potential interaction)
        for week, msgs in weekly_messages.items():
            students_in_week = [msg['student_id'] for msg in msgs]
            
            # Create pairs (simplified - would use actual reply patterns)
            for i, student1 in enumerate(students_in_week):
                for student2 in students_in_week[i+1:]:
                    # Interaction strength based on communication frequency
                    strength = 1.0 / len(students_in_week)  # Simplified
                    pairs.append((student1, student2, strength))
        
        return pairs

class AdvancedGenAIReasoner:
    """Advanced GenAI reasoning system combining all advanced components."""
    
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        self.api_key = api_key
        self.model_name = model_name
        
        # Initialize advanced components
        self.causal_engine = CausalInferenceEngine()
        self.contrastive_model = ContrastiveLearningModel(input_dim=64)
        self.meta_adapter = MetaLearningAdapter(base_model_dim=64)
        self.social_analyzer = SocialInfluenceAnalyzer(node_dim=7)
        
        # Multi-modal attention
        feature_dims = {
            'lms_features': 10,
            'assignment_features': 8,
            'message_features': 6,
            'attendance_features': 4
        }
        self.multimodal_attention = MultiModalAttention(feature_dims)
        
        # Advanced pattern memory
        self.pattern_memory = []
        self.institution_profiles = {}
        
    def advanced_narrative_extraction(self, student_profile: Dict, 
                                    temporal_embeddings: Dict,
                                    social_context: Dict = None) -> Dict[str, Any]:
        """Advanced narrative extraction with all reasoning components."""
        
        # 1. Multi-modal feature fusion with attention
        multimodal_features = self._extract_multimodal_features(student_profile)
        attended_features = self._apply_multimodal_attention(multimodal_features)
        
        # 2. Causal inference for root cause analysis
        causal_effects = self.causal_engine.estimate_causal_effects({student_profile['student_id']: student_profile})
        
        # 3. Contrastive pattern recognition
        pattern_similarity = self._contrastive_pattern_matching(attended_features, student_profile)
        
        # 4. Social influence analysis
        social_influence = {}
        if social_context:
            social_graph = self.social_analyzer.build_social_graph(
                social_context['students'], 
                social_context['messages']
            )
            social_influence = self.social_analyzer.analyze_influence_propagation(
                social_graph, 
                [student_profile['student_id']]
            )
        
        # 5. Meta-learning adaptation
        adapted_features = self._apply_meta_learning_adaptation(attended_features, student_profile)
        
        # 6. Advanced narrative synthesis
        narrative = self._synthesize_advanced_narrative(
            student_profile, causal_effects, pattern_similarity, 
            social_influence, adapted_features
        )
        
        return {
            "student_id": student_profile['student_id'],
            "advanced_narrative": narrative,
            "causal_analysis": causal_effects.get(student_profile['student_id'], {}),
            "pattern_similarity": pattern_similarity,
            "social_influence": social_influence,
            "multimodal_features": attended_features.detach().numpy().tolist() if hasattr(attended_features, 'detach') else attended_features,
            "confidence_score": self._compute_advanced_confidence(narrative, causal_effects, pattern_similarity)
        }
    
    def _extract_multimodal_features(self, student_profile: Dict) -> Dict[str, torch.Tensor]:
        """Extract features for multi-modal attention."""
        features = {}
        
        # LMS features
        lms_data = student_profile.get('lms_activity', {})
        lms_features = torch.tensor([
            lms_data.get('total_sessions', 0) / 50.0,
            lms_data.get('avg_session_gap_hours', 0) / 100.0,
            lms_data.get('weekend_activity_ratio', 0),
            lms_data.get('activity_frequency_7d', 0) / 20.0,
            lms_data.get('activity_frequency_14d', 0) / 40.0,
            lms_data.get('activity_frequency_30d', 0) / 80.0,
            lms_data.get('peak_activity_hour', 14) / 24.0,
            lms_data.get('time_since_last_activity', 0) / 100.0,
            lms_data.get('lms_decay_7_14', 0),
            lms_data.get('lms_decay_14_30', 0)
        ], dtype=torch.float32).unsqueeze(0)
        features['lms_features'] = lms_features
        
        # Assignment features
        assign_data = student_profile.get('assignments', {})
        assign_features = torch.tensor([
            assign_data.get('total_assignments', 0) / 20.0,
            assign_data.get('late_submission_rate', 0),
            assign_data.get('avg_delay_hours', 0) / 100.0,
            assign_data.get('avg_text_length', 0) / 200.0,
            assign_data.get('avg_word_count', 0) / 100.0,
            assign_data.get('recent_late_rate', 0),
            assign_data.get('assign_quality_ratio', 0),
            assign_data.get('last_submission_days_ago', 0) / 100.0
        ], dtype=torch.float32).unsqueeze(0)
        features['assignment_features'] = assign_features
        
        # Message features
        msg_data = student_profile.get('messages', {})
        msg_features = torch.tensor([
            msg_data.get('total_messages', 0) / 50.0,
            msg_data.get('avg_message_length', 0) / 100.0,
            msg_data.get('avg_word_count', 0) / 50.0,
            msg_data.get('negative_sentiment_total', 0) / 20.0,
            msg_data.get('positive_sentiment_total', 0) / 20.0,
            msg_data.get('avg_sentiment_ratio', 1.0)
        ], dtype=torch.float32).unsqueeze(0)
        features['message_features'] = msg_features
        
        # Attendance features
        att_data = student_profile.get('attendance', {})
        att_features = torch.tensor([
            att_data.get('total_days', 0) / 100.0,
            att_data.get('attendance_rate', 1.0),
            att_data.get('late_rate', 0),
            att_data.get('absent_rate', 0)
        ], dtype=torch.float32).unsqueeze(0)
        features['attendance_features'] = att_features
        
        return features
    
    def _apply_multimodal_attention(self, features: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Apply multi-modal attention to fuse features."""
        return self.multimodal_attention(features)
    
    def _contrastive_pattern_matching(self, features: torch.Tensor, 
                                     student_profile: Dict) -> Dict[str, float]:
        """Perform contrastive pattern matching against known patterns."""
        similarities = {}
        
        # Compare with stored patterns
        for pattern in self.pattern_memory:
            pattern_features = torch.tensor(pattern['features'], dtype=torch.float32).unsqueeze(0)
            
            # Compute similarity
            similarity = F.cosine_similarity(features, pattern_features, dim=1)
            similarities[pattern['name']] = similarity.item()
        
        return similarities
    
    def _apply_meta_learning_adaptation(self, features: torch.Tensor, 
                                      student_profile: Dict) -> torch.Tensor:
        """Apply meta-learning adaptation."""
        # Simplified meta-learning adaptation
        institution_id = student_profile.get('institution_id', 'default')
        
        if institution_id not in self.institution_profiles:
            self.institution_profiles[institution_id] = {'data': [student_profile]}
        else:
            self.institution_profiles[institution_id]['data'].append(student_profile)
        
        # Adapt features based on institution patterns
        adapted_features = features * 1.0  # Simplified adaptation
        
        return adapted_features
    
    def _synthesize_advanced_narrative(self, student_profile: Dict, 
                                    causal_effects: Dict,
                                    pattern_similarity: Dict,
                                    social_influence: Dict,
                                    adapted_features: torch.Tensor) -> Dict[str, Any]:
        """Synthesize advanced narrative with all reasoning components."""
        
        narrative = {
            "summary": self._generate_narrative_summary(student_profile, causal_effects),
            "root_causes": self._identify_root_causes(causal_effects),
            "pattern_matches": self._interpret_pattern_matches(pattern_similarity),
            "social_context": self._interpret_social_influence(social_influence),
            "trajectory_prediction": self._predict_trajectory(adapted_features, student_profile),
            "intervention_recommendations": self._generate_intervention_recommendations(
                causal_effects, pattern_similarity, social_influence
            )
        }
        
        return narrative
    
    def _generate_narrative_summary(self, student_profile: Dict, 
                                  causal_effects: Dict) -> str:
        """Generate comprehensive narrative summary."""
        
        student_id = student_profile['student_id']
        
        # Extract key indicators
        engagement_trend = self._analyze_engagement_trend(student_profile)
        academic_trend = self._analyze_academic_trend(student_profile)
        communication_trend = self._analyze_communication_trend(student_profile)
        
        summary_parts = []
        
        if engagement_trend['direction'] == 'declining':
            summary_parts.append(f"Student {student_id} shows declining engagement patterns")
        
        if academic_trend['direction'] == 'declining':
            summary_parts.append("with deteriorating academic performance")
        
        if communication_trend['direction'] == 'declining':
            summary_parts.append("and reduced communication frequency")
        
        # Add causal insights
        if causal_effects.get('stress_on_engagement', 0) < -0.3:
            summary_parts.append("potentially influenced by external stress factors")
        
        if not summary_parts:
            summary_parts.append(f"Student {student_id} maintains stable engagement patterns")
        
        return ". ".join(summary_parts) + "."
    
    def _identify_root_causes(self, causal_effects: Dict) -> List[str]:
        """Identify root causes from causal analysis."""
        root_causes = []
        
        for cause, effect in causal_effects.items():
            # Handle both dict and float cases
            if isinstance(effect, dict):
                effect_value = effect.get('value', 0)  # Extract value if dict
            else:
                effect_value = effect
            
            if effect_value < -0.3:  # Significant negative effect
                if cause == 'stress_on_engagement':
                    root_causes.append("External stress impacting engagement")
                elif cause == 'engagement_on_academic':
                    root_causes.append("Engagement decline affecting academic performance")
        
        return root_causes
    
    def _interpret_pattern_matches(self, pattern_similarity: Dict) -> Dict[str, str]:
        """Interpret pattern similarity results."""
        interpretations = {}
        
        for pattern, similarity in pattern_similarity.items():
            if similarity > 0.8:
                interpretations[pattern] = "Strong match"
            elif similarity > 0.6:
                interpretations[pattern] = "Moderate match"
            elif similarity > 0.4:
                interpretations[pattern] = "Weak match"
            else:
                interpretations[pattern] = "No significant match"
        
        return interpretations
    
    def _interpret_social_influence(self, social_influence: Dict) -> Dict[str, str]:
        """Interpret social influence analysis."""
        interpretations = {}
        
        for student_id, influence_score in social_influence.items():
            if influence_score > 0.7:
                interpretations[student_id] = "High social influence"
            elif influence_score > 0.4:
                interpretations[student_id] = "Moderate social influence"
            else:
                interpretations[student_id] = "Low social influence"
        
        return interpretations
    
    def _predict_trajectory(self, features: torch.Tensor, 
                           student_profile: Dict) -> Dict[str, Any]:
        """Predict future trajectory."""
        
        # Simplified trajectory prediction
        current_risk = self._compute_current_risk(student_profile)
        
        # Predict based on features and trends
        if current_risk > 0.7:
            trajectory = "declining"
            confidence = 0.8
        elif current_risk > 0.4:
            trajectory = "stable"
            confidence = 0.6
        else:
            trajectory = "improving"
            confidence = 0.7
        
        return {
            "predicted_trajectory": trajectory,
            "confidence": confidence,
            "time_horizon": "4-6 weeks",
            "key_factors": self._identify_trajectory_factors(student_profile)
        }
    
    def _generate_intervention_recommendations(self, causal_effects: Dict,
                                            pattern_similarity: Dict,
                                            social_influence: Dict) -> List[str]:
        """Generate personalized intervention recommendations."""
        recommendations = []
        
        # Based on causal effects
        if causal_effects.get('stress_on_engagement', 0) < -0.3:
            recommendations.append("Provide stress management resources and counseling support")
        
        # Based on pattern matches
        high_risk_patterns = [p for p, s in pattern_similarity.items() if s > 0.7 and 'risk' in p]
        if high_risk_patterns:
            recommendations.append("Implement proactive monitoring and early intervention")
        
        # Based on social influence
        high_influence_students = [s for s, inf in social_influence.items() if inf > 0.7]
        if high_influence_students:
            recommendations.append("Leverage positive peer influence and support networks")
        
        # Default recommendations
        if not recommendations:
            recommendations.append("Continue routine monitoring and engagement")
        
        return recommendations
    
    def _compute_advanced_confidence(self, narrative: Dict, 
                                   causal_effects: Dict,
                                   pattern_similarity: Dict) -> float:
        """Compute advanced confidence score."""
        
        confidence_factors = []
        
        # Causal analysis confidence
        if causal_effects:
            confidence_factors.append(0.7)  # Causal analysis provides strong confidence
        else:
            confidence_factors.append(0.3)
        
        # Pattern matching confidence
        if pattern_similarity:
            max_similarity = max(pattern_similarity.values())
            confidence_factors.append(max_similarity)
        else:
            confidence_factors.append(0.5)
        
        # Narrative completeness confidence
        narrative_completeness = len([v for v in narrative.values() if v]) / len(narrative)
        confidence_factors.append(narrative_completeness)
        
        return np.mean(confidence_factors)
    
    def _analyze_engagement_trend(self, student_profile: Dict) -> Dict[str, Any]:
        """Analyze engagement trend."""
        lms_data = student_profile.get('lms_activity', {})
        
        recent_activity = lms_data.get('activity_frequency_7d', 0)
        earlier_activity = lms_data.get('activity_frequency_14d', 0)
        
        if recent_activity < earlier_activity * 0.8:
            direction = "declining"
        elif recent_activity > earlier_activity * 1.2:
            direction = "improving"
        else:
            direction = "stable"
        
        return {"direction": direction, "magnitude": abs(recent_activity - earlier_activity)}
    
    def _analyze_academic_trend(self, student_profile: Dict) -> Dict[str, Any]:
        """Analyze academic trend."""
        assign_data = student_profile.get('assignments', {})
        
        recent_late_rate = assign_data.get('recent_late_rate', 0)
        overall_late_rate = assign_data.get('late_submission_rate', 0)
        
        if recent_late_rate > overall_late_rate + 0.1:
            direction = "declining"
        elif recent_late_rate < overall_late_rate - 0.1:
            direction = "improving"
        else:
            direction = "stable"
        
        return {"direction": direction, "magnitude": abs(recent_late_rate - overall_late_rate)}
    
    def _analyze_communication_trend(self, student_profile: Dict) -> Dict[str, Any]:
        """Analyze communication trend."""
        msg_data = student_profile.get('messages', {})
        
        if msg_data.get('recent_sentiment_decline', False):
            direction = "declining"
        elif msg_data.get('total_messages', 0) > 10:
            direction = "stable"
        else:
            direction = "improving"
        
        return {"direction": direction, "magnitude": msg_data.get('avg_sentiment_ratio', 1.0)}
    
    def _compute_current_risk(self, student_profile: Dict) -> float:
        """Compute current risk score."""
        risk_factors = []
        
        # Engagement risk
        lms_data = student_profile.get('lms_activity', {})
        if lms_data.get('activity_frequency_7d', 0) < 5:
            risk_factors.append(0.7)
        
        # Academic risk
        assign_data = student_profile.get('assignments', {})
        if assign_data.get('late_submission_rate', 0) > 0.3:
            risk_factors.append(0.6)
        
        # Communication risk
        msg_data = student_profile.get('messages', {})
        if msg_data.get('avg_sentiment_ratio', 1.0) < 0.7:
            risk_factors.append(0.5)
        
        return np.mean(risk_factors) if risk_factors else 0.2
    
    def _identify_trajectory_factors(self, student_profile: Dict) -> List[str]:
        """Identify key factors influencing trajectory."""
        factors = []
        
        lms_data = student_profile.get('lms_activity', {})
        if lms_data.get('activity_frequency_7d', 0) < 5:
            factors.append("Low recent activity")
        
        assign_data = student_profile.get('assignments', {})
        if assign_data.get('late_submission_rate', 0) > 0.3:
            factors.append("High late submission rate")
        
        msg_data = student_profile.get('messages', {})
        if msg_data.get('avg_sentiment_ratio', 1.0) < 0.7:
            factors.append("Declining communication sentiment")
        
        return factors

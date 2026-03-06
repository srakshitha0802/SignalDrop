"""
SignalDrop AI - Early Warning Risk Detection System

A GenAI-powered platform for detecting weak signals and flagging risk momentum
before failure occurs in educational settings.
"""

__version__ = "2.0.0"
__author__ = "SignalDrop AI Team"

from .core import SignalDropSystem
from .data_layer import DataProcessor
from .representation_layer import TemporalEmbedding
from .reasoning_layer import GenAIReasoner
from .risk_layer import RiskScorer
from .explainability_layer import ExplainabilityEngine

# Advanced components
from .advanced_reasoning import AdvancedGenAIReasoner
from .ensemble_predictor import EnsemblePredictor
from .real_time_processor import RealTimeProcessor

__all__ = [
    "SignalDropSystem",
    "DataProcessor", 
    "TemporalEmbedding",
    "GenAIReasoner",
    "RiskScorer",
    "ExplainabilityEngine",
    "AdvancedGenAIReasoner",
    "EnsemblePredictor",
    "RealTimeProcessor"
]

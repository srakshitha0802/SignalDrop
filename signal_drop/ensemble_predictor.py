"""
Ensemble Predictor for SignalDrop AI

Advanced ensemble methods combining multiple models for robust predictions:
- Stacking ensemble with meta-learner
- Bayesian model averaging
- Temporal ensemble with weighted voting
- Adaptive ensemble selection
- Uncertainty quantification through ensembling
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score
from sklearn.calibration import CalibratedClassifierCV
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EnsemblePredictor:
    """Advanced ensemble predictor for robust risk assessment."""
    
    def __init__(self, n_base_models: int = 5):
        self.n_base_models = n_base_models
        self.base_models = {}
        self.meta_learner = None
        self.model_weights = {}
        self.model_performance = {}
        self.uncertainty_estimator = None
        
        # Initialize diverse base models
        self._initialize_base_models()
        
        # Ensemble configuration
        self.ensemble_method = "stacking"  # stacking, voting, bayesian, adaptive
        self.uncertainty_method = "ensemble_variance"  # ensemble_variance, bootstrap, deep_ensemble
        
    def _initialize_base_models(self):
        """Initialize diverse base models for ensemble."""
        
        # Model 1: Random Forest (tree-based)
        self.base_models['random_forest'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        # Model 2: Gradient Boosting (boosted trees)
        self.base_models['gradient_boosting'] = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        # Model 3: Logistic Regression (linear)
        self.base_models['logistic_regression'] = LogisticRegression(
            C=1.0,
            max_iter=1000,
            random_state=42
        )
        
        # Model 4: SVM (kernel-based)
        self.base_models['svm'] = SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            probability=True,
            random_state=42
        )
        
        # Model 5: Neural Network (deep learning)
        self.base_models['neural_network'] = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation='relu',
            solver='adam',
            alpha=0.001,
            learning_rate='adaptive',
            max_iter=1000,
            random_state=42
        )
        
        # Calibrate models for probability estimates
        for name, model in self.base_models.items():
            self.base_models[name] = CalibratedClassifierCV(model, cv=3)
    
    def fit_ensemble(self, X: np.ndarray, y: np.ndarray, 
                    temporal_weights: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Fit ensemble models with temporal weighting."""
        
        training_results = {}
        
        # Apply temporal weights if provided
        if temporal_weights is not None:
            sample_weights = temporal_weights
        else:
            sample_weights = np.ones(len(X))
        
        # Train base models
        base_predictions = []
        
        for name, model in self.base_models.items():
            logger.info(f"Training {name}...")
            
            # Fit model
            model.fit(X, y, sample_weight=sample_weights)
            
            # Get cross-validation performance
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
            self.model_performance[name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'cv_scores': cv_scores.tolist()
            }
            
            # Get predictions for meta-learner
            predictions = model.predict_proba(X)[:, 1]
            base_predictions.append(predictions)
            
            training_results[name] = {
                'trained': True,
                'cv_performance': cv_scores.mean()
            }
        
        # Stack predictions for meta-learner
        stacked_features = np.column_stack(base_predictions)
        
        # Train meta-learner
        self.meta_learner = LogisticRegression(
            C=1.0,
            max_iter=1000,
            random_state=42
        )
        self.meta_learner.fit(stacked_features, y, sample_weight=sample_weights)
        
        # Calculate model weights based on performance
        self._calculate_model_weights()
        
        training_results['meta_learner'] = {'trained': True}
        training_results['ensemble_method'] = self.ensemble_method
        
        return training_results
    
    def predict_ensemble(self, X: np.ndarray, 
                         return_uncertainty: bool = True) -> Dict[str, Any]:
        """Make ensemble predictions with uncertainty quantification."""
        
        if not self.base_models or not self.meta_learner:
            raise ValueError("Ensemble not trained. Call fit_ensemble first.")
        
        # Get base model predictions
        base_predictions = {}
        base_probabilities = {}
        
        for name, model in self.base_models.items():
            predictions = model.predict(X)
            probabilities = model.predict_proba(X)[:, 1]
            
            base_predictions[name] = predictions
            base_probabilities[name] = probabilities
        
        # Ensemble prediction based on method
        if self.ensemble_method == "stacking":
            ensemble_prob, ensemble_pred = self._stacking_prediction(base_probabilities, X)
        elif self.ensemble_method == "voting":
            ensemble_prob, ensemble_pred = self._voting_prediction(base_probabilities)
        elif self.ensemble_method == "bayesian":
            ensemble_prob, ensemble_pred = self._bayesian_prediction(base_probabilities)
        elif self.ensemble_method == "adaptive":
            ensemble_prob, ensemble_pred = self._adaptive_prediction(base_probabilities, X)
        else:
            ensemble_prob, ensemble_pred = self._stacking_prediction(base_probabilities, X)
        
        results = {
            'ensemble_predictions': ensemble_pred,
            'ensemble_probabilities': ensemble_prob,
            'base_predictions': base_predictions,
            'base_probabilities': base_probabilities
        }
        
        # Add uncertainty estimates
        if return_uncertainty:
            uncertainty = self._estimate_uncertainty(base_probabilities, ensemble_prob)
            results['uncertainty'] = uncertainty
        
        return results
    
    def _stacking_prediction(self, base_probabilities: Dict[str, np.ndarray], 
                           X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Stacking ensemble prediction using meta-learner."""
        
        # Stack base predictions
        stacked_features = np.column_stack(list(base_probabilities.values()))
        
        # Meta-learner prediction
        ensemble_prob = self.meta_learner.predict_proba(stacked_features)[:, 1]
        ensemble_pred = (ensemble_prob > 0.5).astype(int)
        
        return ensemble_prob, ensemble_pred
    
    def _voting_prediction(self, base_probabilities: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """Weighted voting ensemble prediction."""
        
        # Calculate weighted average of probabilities
        weighted_prob = np.zeros(len(list(base_probabilities.values())[0]))
        
        for name, prob in base_probabilities.items():
            weight = self.model_weights.get(name, 1.0)
            weighted_prob += prob * weight
        
        # Normalize by total weight
        total_weight = sum(self.model_weights.values())
        ensemble_prob = weighted_prob / total_weight
        ensemble_pred = (ensemble_prob > 0.5).astype(int)
        
        return ensemble_prob, ensemble_pred
    
    def _bayesian_prediction(self, base_probabilities: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """Bayesian model averaging prediction."""
        
        # Use model performance as prior weights
        prior_weights = {}
        total_performance = sum(perf['cv_mean'] for perf in self.model_performance.values())
        
        for name, perf in self.model_performance.items():
            prior_weights[name] = perf['cv_mean'] / total_performance
        
        # Bayesian model averaging
        bayesian_prob = np.zeros(len(list(base_probabilities.values())[0]))
        
        for name, prob in base_probabilities.items():
            weight = prior_weights.get(name, 1.0 / len(base_probabilities))
            bayesian_prob += prob * weight
        
        ensemble_pred = (bayesian_prob > 0.5).astype(int)
        
        return bayesian_prob, ensemble_pred
    
    def _adaptive_prediction(self, base_probabilities: Dict[str, np.ndarray], 
                            X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Adaptive ensemble selection based on data characteristics."""
        
        # Simple adaptive selection based on data variance
        data_variance = np.var(X, axis=1)
        
        # For high variance data, prefer non-linear models
        # For low variance data, prefer linear models
        adaptive_prob = np.zeros(len(list(base_probabilities.values())[0]))
        
        for i in range(len(data_variance)):
            if data_variance[i] > np.median(data_variance):
                # High variance: use tree-based models
                models_to_use = ['random_forest', 'gradient_boosting', 'neural_network']
            else:
                # Low variance: use linear models
                models_to_use = ['logistic_regression', 'svm']
            
            # Average selected models
            selected_probs = [base_probabilities[name][i] for name in models_to_use]
            adaptive_prob[i] = np.mean(selected_probs)
        
        ensemble_pred = (adaptive_prob > 0.5).astype(int)
        
        return adaptive_prob, ensemble_pred
    
    def _calculate_model_weights(self):
        """Calculate model weights based on cross-validation performance."""
        
        # Use inverse of performance variance as weight
        for name, perf in self.model_performance.items():
            # Higher performance = higher weight
            # Lower variance = higher weight
            weight = perf['cv_mean'] / (perf['cv_std'] + 1e-6)
            self.model_weights[name] = weight
        
        # Normalize weights
        total_weight = sum(self.model_weights.values())
        for name in self.model_weights:
            self.model_weights[name] /= total_weight
    
    def _estimate_uncertainty(self, base_probabilities: Dict[str, np.ndarray], 
                            ensemble_prob: np.ndarray) -> Dict[str, Any]:
        """Estimate prediction uncertainty."""
        
        uncertainty = {}
        
        if self.uncertainty_method == "ensemble_variance":
            # Variance across base model predictions
            prob_matrix = np.column_stack(list(base_probabilities.values()))
            variance = np.var(prob_matrix, axis=1)
            
            uncertainty['type'] = 'ensemble_variance'
            uncertainty['values'] = variance
            uncertainty['mean_uncertainty'] = np.mean(variance)
            
        elif self.uncertainty_method == "bootstrap":
            # Bootstrap uncertainty estimation
            bootstrap_uncertainty = self._bootstrap_uncertainty(base_probabilities)
            uncertainty.update(bootstrap_uncertainty)
            
        elif self.uncertainty_method == "deep_ensemble":
            # Deep ensemble uncertainty (simplified)
            uncertainty['type'] = 'deep_ensemble'
            uncertainty['values'] = np.abs(ensemble_prob - 0.5) * 2  # Distance from decision boundary
            uncertainty['mean_uncertainty'] = np.mean(uncertainty['values'])
        
        else:
            uncertainty['type'] = 'ensemble_variance'
            uncertainty['values'] = np.zeros(len(ensemble_prob))
            uncertainty['mean_uncertainty'] = 0.0
        
        return uncertainty
    
    def _bootstrap_uncertainty(self, base_probabilities: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Bootstrap uncertainty estimation."""
        
        # Simplified bootstrap uncertainty
        prob_matrix = np.column_stack(list(base_probabilities.values()))
        
        # Calculate bootstrap statistics
        bootstrap_mean = np.mean(prob_matrix, axis=1)
        bootstrap_std = np.std(prob_matrix, axis=1)
        
        return {
            'type': 'bootstrap',
            'values': bootstrap_std,
            'mean_uncertainty': np.mean(bootstrap_std),
            'bootstrap_mean': bootstrap_mean
        }
    
    def temporal_ensemble_prediction(self, X_history: List[np.ndarray], 
                                    y_history: List[np.ndarray],
                                    X_current: np.ndarray,
                                    decay_factor: float = 0.9) -> Dict[str, Any]:
        """Temporal ensemble prediction with historical weighting."""
        
        if len(X_history) != len(y_history):
            raise ValueError("X_history and y_history must have same length")
        
        # Train models on historical data with temporal weighting
        temporal_weights = []
        for i, (X_hist, y_hist) in enumerate(zip(X_history, y_history)):
            # More recent data gets higher weight
            weight = decay_factor ** (len(X_history) - i - 1)
            temporal_weights.extend([weight] * len(X_hist))
        
        # Combine all historical data
        X_combined = np.vstack(X_history)
        y_combined = np.hstack(y_history)
        
        # Fit ensemble with temporal weights
        self.fit_ensemble(X_combined, y_combined, np.array(temporal_weights))
        
        # Predict on current data
        predictions = self.predict_ensemble(X_current)
        
        # Add temporal information
        predictions['temporal_info'] = {
            'historical_periods': len(X_history),
            'decay_factor': decay_factor,
            'temporal_weights_applied': True
        }
        
        return predictions
    
    def get_ensemble_insights(self) -> Dict[str, Any]:
        """Get insights about ensemble performance and model contributions."""
        
        insights = {
            'ensemble_method': self.ensemble_method,
            'uncertainty_method': self.uncertainty_method,
            'model_count': len(self.base_models),
            'model_performance': self.model_performance,
            'model_weights': self.model_weights
        }
        
        # Calculate ensemble diversity
        if self.model_performance:
            performances = [perf['cv_mean'] for perf in self.model_performance.values()]
            insights['ensemble_diversity'] = {
                'performance_range': max(performances) - min(performances),
                'performance_std': np.std(performances),
                'mean_performance': np.mean(performances)
            }
        
        # Model contribution analysis
        if self.model_weights:
            insights['model_contributions'] = {
                'highest_weight': max(self.model_weights.items(), key=lambda x: x[1]),
                'lowest_weight': min(self.model_weights.items(), key=lambda x: x[1]),
                'weight_distribution': self.model_weights
            }
        
        return insights
    
    def update_ensemble(self, X_new: np.ndarray, y_new: np.ndarray, 
                       learning_rate: float = 0.1) -> Dict[str, Any]:
        """Update ensemble with new data (online learning)."""
        
        update_results = {}
        
        # Update each base model
        for name, model in self.base_models.items():
            # For models that support partial_fit
            if hasattr(model, 'partial_fit'):
                model.partial_fit(X_new, y_new)
                update_results[name] = {'updated': True, 'method': 'partial_fit'}
            else:
                # Retrain models that don't support partial_fit
                # In practice, would maintain data buffer
                update_results[name] = {'updated': False, 'method': 'retrain_required'}
        
        # Update meta-learner
        if self.meta_learner:
            # Get new base predictions
            new_base_predictions = []
            for model in self.base_models.values():
                if hasattr(model, 'predict_proba'):
                    new_base_predictions.append(model.predict_proba(X_new)[:, 1])
            
            if new_base_predictions:
                new_stacked_features = np.column_stack(new_base_predictions)
                
                # Update meta-learner
                if hasattr(self.meta_learner, 'partial_fit'):
                    self.meta_learner.partial_fit(new_stacked_features, y_new)
                    update_results['meta_learner'] = {'updated': True, 'method': 'partial_fit'}
                else:
                    update_results['meta_learner'] = {'updated': False, 'method': 'retrain_required'}
        
        return update_results
    
    def save_ensemble(self, filepath: str) -> bool:
        """Save ensemble model to file."""
        try:
            import pickle
            
            ensemble_data = {
                'base_models': self.base_models,
                'meta_learner': self.meta_learner,
                'model_weights': self.model_weights,
                'model_performance': self.model_performance,
                'ensemble_method': self.ensemble_method,
                'uncertainty_method': self.uncertainty_method
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(ensemble_data, f)
            
            return True
        except Exception as e:
            logger.error(f"Error saving ensemble: {e}")
            return False
    
    def load_ensemble(self, filepath: str) -> bool:
        """Load ensemble model from file."""
        try:
            import pickle
            
            with open(filepath, 'rb') as f:
                ensemble_data = pickle.load(f)
            
            self.base_models = ensemble_data['base_models']
            self.meta_learner = ensemble_data['meta_learner']
            self.model_weights = ensemble_data['model_weights']
            self.model_performance = ensemble_data['model_performance']
            self.ensemble_method = ensemble_data['ensemble_method']
            self.uncertainty_method = ensemble_data['uncertainty_method']
            
            return True
        except Exception as e:
            logger.error(f"Error loading ensemble: {e}")
            return False

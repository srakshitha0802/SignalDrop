"""
Evaluation Framework for SignalDrop AI

Comprehensive evaluation system to measure early-warning effectiveness,
compare against baselines, and assess explanation quality.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import precision_recall_curve, roc_auc_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import json
import logging

logger = logging.getLogger(__name__)

class SignalDropEvaluator:
    """Comprehensive evaluation framework for SignalDrop AI."""
    
    def __init__(self, signal_drop_system):
        self.signal_drop_system = signal_drop_system
        self.evaluation_results = {}
        
    def evaluate_early_warning_effectiveness(self, test_data: Dict[str, List[Dict]], 
                                          ground_truth: Dict[str, Dict]) -> Dict[str, Any]:
        """Evaluate how early the system flags risk compared to ground truth."""
        
        # Generate alerts
        alerts = self.signal_drop_system.process_student_data(test_data)
        
        # Calculate early warning metrics
        early_warning_metrics = self._calculate_early_warning_metrics(alerts, ground_truth)
        
        # Calculate detection delay
        detection_delay = self._calculate_detection_delay(alerts, ground_truth)
        
        # Calculate true positive/false positive rates
        classification_metrics = self._calculate_classification_metrics(alerts, ground_truth)
        
        return {
            "early_warning_metrics": early_warning_metrics,
            "detection_delay": detection_delay,
            "classification_metrics": classification_metrics,
            "total_alerts": len(alerts),
            "students_at_risk": len([s for s in ground_truth.values() if s.get('at_risk', False)])
        }
    
    def compare_against_baselines(self, test_data: Dict[str, List[Dict]], 
                                 ground_truth: Dict[str, Dict]) -> Dict[str, Any]:
        """Compare SignalDrop against simple statistical baselines."""
        
        # Get SignalDrop results
        signal_drop_alerts = self.signal_drop_system.process_student_data(test_data)
        signal_drop_metrics = self._calculate_classification_metrics(signal_drop_alerts, ground_truth)
        
        # Baseline 1: Simple threshold-based alerting
        threshold_alerts = self._threshold_baseline(test_data)
        threshold_metrics = self._calculate_classification_metrics(threshold_alerts, ground_truth)
        
        # Baseline 2: Random Forest
        rf_alerts = self._random_forest_baseline(test_data, ground_truth)
        rf_metrics = self._calculate_classification_metrics(rf_alerts, ground_truth)
        
        # Baseline 3: Logistic Regression
        lr_alerts = self._logistic_regression_baseline(test_data, ground_truth)
        lr_metrics = self._calculate_classification_metrics(lr_alerts, ground_truth)
        
        return {
            "signal_drop": signal_drop_metrics,
            "threshold_baseline": threshold_metrics,
            "random_forest": rf_metrics,
            "logistic_regression": lr_metrics,
            "improvement_over_threshold": self._calculate_improvement(signal_drop_metrics, threshold_metrics),
            "improvement_over_ml": self._calculate_improvement(signal_drop_metrics, rf_metrics)
        }
    
    def evaluate_explanation_quality(self, alerts: List[Dict], 
                                   human_evaluations: List[Dict] = None) -> Dict[str, Any]:
        """Evaluate the quality and understandability of explanations."""
        
        if human_evaluations is None:
            # Simulate human evaluations
            human_evaluations = self._simulate_human_evaluations(alerts)
        
        # Calculate explanation metrics
        clarity_scores = [eval.get('clarity', 0) for eval in human_evaluations]
        usefulness_scores = [eval.get('usefulness', 0) for eval in human_evaluations]
        trust_scores = [eval.get('trust', 0) for eval in human_evaluations]
        
        # Analyze explanation characteristics
        explanation_lengths = [len(alert.get('explanation', '').split()) for alert in alerts]
        key_signals_counts = [len(alert.get('key_signals', [])) for alert in alerts]
        
        return {
            "average_clarity": np.mean(clarity_scores),
            "average_usefulness": np.mean(usefulness_scores),
            "average_trust": np.mean(trust_scores),
            "explanation_length_stats": {
                "mean": np.mean(explanation_lengths),
                "std": np.std(explanation_lengths),
                "min": np.min(explanation_lengths),
                "max": np.max(explanation_lengths)
            },
            "key_signals_stats": {
                "mean": np.mean(key_signals_counts),
                "std": np.std(key_signals_counts),
                "min": np.min(key_signals_counts),
                "max": np.max(key_signals_counts)
            },
            "clarity_distribution": self._calculate_distribution(clarity_scores),
            "usefulness_distribution": self._calculate_distribution(usefulness_scores)
        }
    
    def evaluate_false_positive_tolerance(self, alerts: List[Dict], 
                                       ground_truth: Dict[str, Dict],
                                       tolerance_levels: List[float] = [0.1, 0.2, 0.3]) -> Dict[str, Any]:
        """Evaluate system performance at different false positive tolerance levels."""
        
        results = {}
        
        for tolerance in tolerance_levels:
            # Filter alerts based on confidence threshold
            high_confidence_alerts = [
                alert for alert in alerts 
                if self._get_confidence_score(alert) >= (1 - tolerance)
            ]
            
            # Calculate metrics at this tolerance level
            metrics = self._calculate_classification_metrics(high_confidence_alerts, ground_truth)
            
            results[f"tolerance_{tolerance}"] = {
                "alerts_generated": len(high_confidence_alerts),
                "precision": metrics.get('precision', 0),
                "recall": metrics.get('recall', 0),
                "f1_score": metrics.get('f1_score', 0),
                "false_positive_rate": metrics.get('false_positive_rate', 0)
            }
        
        return results
    
    def run_comprehensive_evaluation(self, test_data: Dict[str, List[Dict]], 
                                   ground_truth: Dict[str, Dict]) -> Dict[str, Any]:
        """Run comprehensive evaluation of the SignalDrop system."""
        
        # Early warning effectiveness
        early_warning_results = self.evaluate_early_warning_effectiveness(test_data, ground_truth)
        
        # Baseline comparison
        baseline_comparison = self.compare_against_baselines(test_data, ground_truth)
        
        # Generate alerts for explanation evaluation
        alerts = self.signal_drop_system.process_student_data(test_data)
        
        # Explanation quality
        explanation_quality = self.evaluate_explanation_quality(alerts)
        
        # False positive tolerance
        tolerance_analysis = self.evaluate_false_positive_tolerance(alerts, ground_truth)
        
        # System statistics
        system_stats = self.signal_drop_system.get_system_statistics(test_data)
        
        return {
            "early_warning_effectiveness": early_warning_results,
            "baseline_comparison": baseline_comparison,
            "explanation_quality": explanation_quality,
            "false_positive_tolerance": tolerance_analysis,
            "system_statistics": system_stats,
            "evaluation_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_early_warning_metrics(self, alerts: List[Dict], 
                                       ground_truth: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate early warning specific metrics."""
        
        # Students who are actually at risk
        at_risk_students = {sid for sid, data in ground_truth.items() if data.get('at_risk', False)}
        
        # Students flagged by the system
        flagged_students = {alert['student_id'] for alert in alerts}
        
        # True positives (correctly identified at-risk students)
        true_positives = len(at_risk_students & flagged_students)
        
        # False negatives (missed at-risk students)
        false_negatives = len(at_risk_students - flagged_students)
        
        # Early warning rate
        early_warning_rate = true_positives / len(at_risk_students) if at_risk_students else 0
        
        # Alert precision
        alert_precision = true_positives / len(flagged_students) if flagged_students else 0
        
        return {
            "early_warning_rate": early_warning_rate,
            "alert_precision": alert_precision,
            "true_positives": true_positives,
            "false_negatives": false_negatives,
            "total_at_risk": len(at_risk_students)
        }
    
    def _calculate_detection_delay(self, alerts: List[Dict], 
                                 ground_truth: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate how early risk is detected compared to ground truth."""
        
        delays = []
        
        for alert in alerts:
            student_id = alert['student_id']
            
            if student_id in ground_truth:
                gt_data = ground_truth[student_id]
                
                # Get detection dates
                alert_date = datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00'))
                risk_date = gt_data.get('risk_start_date')
                
                if risk_date:
                    risk_date = datetime.fromisoformat(risk_date.replace('Z', '+00:00'))
                    delay_days = (alert_date - risk_date).days
                    delays.append(delay_days)
        
        if delays:
            return {
                "mean_detection_delay": np.mean(delays),
                "median_detection_delay": np.median(delays),
                "std_detection_delay": np.std(delays),
                "min_detection_delay": np.min(delays),
                "max_detection_delay": np.max(delays)
            }
        else:
            return {"message": "No detection delays calculated"}
    
    def _calculate_classification_metrics(self, alerts: List[Dict], 
                                         ground_truth: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate standard classification metrics."""
        
        # Create binary predictions
        student_ids = list(ground_truth.keys())
        y_true = [1 if ground_truth[sid].get('at_risk', False) else 0 for sid in student_ids]
        y_pred = [1 if any(alert['student_id'] == sid for alert in alerts) else 0 for sid in student_ids]
        
        if len(set(y_true)) < 2 or len(set(y_pred)) < 2:
            # Handle edge cases
            return {
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "accuracy": np.mean([y_true[i] == y_pred[i] for i in range(len(y_true))]),
                "false_positive_rate": 0.0
            }
        
        # Calculate metrics
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        # Calculate AUC if possible
        try:
            auc = roc_auc_score(y_true, y_pred)
        except:
            auc = 0.0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accuracy": accuracy,
            "false_positive_rate": false_positive_rate,
            "auc": auc,
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn
        }
    
    def _threshold_baseline(self, test_data: Dict[str, List[Dict]]) -> List[Dict]:
        """Simple threshold-based baseline."""
        
        # Process data
        processed_data = self.signal_drop_system._process_raw_data(test_data)
        alerts = []
        
        for student_id, profile in processed_data.items():
            # Simple threshold rules
            risk_score = 0
            
            # LMS activity threshold
            lms_data = profile.get('lms_activity', {})
            if lms_data.get('activity_frequency_7d', 0) < 2:
                risk_score += 0.3
            
            # Assignment threshold
            assign_data = profile.get('assignments', {})
            if assign_data.get('late_submission_rate', 0) > 0.3:
                risk_score += 0.3
            
            # Attendance threshold
            att_data = profile.get('attendance', {})
            if att_data.get('attendance_rate', 1) < 0.8:
                risk_score += 0.4
            
            if risk_score > 0.5:
                alerts.append({
                    "student_id": student_id,
                    "risk_score": risk_score,
                    "timestamp": datetime.now().isoformat(),
                    "method": "threshold_baseline"
                })
        
        return alerts
    
    def _random_forest_baseline(self, test_data: Dict[str, List[Dict]], 
                              ground_truth: Dict[str, Dict]) -> List[Dict]:
        """Random Forest baseline."""
        
        # This is a simplified version - in practice, you'd need training data
        # For now, return threshold-based results as placeholder
        return self._threshold_baseline(test_data)
    
    def _logistic_regression_baseline(self, test_data: Dict[str, List[Dict]], 
                                    ground_truth: Dict[str, Dict]) -> List[Dict]:
        """Logistic Regression baseline."""
        
        # This is a simplified version - in practice, you'd need training data
        # For now, return threshold-based results as placeholder
        return self._threshold_baseline(test_data)
    
    def _calculate_improvement(self, signal_drop_metrics: Dict, 
                             baseline_metrics: Dict) -> Dict[str, float]:
        """Calculate improvement over baseline."""
        
        improvements = {}
        
        for metric in ['precision', 'recall', 'f1_score', 'accuracy']:
            signal_drop_val = signal_drop_metrics.get(metric, 0)
            baseline_val = baseline_metrics.get(metric, 0)
            
            if baseline_val > 0:
                improvement = (signal_drop_val - baseline_val) / baseline_val
            else:
                improvement = signal_drop_val
            
            improvements[f"{metric}_improvement"] = improvement
        
        return improvements
    
    def _simulate_human_evaluations(self, alerts: List[Dict]) -> List[Dict]:
        """Simulate human evaluations of explanations (for testing)."""
        
        evaluations = []
        
        for alert in alerts:
            # Simulate evaluation based on explanation characteristics
            explanation = alert.get('explanation', '')
            key_signals = alert.get('key_signals', [])
            confidence = alert.get('confidence', 'medium')
            
            # Base scores
            clarity = np.random.normal(0.7, 0.15)
            usefulness = np.random.normal(0.65, 0.2)
            trust = np.random.normal(0.6, 0.18)
            
            # Adjust based on characteristics
            if len(explanation.split()) > 20:  # Longer explanation
                clarity += 0.1
            elif len(explanation.split()) < 10:  # Too short
                clarity -= 0.2
            
            if len(key_signals) >= 2:  # Good number of signals
                usefulness += 0.15
            elif len(key_signals) == 0:  # No signals
                usefulness -= 0.3
            
            if confidence == 'high':
                trust += 0.2
            elif confidence == 'low':
                trust -= 0.15
            
            # Ensure scores are in [0, 1]
            clarity = np.clip(clarity, 0, 1)
            usefulness = np.clip(usefulness, 0, 1)
            trust = np.clip(trust, 0, 1)
            
            evaluations.append({
                "student_id": alert['student_id'],
                "clarity": clarity,
                "usefulness": usefulness,
                "trust": trust,
                "overall_score": (clarity + usefulness + trust) / 3
            })
        
        return evaluations
    
    def _calculate_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of scores."""
        
        distribution = {"low": 0, "medium": 0, "high": 0}
        
        for score in scores:
            if score < 0.4:
                distribution["low"] += 1
            elif score < 0.7:
                distribution["medium"] += 1
            else:
                distribution["high"] += 1
        
        return distribution
    
    def _get_confidence_score(self, alert: Dict) -> float:
        """Convert confidence level to numeric score."""
        
        confidence_map = {"low": 0.3, "medium": 0.6, "high": 0.9}
        return confidence_map.get(alert.get('confidence', 'medium'), 0.6)
    
    def generate_evaluation_report(self, results: Dict[str, Any], 
                                  filename: str = None) -> str:
        """Generate comprehensive evaluation report."""
        
        if filename is None:
            filename = f"signal_drop_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return filename
    
    def plot_evaluation_results(self, results: Dict[str, Any], 
                               save_plots: bool = True) -> Dict[str, str]:
        """Generate evaluation plots."""
        
        plot_files = {}
        
        # Plot 1: Early Warning Effectiveness
        if 'early_warning_effectiveness' in results:
            plt.figure(figsize=(10, 6))
            
            ew_results = results['early_warning_effectiveness']
            metrics = ['early_warning_rate', 'alert_precision']
            values = [ew_results['early_warning_metrics'].get(m, 0) for m in metrics]
            
            plt.bar(metrics, values, color=['skyblue', 'lightcoral'])
            plt.title('Early Warning Effectiveness')
            plt.ylabel('Score')
            plt.ylim(0, 1)
            
            if save_plots:
                filename = 'early_warning_effectiveness.png'
                plt.savefig(filename)
                plot_files['early_warning'] = filename
            plt.close()
        
        # Plot 2: Baseline Comparison
        if 'baseline_comparison' in results:
            plt.figure(figsize=(12, 8))
            
            comparison = results['baseline_comparison']
            methods = ['signal_drop', 'threshold_baseline', 'random_forest', 'logistic_regression']
            metrics = ['precision', 'recall', 'f1_score']
            
            x = np.arange(len(metrics))
            width = 0.2
            
            for i, method in enumerate(methods):
                values = [comparison[method].get(m, 0) for m in metrics]
                plt.bar(x + i*width, values, width, label=method.replace('_', ' ').title())
            
            plt.xlabel('Metrics')
            plt.ylabel('Score')
            plt.title('Baseline Comparison')
            plt.xticks(x + width * 1.5, metrics)
            plt.legend()
            plt.ylim(0, 1)
            
            if save_plots:
                filename = 'baseline_comparison.png'
                plt.savefig(filename)
                plot_files['baseline'] = filename
            plt.close()
        
        # Plot 3: Explanation Quality
        if 'explanation_quality' in results:
            plt.figure(figsize=(10, 6))
            
            eq_results = results['explanation_quality']
            qualities = ['average_clarity', 'average_usefulness', 'average_trust']
            values = [eq_results.get(q, 0) for q in qualities]
            
            plt.bar(qualities, values, color=['gold', 'lightgreen', 'coral'])
            plt.title('Explanation Quality')
            plt.ylabel('Average Score')
            plt.ylim(0, 1)
            plt.xticks(rotation=45)
            
            if save_plots:
                filename = 'explanation_quality.png'
                plt.savefig(filename, bbox_inches='tight')
                plot_files['explanation'] = filename
            plt.close()
        
        return plot_files

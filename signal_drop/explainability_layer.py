"""
Explainability Layer - Natural Language Justifications

Generates natural language explanations for risk alerts, including
key contributing signals, uncertainty quantification, and limitations.
"""

import openai
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ExplainabilityEngine:
    """Generates explainable justifications for risk alerts."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: str = None):
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=api_key) if api_key else None
        
        # Explanation templates for different risk patterns
        self.explanation_templates = {
            'engagement_decay': [
                "Student shows declining engagement with {activity_level} LMS activity over the past {timeframe}.",
                "Reduced platform interaction suggests potential disengagement.",
                "Activity frequency has decreased by {percentage}% compared to baseline."
            ],
            'academic_decline': [
                "Assignment submissions show concerning patterns with {late_rate}% late submissions.",
                "Recent work quality indicates {quality_trend} in academic performance.",
                "Average submission delay of {delay_hours} hours suggests time management challenges."
            ],
            'communication_shift': [
                "Communication patterns reveal {sentiment_trend} in student sentiment.",
                "Message frequency has {frequency_change} over the past {timeframe}.",
                "Sentiment analysis shows {sentiment_description} in recent interactions."
            ],
            'attendance_decline': [
                "Attendance record shows {attendance_trend} with {attendance_rate}% overall attendance.",
                "Recent attendance has declined by {decline_percentage}% compared to baseline.",
                "Pattern of {absence_pattern} suggests emerging disengagement."
            ]
        }
    
    def generate_explanation(self, student_id: str, risk_assessment: Dict,
                           student_profile: Dict, narrative_analysis: Dict) -> Dict[str, Any]:
        """Generate comprehensive explanation for risk alert."""
        
        # Identify key contributing signals
        key_signals = self._identify_key_signals(risk_assessment, student_profile)
        
        # Generate natural language explanation
        explanation = self._generate_natural_language_explanation(
            risk_assessment, student_profile, narrative_analysis, key_signals
        )
        
        # Quantify uncertainty
        uncertainty = self._quantify_uncertainty(risk_assessment, student_profile)
        
        # Identify limitations
        limitations = self._identify_limitations(student_profile, risk_assessment)
        
        # Provide actionable insights
        actionable_insights = self._generate_actionable_insights(key_signals, risk_assessment)
        
        return {
            "student_id": student_id,
            "risk_momentum": risk_assessment.get('risk_momentum', 'stable'),
            "confidence": risk_assessment.get('confidence', 'low'),
            "key_signals": key_signals,
            "explanation": explanation,
            "uncertainty": uncertainty,
            "limitations": limitations,
            "actionable_insights": actionable_insights,
            "timestamp": datetime.now().isoformat()
        }
    
    def _identify_key_signals(self, risk_assessment: Dict, student_profile: Dict) -> List[str]:
        """Identify the most significant contributing signals."""
        
        key_signals = []
        risk_components = risk_assessment.get('risk_components', {})
        
        # Sort components by risk score
        sorted_components = sorted(
            risk_components.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Generate signal descriptions for top components
        for component, score in sorted_components[:3]:  # Top 3 signals
            if score > 0.3:  # Only include significant signals
                signal_desc = self._generate_signal_description(component, score, student_profile)
                if signal_desc:
                    key_signals.append(signal_desc)
        
        return key_signals
    
    def _generate_signal_description(self, component: str, score: float, 
                                   student_profile: Dict) -> Optional[str]:
        """Generate human-readable description for a risk signal."""
        
        if component == 'engagement_decay':
            lms_data = student_profile.get('lms_activity', {})
            activity_7d = lms_data.get('activity_frequency_7d', 0)
            activity_14d = lms_data.get('activity_frequency_14d', 0)
            
            if activity_7d <= 2:
                return f"Very low LMS activity ({activity_7d} sessions in 7 days)"
            elif activity_14d > 0 and activity_7d / activity_14d < 0.5:
                decline_pct = int((1 - activity_7d / activity_14d) * 100)
                return f"Decline in LMS activity over 14 days ({decline_pct}% drop)"
        
        elif component == 'academic_decline':
            assign_data = student_profile.get('assignments', {})
            late_rate = assign_data.get('late_submission_rate', 0)
            recent_late = assign_data.get('recent_late_rate', 0)
            
            if recent_late > 0.4:
                return f"High recent late submission rate ({int(recent_late * 100)}%)"
            elif late_rate > 0.3:
                return f"Elevated late submission pattern ({int(late_rate * 100)}%)"
        
        elif component == 'communication_shift':
            msg_data = student_profile.get('messages', {})
            if msg_data.get('recent_sentiment_decline', False):
                return "Negative sentiment shift in messages"
            elif msg_data.get('avg_sentiment_ratio', 1) < 0.6:
                return "Low sentiment ratio in communications"
        
        elif component == 'attendance_decline':
            att_data = student_profile.get('attendance', {})
            recent_rate = att_data.get('recent_attendance_rate', 1)
            overall_rate = att_data.get('attendance_rate', 1)
            
            if recent_rate < overall_rate - 0.15:
                decline_pct = int((overall_rate - recent_rate) * 100)
                return f"Attendance decline ({decline_pct}% drop in recent period)"
            elif recent_rate < 0.8:
                return f"Low recent attendance rate ({int(recent_rate * 100)}%)"
        
        return None
    
    def _generate_natural_language_explanation(self, risk_assessment: Dict,
                                              student_profile: Dict,
                                              narrative_analysis: Dict,
                                              key_signals: List[str]) -> str:
        """Generate comprehensive natural language explanation."""
        
        if not self.client:
            return self._generate_fallback_explanation(risk_assessment, key_signals)
        
        try:
            # Prepare context for LLM
            context = self._prepare_explanation_context(
                risk_assessment, student_profile, narrative_analysis, key_signals
            )
            
            prompt = f"""
            Generate a clear, concise explanation for an early-warning risk alert about a student.
            
            Context:
            {context}
            
            Guidelines:
            - Focus on patterns and trends, not just individual metrics
            - Use clear, non-technical language suitable for educators
            - Emphasize early-warning nature (not definitive predictions)
            - Include temporal context (how patterns evolved)
            - Be specific about what changed and why it matters
            - Keep explanation under 150 words
            
            Generate the explanation:
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert educational analyst explaining early-warning alerts to teachers and administrators."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM explanation generation failed: {e}")
            return self._generate_fallback_explanation(risk_assessment, key_signals)
    
    def _generate_fallback_explanation(self, risk_assessment: Dict, 
                                     key_signals: List[str]) -> str:
        """Generate fallback explanation without LLM."""
        
        risk_score = risk_assessment.get('risk_score', 0.0)
        momentum = risk_assessment.get('risk_momentum', 'stable')
        
        if not key_signals:
            return "Limited data available for comprehensive risk assessment."
        
        # Build explanation based on key signals
        explanation_parts = []
        
        if momentum == "increasing":
            explanation_parts.append("Multiple risk indicators show an accelerating pattern of disengagement.")
        elif momentum == "decreasing":
            explanation_parts.append("Risk indicators show some improvement, though concerns remain.")
        else:
            explanation_parts.append("Several risk indicators suggest emerging disengagement patterns.")
        
        # Add key signals
        if len(key_signals) == 1:
            explanation_parts.append(f"Primary concern: {key_signals[0].lower()}.")
        else:
            explanation_parts.append(f"Key concerns include: {', '.join([s.lower() for s in key_signals[:2]])}.")
        
        # Add risk level context
        if risk_score > 0.7:
            explanation_parts.append("These patterns suggest high risk of academic disengagement if no intervention occurs.")
        elif risk_score > 0.4:
            explanation_parts.append("These patterns indicate moderate risk that may escalate without attention.")
        else:
            explanation_parts.append("These patterns suggest low to moderate risk requiring monitoring.")
        
        return " ".join(explanation_parts)
    
    def _prepare_explanation_context(self, risk_assessment: Dict, student_profile: Dict,
                                   narrative_analysis: Dict, key_signals: List[str]) -> str:
        """Prepare context for explanation generation."""
        
        context_parts = []
        
        # Risk assessment summary
        risk_score = risk_assessment.get('risk_score', 0.0)
        momentum = risk_assessment.get('risk_momentum', 'stable')
        confidence = risk_assessment.get('confidence', 'low')
        
        context_parts.append(f"Risk Score: {risk_score:.2f}")
        context_parts.append(f"Risk Momentum: {momentum}")
        context_parts.append(f"Confidence Level: {confidence}")
        
        # Key signals
        if key_signals:
            context_parts.append(f"Key Signals: {', '.join(key_signals)}")
        
        # Narrative insights
        if narrative_analysis:
            trajectory = narrative_analysis.get('engagement_trajectory', 'stable')
            summary = narrative_analysis.get('summary', '')
            if summary:
                context_parts.append(f"Narrative: {summary}")
        
        # Recent data patterns
        lms_data = student_profile.get('lms_activity', {})
        if lms_data:
            context_parts.append(f"LMS Activity: {lms_data.get('activity_frequency_7d', 0)} sessions (7 days), "
                               f"{lms_data.get('activity_frequency_14d', 0)} sessions (14 days)")
        
        assign_data = student_profile.get('assignments', {})
        if assign_data:
            context_parts.append(f"Assignments: {assign_data.get('late_submission_rate', 0):.1%} late rate")
        
        msg_data = student_profile.get('messages', {})
        if msg_data:
            context_parts.append(f"Communication: {msg_data.get('total_messages', 0)} messages, "
                               f"sentiment ratio: {msg_data.get('avg_sentiment_ratio', 1):.2f}")
        
        att_data = student_profile.get('attendance', {})
        if att_data:
            context_parts.append(f"Attendance: {att_data.get('attendance_rate', 0):.1%} rate")
        
        return "\n".join(context_parts)
    
    def _quantify_uncertainty(self, risk_assessment: Dict, student_profile: Dict) -> Dict[str, Any]:
        """Quantify uncertainty in the risk assessment."""
        
        uncertainty_factors = {}
        
        # Data completeness uncertainty
        data_sources = ['lms_activity', 'assignments', 'messages', 'attendance']
        available_sources = sum(1 for source in data_sources if student_profile.get(source))
        completeness_score = available_sources / len(data_sources)
        
        uncertainty_factors['data_completeness'] = {
            'score': completeness_score,
            'uncertainty_level': 'low' if completeness_score > 0.8 else 'medium' if completeness_score > 0.5 else 'high',
            'missing_sources': [source for source in data_sources if not student_profile.get(source)]
        }
        
        # Temporal uncertainty
        recent_activity = self._check_data_recency(student_profile)
        uncertainty_factors['temporal_recency'] = {
            'score': recent_activity['recency_score'],
            'uncertainty_level': recent_activity['uncertainty_level'],
            'oldest_data_days': recent_activity['oldest_data_days']
        }
        
        # Model confidence uncertainty
        confidence = risk_assessment.get('confidence', 'low')
        confidence_scores = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
        model_confidence = confidence_scores.get(confidence, 0.3)
        
        uncertainty_factors['model_confidence'] = {
            'score': model_confidence,
            'uncertainty_level': confidence,
            'confidence_factors': self._identify_confidence_factors(risk_assessment)
        }
        
        # Overall uncertainty
        overall_score = np.mean([
            completeness_score,
            recent_activity['recency_score'],
            model_confidence
        ])
        
        overall_uncertainty = {
            'overall_score': overall_score,
            'uncertainty_level': 'low' if overall_score > 0.7 else 'medium' if overall_score > 0.4 else 'high',
            'primary_factors': self._identify_primary_uncertainty_factors(uncertainty_factors)
        }
        
        return {
            'overall': overall_uncertainty,
            'factors': uncertainty_factors
        }
    
    def _check_data_recency(self, student_profile: Dict) -> Dict[str, Any]:
        """Check recency of student data."""
        
        current_date = datetime.now()
        oldest_data_days = 0
        recency_scores = []
        
        # Check each data source for recency
        for source_type, source_key in [
            ('lms_activity', 'last_activity'),
            ('assignments', 'last_submission'),
            ('messages', 'last_message'),
            ('attendance', 'last_attendance')
        ]:
            source_data = student_profile.get(source_type, {})
            if source_key in source_data and source_data[source_key]:
                days_old = (current_date - source_data[source_key]).days
                oldest_data_days = max(oldest_data_days, days_old)
                
                # Score based on recency (more recent = higher score)
                if days_old <= 7:
                    recency_scores.append(1.0)
                elif days_old <= 14:
                    recency_scores.append(0.8)
                elif days_old <= 30:
                    recency_scores.append(0.6)
                else:
                    recency_scores.append(0.3)
        
        if not recency_scores:
            return {'recency_score': 0.0, 'uncertainty_level': 'high', 'oldest_data_days': 999}
        
        recency_score = np.mean(recency_scores)
        uncertainty_level = 'low' if recency_score > 0.7 else 'medium' if recency_score > 0.4 else 'high'
        
        return {
            'recency_score': recency_score,
            'uncertainty_level': uncertainty_level,
            'oldest_data_days': oldest_data_days
        }
    
    def _identify_confidence_factors(self, risk_assessment: Dict) -> List[str]:
        """Identify factors affecting model confidence."""
        
        factors = []
        risk_components = risk_assessment.get('risk_components', {})
        
        # Check for weak signals
        weak_signals = [comp for comp, score in risk_components.items() if 0.1 < score < 0.3]
        if weak_signals:
            factors.append("Multiple weak signals detected")
        
        # Check for conflicting signals
        high_risk = [comp for comp, score in risk_components.items() if score > 0.6]
        low_risk = [comp for comp, score in risk_components.items() if score < 0.2]
        
        if high_risk and low_risk:
            factors.append("Mixed risk signals across domains")
        
        # Check for single-source risk
        if len(high_risk) == 1:
            factors.append("Risk concentrated in single domain")
        
        return factors
    
    def _identify_primary_uncertainty_factors(self, uncertainty_factors: Dict) -> List[str]:
        """Identify primary sources of uncertainty."""
        
        primary_factors = []
        
        for factor_name, factor_data in uncertainty_factors.items():
            if factor_data['uncertainty_level'] == 'high':
                if factor_name == 'data_completeness':
                    primary_factors.append("Incomplete data coverage")
                elif factor_name == 'temporal_recency':
                    primary_factors.append("Stale data patterns")
                elif factor_name == 'model_confidence':
                    primary_factors.append("Low model confidence")
        
        return primary_factors
    
    def _identify_limitations(self, student_profile: Dict, risk_assessment: Dict) -> List[str]:
        """Identify limitations of the current assessment."""
        
        limitations = []
        
        # Data limitations
        data_sources = ['lms_activity', 'assignments', 'messages', 'attendance']
        available_sources = sum(1 for source in data_sources if student_profile.get(source))
        
        if available_sources < len(data_sources):
            missing_count = len(data_sources) - available_sources
            limitations.append(f"Analysis based on {available_sources}/{len(data_sources)} data sources")
        
        # Temporal limitations
        confidence = risk_assessment.get('confidence', 'low')
        if confidence == 'low':
            limitations.append("Limited historical data for trend analysis")
        
        # Sample size limitations
        lms_data = student_profile.get('lms_activity', {})
        if lms_data.get('total_sessions', 0) < 10:
            limitations.append("Limited activity history for reliable pattern detection")
        
        # Contextual limitations
        limitations.append("Does not account for external factors (personal circumstances, etc.)")
        limitations.append("Risk indicators, not definitive predictions")
        
        return limitations
    
    def _generate_actionable_insights(self, key_signals: List[str], 
                                    risk_assessment: Dict) -> List[str]:
        """Generate actionable insights for educators."""
        
        insights = []
        risk_score = risk_assessment.get('risk_score', 0.0)
        
        # General insights based on risk level
        if risk_score > 0.7:
            insights.append("Immediate outreach recommended to assess student wellbeing")
            insights.append("Consider academic support resources")
        elif risk_score > 0.4:
            insights.append("Monitor closely over the next 1-2 weeks")
            insights.append("Check in during office hours or via email")
        else:
            insights.append("Continue routine monitoring")
        
        # Specific insights based on key signals
        for signal in key_signals:
            if "LMS activity" in signal.lower():
                insights.append("Review platform engagement patterns")
            elif "assignment" in signal.lower():
                insights.append("Discuss time management strategies")
            elif "sentiment" in signal.lower() or "communication" in signal.lower():
                insights.append("Schedule a supportive conversation")
            elif "attendance" in signal.lower():
                insights.append("Address any barriers to class participation")
        
        return list(set(insights))  # Remove duplicates

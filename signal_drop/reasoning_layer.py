"""
GenAI Reasoning Layer - LLM-powered Narrative Extraction

Uses LLM to extract latent narratives from text, cluster weak signals
across time, and identify trend acceleration patterns.
"""

import openai
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

class GenAIReasoner:
    """GenAI-powered reasoning engine for narrative extraction and pattern recognition."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: str = None):
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=api_key) if api_key else None
        self.narrative_patterns = {}
        self.signal_clusters = {}
        
    def extract_student_narrative(self, student_profile: Dict, temporal_embeddings: Dict) -> Dict[str, Any]:
        """Extract latent narratives from student data using LLM reasoning."""
        
        # Prepare context for LLM
        context = self._prepare_narrative_context(student_profile, temporal_embeddings)
        
        # Generate narrative analysis
        narrative_analysis = self._generate_narrative_analysis(context)
        
        # Extract key themes and patterns
        themes = self._extract_key_themes(narrative_analysis)
        
        # Identify narrative shifts
        shifts = self._identify_narrative_shifts(student_profile, themes)
        
        return {
            "narrative_summary": narrative_analysis.get("summary", ""),
            "key_themes": themes,
            "narrative_shifts": shifts,
            "engagement_trajectory": narrative_analysis.get("trajectory", "stable"),
            "risk_indicators": narrative_analysis.get("risk_indicators", []),
            "confidence_score": narrative_analysis.get("confidence", 0.5)
        }
    
    def _prepare_narrative_context(self, student_profile: Dict, temporal_embeddings: Dict) -> str:
        """Prepare context for LLM narrative analysis."""
        
        context_parts = []
        
        # Student activity summary
        lms_data = student_profile.get('lms_activity', {})
        if lms_data:
            context_parts.append(f"LMS Activity: {lms_data.get('activity_frequency_7d', 0)} sessions in last 7 days, "
                               f"{lms_data.get('activity_frequency_14d', 0)} in last 14 days. "
                               f"Average session gap: {lms_data.get('avg_session_gap_hours', 0):.1f} hours.")
        
        # Assignment patterns
        assign_data = student_profile.get('assignments', {})
        if assign_data:
            context_parts.append(f"Assignments: {assign_data.get('late_submission_rate', 0):.1%} late submission rate, "
                               f"average delay: {assign_data.get('avg_delay_hours', 0):.1f} hours. "
                               f"Recent late rate: {assign_data.get('recent_late_rate', 0):.1%}.")
        
        # Communication patterns
        msg_data = student_profile.get('messages', {})
        if msg_data:
            context_parts.append(f"Messages: {msg_data.get('total_messages', 0)} total messages, "
                               f"sentiment ratio: {msg_data.get('avg_sentiment_ratio', 1):.2f}, "
                               f"negative sentiment indicators: {msg_data.get('negative_sentiment_total', 0)}.")
        
        # Attendance patterns
        att_data = student_profile.get('attendance', {})
        if att_data:
            context_parts.append(f"Attendance: {att_data.get('attendance_rate', 0):.1%} overall rate, "
                               f"recent rate: {att_data.get('recent_attendance_rate', 0):.1%}, "
                               f"absent rate: {att_data.get('absent_rate', 0):.1%}.")
        
        # Temporal drift information
        if temporal_embeddings:
            context_parts.append(f"Temporal analysis shows patterns across {list(temporal_embeddings.keys())} day windows.")
        
        return " ".join(context_parts)
    
    def _generate_narrative_analysis(self, context: str) -> Dict[str, Any]:
        """Generate narrative analysis using LLM."""
        
        if not self.client:
            # Fallback to rule-based analysis
            return self._fallback_narrative_analysis(context)
        
        try:
            prompt = f"""
            Analyze the following student engagement data and provide a narrative assessment:

            Student Data:
            {context}

            Please provide:
            1. A brief narrative summary of the student's engagement pattern
            2. Key themes or patterns observed
            3. The engagement trajectory (improving, declining, stable, volatile)
            4. Risk indicators for potential disengagement or dropout
            5. Confidence level in your assessment (0-1)

            Focus on identifying weak signals and emerging patterns, not just obvious issues.
            Consider the interplay between different data sources and temporal trends.

            Respond in JSON format:
            {{
                "summary": "brief narrative summary",
                "trajectory": "improving|declining|stable|volatile",
                "risk_indicators": ["indicator1", "indicator2", ...],
                "confidence": 0.8
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert educational analyst specializing in early warning systems for student dropout risk."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._fallback_narrative_analysis(context)
    
    def _fallback_narrative_analysis(self, context: str) -> Dict[str, Any]:
        """Fallback rule-based narrative analysis when LLM is unavailable."""
        
        # Simple keyword-based analysis
        risk_indicators = []
        trajectory = "stable"
        confidence = 0.6
        
        # Check for risk patterns in context
        if "late submission rate: 0." in context and float(re.search(r'late submission rate: ([0-9.]+)', context).group(1)) > 0.3:
            risk_indicators.append("High late submission rate")
            trajectory = "declining"
        
        if "sentiment ratio:" in context:
            sentiment_match = re.search(r'sentiment ratio: ([0-9.]+)', context)
            if sentiment_match and float(sentiment_match.group(1)) < 0.5:
                risk_indicators.append("Low sentiment ratio")
                if trajectory == "stable":
                    trajectory = "declining"
        
        if "attendance rate:" in context:
            attendance_match = re.search(r'attendance rate: ([0-9.]+)', context)
            if attendance_match and float(attendance_match.group(1)) < 0.8:
                risk_indicators.append("Low attendance rate")
                trajectory = "declining"
        
        if "sessions in last 7 days: 0" in context or "sessions in last 7 days: 1" in context:
            risk_indicators.append("Low recent activity")
            trajectory = "declining"
        
        summary = f"Student shows {trajectory} engagement pattern"
        if risk_indicators:
            summary += f" with concerns including {', '.join(risk_indicators[:2])}"
        
        return {
            "summary": summary,
            "trajectory": trajectory,
            "risk_indicators": risk_indicators,
            "confidence": confidence
        }
    
    def _extract_key_themes(self, narrative_analysis: Dict) -> List[str]:
        """Extract key themes from narrative analysis."""
        
        themes = []
        
        # Extract from summary and risk indicators
        summary = narrative_analysis.get("summary", "").lower()
        risk_indicators = narrative_analysis.get("risk_indicators", [])
        
        # Theme mapping
        theme_keywords = {
            "disengagement": ["disengaged", "withdrawn", "inactive", "low activity"],
            "academic_struggle": ["struggling", "difficulty", "falling behind", "poor performance"],
            "time_management": ["late", "delayed", "procrastination", "time management"],
            "communication_decline": ["less communication", "withdrawn", "isolated", "quiet"],
            "attendance_issues": ["absent", "missing", "poor attendance", "skipping"],
            "sentiment_shift": ["negative", "frustrated", "discouraged", "unhappy"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in summary for keyword in keywords):
                themes.append(theme)
        
        # Add themes from risk indicators
        for indicator in risk_indicators:
            indicator_lower = indicator.lower()
            if "late" in indicator_lower:
                themes.append("time_management")
            elif "attendance" in indicator_lower:
                themes.append("attendance_issues")
            elif "sentiment" in indicator_lower:
                themes.append("sentiment_shift")
            elif "activity" in indicator_lower:
                themes.append("disengagement")
        
        return list(set(themes))  # Remove duplicates
    
    def _identify_narrative_shifts(self, student_profile: Dict, themes: List[str]) -> List[Dict[str, Any]]:
        """Identify narrative shifts in student behavior."""
        
        shifts = []
        
        # Check for recent vs long-term patterns
        lms_data = student_profile.get('lms_activity', {})
        assign_data = student_profile.get('assignments', {})
        msg_data = student_profile.get('messages', {})
        att_data = student_profile.get('attendance', {})
        
        # Activity shift
        if lms_data:
            recent_7d = lms_data.get('activity_frequency_7d', 0)
            recent_14d = lms_data.get('activity_frequency_14d', 0)
            
            if recent_14d > 0 and recent_7d / recent_14d < 0.5:
                shifts.append({
                    "type": "activity_decline",
                    "description": "Significant drop in LMS activity in recent week",
                    "severity": "high" if recent_7d == 0 else "medium",
                    "timeframe": "last 7 days"
                })
        
        # Assignment quality shift
        if assign_data:
            recent_late = assign_data.get('recent_late_rate', 0)
            overall_late = assign_data.get('late_submission_rate', 0)
            
            if recent_late > overall_late + 0.2:  # 20% increase
                shifts.append({
                    "type": "assignment_punctuality_decline",
                    "description": "Recent increase in late submissions",
                    "severity": "high" if recent_late > 0.5 else "medium",
                    "timeframe": "recent assignments"
                })
        
        # Sentiment shift
        if msg_data.get('recent_sentiment_decline', False):
            shifts.append({
                "type": "sentiment_decline",
                "description": "Negative shift in communication sentiment",
                "severity": "medium",
                "timeframe": "recent messages"
            })
        
        # Attendance shift
        if att_data:
            recent_rate = att_data.get('recent_attendance_rate', 0)
            overall_rate = att_data.get('attendance_rate', 0)
            
            if recent_rate < overall_rate - 0.15:  # 15% decline
                shifts.append({
                    "type": "attendance_decline",
                    "description": "Recent decline in attendance rate",
                    "severity": "high" if recent_rate < 0.7 else "medium",
                    "timeframe": "recent classes"
                })
        
        return shifts
    
    def cluster_weak_signals(self, student_profiles: Dict[str, Dict], 
                           signal_threshold: float = 0.3) -> Dict[str, List[str]]:
        """Cluster weak signals across multiple students to identify patterns."""
        
        signal_patterns = defaultdict(list)
        
        for student_id, profile in student_profiles.items():
            # Extract weak signals for this student
            weak_signals = self._extract_weak_signals(profile)
            
            for signal in weak_signals:
                signal_patterns[signal].append(student_id)
        
        # Filter for signals that affect multiple students
        significant_patterns = {
            signal: students 
            for signal, students in signal_patterns.items() 
            if len(students) >= max(2, len(student_profiles) * signal_threshold)
        }
        
        return significant_patterns
    
    def _extract_weak_signals(self, student_profile: Dict) -> List[str]:
        """Extract weak signals from individual student profile."""
        
        weak_signals = []
        
        # LMS weak signals
        lms_data = student_profile.get('lms_activity', {})
        if lms_data:
            if lms_data.get('activity_frequency_7d', 0) <= 2:
                weak_signals.append("very_low_recent_activity")
            if lms_data.get('avg_session_gap_hours', 0) > 72:  # 3 days
                weak_signals.append("large_session_gaps")
            if lms_data.get('weekend_activity_ratio', 0) < 0.1:
                weak_signals.append("no_weekend_activity")
        
        # Assignment weak signals
        assign_data = student_profile.get('assignments', {})
        if assign_data:
            if assign_data.get('avg_text_length', 0) < 50:
                weak_signals.append("minimal_assignment_effort")
            if assign_data.get('recent_late_rate', 0) > 0.3:
                weak_signals.append("emerging_punctuality_issues")
        
        # Message weak signals
        msg_data = student_profile.get('messages', {})
        if msg_data:
            if msg_data.get('total_messages', 0) == 0:
                weak_signals.append("no_communication")
            elif msg_data.get('avg_sentiment_ratio', 1) < 0.7:
                weak_signals.append("declining_sentiment")
        
        # Attendance weak signals
        att_data = student_profile.get('attendance', {})
        if att_data:
            if att_data.get('recent_attendance_rate', 1) < 0.9:
                weak_signals.append("occasional_absences")
            if att_data.get('late_rate', 0) > 0.1:
                weak_signals.append("frequent_tardiness")
        
        return weak_signals
    
    def identify_trend_acceleration(self, temporal_data: Dict[str, List[float]], 
                                  window_sizes: List[int] = [7, 14, 30]) -> Dict[str, Any]:
        """Identify accelerating trends across different time windows."""
        
        acceleration_analysis = {}
        
        for metric, values in temporal_data.items():
            if len(values) < max(window_sizes):
                continue
            
            # Calculate trends for different windows
            trends = {}
            for window in window_sizes:
                if len(values) >= window:
                    recent_values = values[-window:]
                    # Simple linear trend calculation
                    x = np.arange(len(recent_values))
                    if len(x) > 1:
                        slope = np.polyfit(x, recent_values, 1)[0]
                        trends[window] = slope
            
            # Identify acceleration (trend getting more negative/positive)
            if len(trends) >= 2:
                windows_sorted = sorted(trends.keys())
                short_term_trend = trends[windows_sorted[0]]
                long_term_trend = trends[windows_sorted[-1]]
                
                # Acceleration is the change in trend
                acceleration = short_term_trend - long_term_trend
                
                acceleration_analysis[metric] = {
                    "short_term_trend": short_term_trend,
                    "long_term_trend": long_term_trend,
                    "acceleration": acceleration,
                    "is_accelerating_decline": acceleration < -0.01,
                    "is_accelerating_improvement": acceleration > 0.01
                }
        
        return acceleration_analysis

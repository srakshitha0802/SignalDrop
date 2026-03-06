"""
Data Layer - Multi-source data ingestion and preprocessing

Handles LMS activity logs, assignment submissions, student messages,
and attendance records with text normalization and timestamp alignment.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """Processes multi-source educational data for risk detection."""
    
    def __init__(self):
        self.download_nltk_resources()
        self.stop_words = set(stopwords.words('english'))
        
    def download_nltk_resources(self):
        """Download required NLTK resources."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
    
    def normalize_text(self, text: str) -> str:
        """Normalize text by removing special characters, lowercasing, and removing stopwords."""
        if not isinstance(text, str):
            return ""
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize and remove stopwords
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token not in self.stop_words]
        
        return ' '.join(tokens)
    
    def process_lms_activity(self, raw_data: List[Dict]) -> pd.DataFrame:
        """Process LMS activity logs with timestamp alignment."""
        df = pd.DataFrame(raw_data)
        
        # Convert timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Calculate activity frequency metrics
        df = df.sort_values(['student_id', 'timestamp'])
        
        # Add time-based features
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Calculate session gaps
        df['time_since_last_activity'] = df.groupby('student_id')['timestamp'].diff()
        df['time_since_last_activity'] = df['time_since_last_activity'].dt.total_seconds() / 3600  # hours
        
        return df
    
    def process_assignment_submissions(self, raw_data: List[Dict]) -> pd.DataFrame:
        """Process assignment submission data with text analysis."""
        df = pd.DataFrame(raw_data)
        
        # Convert timestamps
        df['submission_timestamp'] = pd.to_datetime(df['submission_timestamp'])
        df['due_timestamp'] = pd.to_datetime(df['due_timestamp'])
        
        # Calculate delay metrics
        df['delay_hours'] = (df['submission_timestamp'] - df['due_timestamp']).dt.total_seconds() / 3600
        df['is_late'] = (df['delay_hours'] > 0).astype(int)
        
        # Process submission text
        if 'submission_text' in df.columns:
            df['normalized_text'] = df['submission_text'].apply(self.normalize_text)
            df['text_length'] = df['normalized_text'].str.len()
            df['word_count'] = df['normalized_text'].str.split().str.len()
        
        return df
    
    def process_student_messages(self, raw_data: List[Dict]) -> pd.DataFrame:
        """Process student messages with sentiment and engagement analysis."""
        df = pd.DataFrame(raw_data)
        
        # Convert timestamps
        df['message_timestamp'] = pd.to_datetime(df['message_timestamp'])
        
        # Normalize message text
        df['normalized_message'] = df['message_text'].apply(self.normalize_text)
        
        # Add message features
        df['message_length'] = df['normalized_message'].str.len()
        df['word_count'] = df['normalized_message'].str.split().str.len()
        
        # Simple sentiment indicators (can be enhanced with proper sentiment analysis)
        negative_words = ['difficult', 'hard', 'confused', 'lost', 'help', 'struggle', 'fail', 'bad']
        positive_words = ['good', 'great', 'understand', 'clear', 'helpful', 'easy', 'thanks']
        
        df['negative_sentiment_score'] = df['normalized_message'].apply(
            lambda x: sum(1 for word in negative_words if word in x.split())
        )
        df['positive_sentiment_score'] = df['normalized_message'].apply(
            lambda x: sum(1 for word in positive_words if word in x.split())
        )
        df['sentiment_ratio'] = df['positive_sentiment_score'] / (df['negative_sentiment_score'] + 1)
        
        return df
    
    def process_attendance_records(self, raw_data: List[Dict]) -> pd.DataFrame:
        """Process attendance records with pattern analysis."""
        df = pd.DataFrame(raw_data)
        
        # Convert timestamps
        df['attendance_date'] = pd.to_datetime(df['attendance_date'])
        
        # Create binary attendance flag
        df['is_present'] = df['attendance_status'].isin(['present', 'on_time']).astype(int)
        df['is_late'] = df['attendance_status'].isin(['late']).astype(int)
        df['is_absent'] = df['attendance_status'].isin(['absent', 'excused']).astype(int)
        
        return df
    
    def aggregate_student_signals(self, lms_df: pd.DataFrame, 
                                 assignment_df: pd.DataFrame,
                                 message_df: pd.DataFrame,
                                 attendance_df: pd.DataFrame) -> Dict[str, Dict]:
        """Aggregate all signals by student with temporal windows."""
        
        # Get unique students
        all_students = set()
        for df in [lms_df, assignment_df, message_df, attendance_df]:
            if 'student_id' in df.columns:
                all_students.update(df['student_id'].unique())
        
        student_profiles = {}
        
        for student_id in all_students:
            profile = {
                'student_id': student_id,
                'lms_activity': self._aggregate_lms_for_student(lms_df, student_id),
                'assignments': self._aggregate_assignments_for_student(assignment_df, student_id),
                'messages': self._aggregate_messages_for_student(message_df, student_id),
                'attendance': self._aggregate_attendance_for_student(attendance_df, student_id)
            }
            student_profiles[student_id] = profile
        
        return student_profiles
    
    def _aggregate_lms_for_student(self, df: pd.DataFrame, student_id: str) -> Dict:
        """Aggregate LMS activity for a specific student."""
        if df.empty or 'student_id' not in df.columns:
            return {}
        
        student_data = df[df['student_id'] == student_id]
        if student_data.empty:
            return {}
        
        return {
            'total_sessions': len(student_data),
            'avg_session_gap_hours': student_data['time_since_last_activity'].mean(),
            'weekend_activity_ratio': student_data['is_weekend'].mean(),
            'peak_activity_hour': student_data['hour_of_day'].mode().iloc[0] if not student_data['hour_of_day'].mode().empty else 14,
            'last_activity': student_data['timestamp'].max(),
            'activity_frequency_7d': len(student_data[student_data['timestamp'] > (datetime.now() - timedelta(days=7))]),
            'activity_frequency_14d': len(student_data[student_data['timestamp'] > (datetime.now() - timedelta(days=14))]),
            'activity_frequency_30d': len(student_data[student_data['timestamp'] > (datetime.now() - timedelta(days=30))])
        }
    
    def _aggregate_assignments_for_student(self, df: pd.DataFrame, student_id: str) -> Dict:
        """Aggregate assignment data for a specific student."""
        if df.empty or 'student_id' not in df.columns:
            return {}
        
        student_data = df[df['student_id'] == student_id]
        if student_data.empty:
            return {}
        
        return {
            'total_assignments': len(student_data),
            'late_submission_rate': student_data['is_late'].mean(),
            'avg_delay_hours': student_data['delay_hours'].mean(),
            'avg_text_length': student_data['text_length'].mean() if 'text_length' in student_data.columns else 0,
            'avg_word_count': student_data['word_count'].mean() if 'word_count' in student_data.columns else 0,
            'last_submission': student_data['submission_timestamp'].max(),
            'recent_late_rate': student_data.tail(5)['is_late'].mean() if len(student_data) >= 5 else student_data['is_late'].mean()
        }
    
    def _aggregate_messages_for_student(self, df: pd.DataFrame, student_id: str) -> Dict:
        """Aggregate message data for a specific student."""
        if df.empty or 'student_id' not in df.columns:
            return {}
        
        student_data = df[df['student_id'] == student_id]
        if student_data.empty:
            return {}
        
        return {
            'total_messages': len(student_data),
            'avg_message_length': student_data['message_length'].mean(),
            'avg_word_count': student_data['word_count'].mean(),
            'negative_sentiment_total': student_data['negative_sentiment_score'].sum(),
            'positive_sentiment_total': student_data['positive_sentiment_score'].sum(),
            'avg_sentiment_ratio': student_data['sentiment_ratio'].mean(),
            'last_message': student_data['message_timestamp'].max(),
            'recent_sentiment_decline': self._detect_sentiment_decline(student_data)
        }
    
    def _aggregate_attendance_for_student(self, df: pd.DataFrame, student_id: str) -> Dict:
        """Aggregate attendance data for a specific student."""
        if df.empty or 'student_id' not in df.columns:
            return {}
        
        student_data = df[df['student_id'] == student_id]
        if student_data.empty:
            return {}
        
        return {
            'total_days': len(student_data),
            'attendance_rate': student_data['is_present'].mean(),
            'late_rate': student_data['is_late'].mean(),
            'absent_rate': student_data['is_absent'].mean(),
            'last_attendance': student_data['attendance_date'].max(),
            'recent_attendance_rate': student_data.tail(10)['is_present'].mean() if len(student_data) >= 10 else student_data['is_present'].mean()
        }
    
    def _detect_sentiment_decline(self, student_data: pd.DataFrame) -> bool:
        """Detect if sentiment has declined in recent messages."""
        if len(student_data) < 5:
            return False
        
        student_data = student_data.sort_values('message_timestamp')
        recent_sentiment = student_data.tail(3)['sentiment_ratio'].mean()
        earlier_sentiment = student_data.head(len(student_data) - 3)['sentiment_ratio'].mean()
        
        return recent_sentiment < earlier_sentiment * 0.8  # 20% decline threshold

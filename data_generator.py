"""
Synthetic Data Generator for SignalDrop AI

Generates realistic synthetic educational data for testing and demonstration.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Any
import json

class SyntheticDataGenerator:
    """Generates synthetic educational data for testing SignalDrop AI."""
    
    def __init__(self, num_students: int = 100, days_back: int = 60):
        self.num_students = num_students
        self.days_back = days_back
        self.current_date = datetime.now()
        
        # Student profiles with different risk patterns
        self.student_profiles = self._create_student_profiles()
        
    def _create_student_profiles(self) -> List[Dict]:
        """Create diverse student profiles with different risk patterns."""
        
        profiles = []
        
        # Define risk pattern types
        risk_patterns = [
            {"type": "stable", "weight": 0.4, "base_risk": 0.2},
            {"type": "declining", "weight": 0.3, "base_risk": 0.6},
            {"type": "critical", "weight": 0.15, "base_risk": 0.8},
            {"type": "improving", "weight": 0.1, "base_risk": 0.4},
            {"type": "volatile", "weight": 0.05, "base_risk": 0.5}
        ]
        
        for i in range(self.num_students):
            # Select risk pattern based on weights
            pattern = np.random.choice(
                risk_patterns, 
                p=[p["weight"] for p in risk_patterns]
            )
            
            profile = {
                "student_id": f"S{1000 + i}",
                "risk_pattern": pattern["type"],
                "base_risk": pattern["base_risk"],
                "engagement_level": np.random.beta(2, 5),  # Mostly low engagement
                "academic_performance": np.random.beta(3, 3),  # Normal distribution
                "communication_style": np.random.choice(["active", "moderate", "minimal"]),
                "attendance_consistency": np.random.beta(4, 2)  # Mostly consistent
            }
            
            profiles.append(profile)
        
        return profiles
    
    def generate_lms_activity(self) -> List[Dict]:
        """Generate LMS activity logs."""
        
        activities = []
        
        for profile in self.student_profiles:
            student_id = profile["student_id"]
            risk_pattern = profile["risk_pattern"]
            engagement = profile["engagement_level"]
            
            # Generate activity sessions
            for day in range(self.days_back):
                date = self.current_date - timedelta(days=day)
                
                # Base activity probability
                base_prob = engagement * 0.8
                
                # Adjust based on risk pattern
                if risk_pattern == "declining":
                    # Decrease activity over time
                    time_factor = 1.0 - (day / self.days_back) * 0.7
                    base_prob *= time_factor
                elif risk_pattern == "critical":
                    # Very low activity with occasional spikes
                    base_prob *= 0.3 if np.random.random() > 0.1 else 1.5
                elif risk_pattern == "improving":
                    # Increase activity over time
                    time_factor = 0.5 + (day / self.days_back) * 0.5
                    base_prob *= time_factor
                elif risk_pattern == "volatile":
                    # Random fluctuations
                    base_prob *= np.random.uniform(0.2, 1.5)
                
                # Generate sessions for this day
                if np.random.random() < base_prob:
                    num_sessions = np.random.poisson(2) + 1
                    
                    for session in range(num_sessions):
                        hour = np.random.choice([10, 14, 16, 19, 21])  # Peak hours
                        
                        activities.append({
                            "student_id": student_id,
                            "timestamp": date.replace(hour=hour, minute=np.random.randint(0, 60)),
                            "activity_type": np.random.choice(["login", "view_content", "download", "forum_post"]),
                            "duration_minutes": np.random.exponential(30) + 5
                        })
        
        return activities
    
    def generate_assignment_submissions(self) -> List[Dict]:
        """Generate assignment submission data."""
        
        submissions = []
        
        # Create assignment schedule
        assignments = []
        for week in range(8):  # 8 weeks of assignments
            due_date = self.current_date - timedelta(weeks=week)
            assignments.append({
                "assignment_id": f"ASSIGN{week + 1}",
                "due_timestamp": due_date,
                "type": np.random.choice(["essay", "problem_set", "project", "quiz"])
            })
        
        for profile in self.student_profiles:
            student_id = profile["student_id"]
            risk_pattern = profile["risk_pattern"]
            academic_perf = profile["academic_performance"]
            
            for assignment in assignments:
                # Base submission probability
                base_prob = 0.9 * academic_perf
                
                # Adjust based on risk pattern
                if risk_pattern == "declining":
                    # More likely to be late/miss recent assignments
                    days_since_due = (self.current_date - assignment["due_timestamp"]).days
                    if days_since_due < 14:  # Recent assignments
                        base_prob *= 0.7
                elif risk_pattern == "critical":
                    base_prob *= 0.6
                elif risk_pattern == "improving":
                    # Better performance on recent assignments
                    days_since_due = (self.current_date - assignment["due_timestamp"]).days
                    if days_since_due < 14:
                        base_prob *= 1.2
                
                if np.random.random() < base_prob:
                    # Generate submission
                    delay_hours = 0
                    
                    if risk_pattern == "declining":
                        delay_hours = np.random.exponential(48)  # Often late
                    elif risk_pattern == "critical":
                        delay_hours = np.random.exponential(72)  # Very often late
                    elif risk_pattern == "improving":
                        delay_hours = max(0, np.random.normal(-12, 24))  # Often early
                    else:
                        delay_hours = max(0, np.random.normal(6, 12))
                    
                    submission_time = assignment["due_timestamp"] + timedelta(hours=delay_hours)
                    
                    # Generate submission text
                    text_length = int(np.random.normal(300, 100) * academic_perf)
                    text_length = max(50, min(800, text_length))
                    
                    submission_text = self._generate_submission_text(
                        assignment["type"], text_length, academic_perf
                    )
                    
                    submissions.append({
                        "student_id": student_id,
                        "assignment_id": assignment["assignment_id"],
                        "submission_timestamp": submission_time,
                        "due_timestamp": assignment["due_timestamp"],
                        "submission_text": submission_text,
                        "grade": np.random.normal(85, 10) * academic_perf + np.random.normal(0, 5)
                    })
        
        return submissions
    
    def generate_student_messages(self) -> List[Dict]:
        """Generate student communication data."""
        
        messages = []
        
        for profile in self.student_profiles:
            student_id = profile["student_id"]
            risk_pattern = profile["risk_pattern"]
            comm_style = profile["communication_style"]
            
            # Base message frequency
            base_freq = {"active": 0.8, "moderate": 0.4, "minimal": 0.1}[comm_style]
            
            for day in range(self.days_back):
                date = self.current_date - timedelta(days=day)
                
                # Adjust frequency based on risk pattern
                if risk_pattern == "declining":
                    time_factor = 1.0 - (day / self.days_back) * 0.6
                    freq = base_freq * time_factor
                elif risk_pattern == "critical":
                    freq = base_freq * 0.3
                elif risk_pattern == "improving":
                    time_factor = 0.5 + (day / self.days_back) * 0.5
                    freq = base_freq * time_factor
                else:
                    freq = base_freq
                
                if np.random.random() < freq:
                    # Generate message
                    sentiment = self._generate_sentiment(risk_pattern, day)
                    message_text = self._generate_message_text(sentiment, risk_pattern)
                    
                    messages.append({
                        "student_id": student_id,
                        "message_timestamp": date.replace(hour=np.random.randint(9, 17)),
                        "message_text": message_text,
                        "recipient": np.random.choice(["instructor", "ta", "admin"]),
                        "message_type": np.random.choice(["question", "comment", "request"])
                    })
        
        return messages
    
    def generate_attendance_records(self) -> List[Dict]:
        """Generate attendance records."""
        
        attendance = []
        
        # Create class schedule (3 classes per week)
        class_dates = []
        for day in range(self.days_back):
            date = self.current_date - timedelta(days=day)
            if date.weekday() in [0, 2, 4]:  # Monday, Wednesday, Friday
                class_dates.append(date)
        
        for profile in self.student_profiles:
            student_id = profile["student_id"]
            risk_pattern = profile["risk_pattern"]
            consistency = profile["attendance_consistency"]
            
            for class_date in class_dates:
                # Base attendance probability
                base_prob = consistency * 0.95
                
                # Adjust based on risk pattern
                if risk_pattern == "declining":
                    time_factor = 1.0 - ((self.days_back - class_date.timetuple().tm_yday) / self.days_back) * 0.5
                    base_prob *= time_factor
                elif risk_pattern == "critical":
                    base_prob *= 0.7
                elif risk_pattern == "improving":
                    time_factor = 0.6 + ((self.days_back - class_date.timetuple().tm_yday) / self.days_back) * 0.4
                    base_prob *= time_factor
                
                if np.random.random() < base_prob:
                    # Present
                    if np.random.random() < 0.1:  # 10% chance of being late
                        status = "late"
                    else:
                        status = "on_time"
                else:
                    # Absent
                    status = np.random.choice(["absent", "excused"], p=[0.7, 0.3])
                
                attendance.append({
                    "student_id": student_id,
                    "attendance_date": class_date,
                    "attendance_status": status,
                    "class_type": np.random.choice(["lecture", "lab", "seminar"])
                })
        
        return attendance
    
    def _generate_submission_text(self, assignment_type: str, length: int, 
                                 academic_perf: float) -> str:
        """Generate realistic submission text."""
        
        # Templates based on assignment type
        templates = {
            "essay": [
                "In this essay, I will explore the key concepts discussed in class. ",
                "The main argument centers around the fundamental principles we've studied. ",
                "Based on my research and understanding, I believe that "
            ],
            "problem_set": [
                "Problem 1: To solve this equation, I first identified the variables. ",
                "For question 2, I applied the formula we learned in lecture. ",
                "The solution approach involves breaking down the complex problem into smaller parts. "
            ],
            "project": [
                "For this project, I implemented a solution that addresses the requirements. ",
                "The methodology I followed includes several key steps. ",
                "My approach combines theoretical knowledge with practical application. "
            ],
            "quiz": [
                "Answer 1: The correct response is based on the course material. ",
                "For question 2, I considered all possible options. ",
                "The reasoning behind my answer involves understanding the core concepts. "
            ]
        }
        
        # Quality indicators based on academic performance
        quality_phrases = {
            "high": ["thoroughly analyzed", "comprehensive explanation", "detailed solution", "well-researched"],
            "medium": ["explained the concept", "provided a solution", "covered the main points", "basic analysis"],
            "low": ["briefly mentioned", "simple answer", "minimal explanation", "basic response"]
        }
        
        # Determine quality level
        if academic_perf > 0.7:
            quality = "high"
        elif academic_perf > 0.4:
            quality = "medium"
        else:
            quality = "low"
        
        # Generate text
        template = np.random.choice(templates.get(assignment_type, templates["essay"]))
        phrase = np.random.choice(quality_phrases[quality])
        
        base_text = template + phrase + " "
        
        # Add filler to reach desired length
        filler_words = ["the", "and", "that", "this", "with", "from", "they", "have", "been", "said"]
        while len(base_text) < length:
            base_text += np.random.choice(filler_words) + " "
        
        return base_text[:length].strip()
    
    def _generate_sentiment(self, risk_pattern: str, day: int) -> str:
        """Generate sentiment based on risk pattern and time."""
        
        if risk_pattern == "declining":
            # Increasingly negative over time
            if day < self.days_back * 0.3:
                return np.random.choice(["positive", "neutral"], p=[0.7, 0.3])
            elif day < self.days_back * 0.7:
                return np.random.choice(["neutral", "negative"], p=[0.6, 0.4])
            else:
                return np.random.choice(["negative", "neutral"], p=[0.7, 0.3])
        
        elif risk_pattern == "critical":
            return np.random.choice(["negative", "neutral"], p=[0.8, 0.2])
        
        elif risk_pattern == "improving":
            # Increasingly positive over time
            if day < self.days_back * 0.3:
                return np.random.choice(["negative", "neutral"], p=[0.6, 0.4])
            elif day < self.days_back * 0.7:
                return np.random.choice(["neutral", "positive"], p=[0.5, 0.5])
            else:
                return np.random.choice(["positive", "neutral"], p=[0.8, 0.2])
        
        else:
            return np.random.choice(["positive", "neutral", "negative"], p=[0.4, 0.4, 0.2])
    
    def _generate_message_text(self, sentiment: str, risk_pattern: str) -> str:
        """Generate message text based on sentiment."""
        
        templates = {
            "positive": [
                "Thanks for the great lecture today! I really understood the material.",
                "I'm finding this topic really interesting. Looking forward to the next class.",
                "The examples you provided were very helpful. Everything makes sense now.",
                "Great explanation! I feel confident about the upcoming assignment."
            ],
            "neutral": [
                "I have a question about the homework problem set.",
                "Could you clarify the requirements for the project?",
                "When are the office hours this week?",
                "I wanted to check the due date for the upcoming assignment."
            ],
            "negative": [
                "I'm really struggling with the recent material. Can we schedule a meeting?",
                "I'm confused about the concepts from yesterday's lecture.",
                "I'm having difficulty keeping up with the coursework pace.",
                "I'm worried about my performance in this class. I need some help."
            ]
        }
        
        return np.random.choice(templates.get(sentiment, templates["neutral"]))
    
    def generate_all_data(self) -> Dict[str, List[Dict]]:
        """Generate all synthetic data."""
        
        return {
            "lms_activity": self.generate_lms_activity(),
            "assignments": self.generate_assignment_submissions(),
            "messages": self.generate_student_messages(),
            "attendance": self.generate_attendance_records()
        }
    
    def save_data(self, filename: str = None) -> str:
        """Generate and save synthetic data to file."""
        
        if filename is None:
            filename = f"synthetic_data_{self.num_students}students_{self.days_back}days.json"
        
        data = self.generate_all_data()
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return filename
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics of generated data."""
        
        data = self.generate_all_data()
        
        stats = {
            "students": self.num_students,
            "days_generated": self.days_back,
            "risk_patterns": {}
        }
        
        # Count risk patterns
        for profile in self.student_profiles:
            pattern = profile["risk_pattern"]
            if pattern not in stats["risk_patterns"]:
                stats["risk_patterns"][pattern] = 0
            stats["risk_patterns"][pattern] += 1
        
        # Data source statistics
        stats["data_sources"] = {
            "lms_activities": len(data["lms_activity"]),
            "assignment_submissions": len(data["assignments"]),
            "student_messages": len(data["messages"]),
            "attendance_records": len(data["attendance"])
        }
        
        return stats

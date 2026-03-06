#!/usr/bin/env python3
"""
High-Fidelity Synthetic Dataset Generator for SignalDrop AI

Generates realistic, ambiguous student engagement data where dropout risk
emerges gradually through weak, fragmented signals across multiple modalities.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string
import os
from typing import Dict, List, Tuple, Optional
import json

class HighFidelityDatasetGenerator:
    """Generates realistic synthetic educational data for early warning systems."""
    
    def __init__(self, num_students: int = 750, semester_weeks: int = 16):
        self.num_students = num_students
        self.semester_weeks = semester_weeks
        self.current_date = datetime.now()
        
        # Student profile parameters
        self.student_profiles = self._create_realistic_student_profiles()
        
        # Text generation templates
        self.text_templates = self._initialize_text_templates()
        
        # Ground truth storage
        self.ground_truth = []
        
    def _create_realistic_student_profiles(self) -> List[Dict]:
        """Create diverse student profiles with hidden risk trajectories."""
        
        profiles = []
        
        # Define latent groups with realistic proportions
        group_distribution = [
            {"type": "stable", "proportion": 0.65, "risk_trajectory": "low"},
            {"type": "gradual_disengagement", "proportion": 0.25, "risk_trajectory": "high"},
            {"type": "volatile_non_failing", "proportion": 0.10, "risk_trajectory": "medium"}
        ]
        
        # Assign students to groups
        group_assignments = []
        for group in group_distribution:
            count = int(self.num_students * group["proportion"])
            group_assignments.extend([group["type"]] * count)
        
        # Fill remaining slots to match exact student count
        while len(group_assignments) < self.num_students:
            group_assignments.append("stable")
        
        random.shuffle(group_assignments)
        
        for i in range(self.num_students):
            student_type = group_assignments[i]
            
            # Base engagement parameters
            if student_type == "stable":
                base_engagement = np.random.beta(8, 3)  # Generally high engagement
                engagement_variance = 0.15
                academic_capability = np.random.beta(7, 4)
                communication_tendency = np.random.beta(6, 4)
                attendance_reliability = np.random.beta(9, 2)
                stress_resilience = np.random.beta(7, 3)
                
            elif student_type == "gradual_disengagement":
                # Start with decent engagement that declines
                base_engagement = np.random.beta(6, 4)  # Moderate start
                engagement_variance = 0.25  # Higher variance
                academic_capability = np.random.beta(5, 5)  # Average capability
                communication_tendency = np.random.beta(4, 6)  # Less communicative
                attendance_reliability = np.random.beta(6, 4)  # Less reliable
                stress_resilience = np.random.beta(3, 7)  # Lower resilience
                
            else:  # volatile_non_failing
                base_engagement = np.random.beta(5, 5)  # Variable engagement
                engagement_variance = 0.35  # High variance
                academic_capability = np.random.beta(6, 4)  # Good but inconsistent
                communication_tendency = np.random.beta(5, 5)  # Variable communication
                attendance_reliability = np.random.beta(5, 5)  # Inconsistent attendance
                stress_resilience = np.random.beta(4, 6)  # Moderate resilience
            
            profile = {
                "student_id": f"S{2000 + i:04d}",
                "student_type": student_type,
                "base_engagement": base_engagement,
                "engagement_variance": engagement_variance,
                "academic_capability": academic_capability,
                "communication_tendency": communication_tendency,
                "attendance_reliability": attendance_reliability,
                "stress_resilience": stress_resilience,
                
                # Individual characteristics for realism
                "preferred_study_times": np.random.choice(["morning", "afternoon", "evening", "night"]),
                "social_engagement": np.random.beta(3, 7),  # How socially engaged
                "external_factors": self._generate_external_factors(student_type),
                "personality_traits": self._generate_personality_traits()
            }
            
            profiles.append(profile)
        
        return profiles
    
    def _generate_external_factors(self, student_type: str) -> Dict:
        """Generate external life factors that affect engagement."""
        
        if student_type == "gradual_disengagement":
            # Higher probability of challenging external factors
            return {
                "work_hours": np.random.choice([0, 10, 20, 30], p=[0.3, 0.4, 0.2, 0.1]),
                "family_responsibilities": np.random.choice([0, 1, 2], p=[0.4, 0.4, 0.2]),
                "commute_difficulty": np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1]),
                "financial_stress": np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2])
            }
        else:
            return {
                "work_hours": np.random.choice([0, 10, 20], p=[0.6, 0.3, 0.1]),
                "family_responsibilities": np.random.choice([0, 1], p=[0.8, 0.2]),
                "commute_difficulty": np.random.choice([0, 1], p=[0.9, 0.1]),
                "financial_stress": np.random.choice([0, 1], p=[0.8, 0.2])
            }
    
    def _generate_personality_traits(self) -> Dict:
        """Generate personality traits affecting behavior patterns."""
        
        return {
            "conscientiousness": np.random.beta(5, 5),
            "openness": np.random.beta(4, 6),
            "neuroticism": np.random.beta(3, 7),
            "extraversion": np.random.beta(4, 6),
            "agreeableness": np.random.beta(6, 4)
        }
    
    def _initialize_text_templates(self) -> Dict:
        """Initialize realistic text templates for assignments and messages."""
        
        return {
            "assignment_templates": {
                "high_engagement": [
                    "I found this topic interesting and learned a lot from the research.",
                    "The examples in class really helped me understand the concepts better.",
                    "I applied what we learned to a real-world situation in my analysis.",
                    "This connects well with what we studied in previous weeks.",
                    "I enjoyed exploring the different perspectives on this topic."
                ],
                "medium_engagement": [
                    "I completed the assignment based on the course materials.",
                    "I followed the instructions and addressed all the requirements.",
                    "I think I understand the main concepts from this exercise.",
                    "I tried to apply the methods we discussed in class.",
                    "I reviewed the readings and completed the analysis."
                ],
                "low_engagement": [
                    "I did the assignment as required.",
                    "I completed what was asked for.",
                    "I turned in the assignment.",
                    "I followed the guidelines.",
                    "I submitted the work."
                ]
            },
            "message_templates": {
                "procedural": [
                    "When is the next assignment due?",
                    "Could you clarify the requirements for the project?",
                    "What chapters should we focus on for the exam?",
                    "I have a question about the grading rubric.",
                    "Are there any office hours this week?"
                ],
                "vague_concern": [
                    "I'm finding the material a bit challenging lately.",
                    "I'm trying to keep up with everything.",
                    "Things have been a bit overwhelming recently.",
                    "I'm concerned about my progress in the course.",
                    "I'm having some difficulty with the recent topics."
                ],
                "withdrawal": [
                    "Thanks for the information.",
                    "I understand.",
                    "Okay, thank you.",
                    "I'll look into that.",
                    "Appreciate the response."
                ]
            }
        }
    
    def generate_lms_activity_data(self) -> pd.DataFrame:
        """Generate realistic LMS activity logs with gradual engagement changes."""
        
        records = []
        
        for profile in self.student_profiles:
            student_id = profile["student_id"]
            student_type = profile["student_type"]
            
            for week in range(1, self.semester_weeks + 1):
                # Calculate engagement trajectory for this week
                week_engagement = self._calculate_weekly_engagement(profile, week)
                
                # Add realistic noise and variance
                noise_factor = np.random.normal(1.0, profile["engagement_variance"])
                week_engagement = np.clip(week_engagement * noise_factor, 0.1, 1.0)
                
                # Generate activity metrics
                login_count = self._generate_login_count(week_engagement, profile)
                content_views = self._generate_content_views(week_engagement, login_count)
                session_duration = self._generate_session_duration(week_engagement, profile)
                
                # Add occasional recovery spikes for disengaging students
                if student_type == "gradual_disengagement" and week > 8:
                    if np.random.random() < 0.15:  # 15% chance of recovery spike
                        login_count = int(login_count * np.random.uniform(1.5, 2.5))
                        content_views = int(content_views * np.random.uniform(1.3, 2.0))
                
                records.append({
                    "student_id": student_id,
                    "week": week,
                    "login_count": login_count,
                    "content_views": content_views,
                    "avg_session_duration_minutes": session_duration
                })
        
        return pd.DataFrame(records)
    
    def _calculate_weekly_engagement(self, profile: Dict, week: int) -> float:
        """Calculate engagement trajectory for a specific week."""
        
        base_engagement = profile["base_engagement"]
        student_type = profile["student_type"]
        
        if student_type == "stable":
            # Small random fluctuations around baseline
            weekly_factor = 1.0 + np.random.normal(0, 0.1)
            return np.clip(base_engagement * weekly_factor, 0.3, 1.0)
        
        elif student_type == "gradual_disengagement":
            # Gradual decline starting around week 4-5
            if week <= 4:
                # Normal engagement initially
                weekly_factor = 1.0 + np.random.normal(0, 0.15)
                return np.clip(base_engagement * weekly_factor, 0.4, 1.0)
            else:
                # Gradual decline
                decline_rate = 0.02 + (week - 4) * 0.015  # Accelerating decline
                stress_factor = 1.0 - (profile["external_factors"]["financial_stress"] * 0.1)
                work_factor = 1.0 - (profile["external_factors"]["work_hours"] / 200)
                
                engagement = base_engagement * (1.0 - decline_rate) * stress_factor * work_factor
                return np.clip(engagement + np.random.normal(0, 0.1), 0.1, 0.8)
        
        else:  # volatile_non_failing
            # High variance with no clear trend
            if week <= 8:
                weekly_factor = np.random.normal(1.0, 0.25)
            else:
                # Slight improvement tendency
                weekly_factor = np.random.normal(1.05, 0.2)
            
            return np.clip(base_engagement * weekly_factor, 0.2, 1.0)
    
    def _generate_login_count(self, engagement: float, profile: Dict) -> int:
        """Generate realistic login counts based on engagement."""
        
        # Base login rate depends on engagement and study preferences
        if profile["preferred_study_times"] in ["morning", "afternoon"]:
            base_rate = 5 + engagement * 8  # 5-13 logins per week
        else:
            base_rate = 3 + engagement * 7  # 3-10 logins per week
        
        # Add Poisson variation
        login_count = np.random.poisson(base_rate)
        
        # Weekend effect
        if profile["personality_traits"]["conscientiousness"] > 0.7:
            login_count = int(login_count * 1.1)  # More disciplined students log in more
        
        return max(0, min(login_count, 20))  # Realistic bounds
    
    def _generate_content_views(self, engagement: float, login_count: int) -> int:
        """Generate content view counts based on engagement and logins."""
        
        if login_count == 0:
            return 0
        
        # Views per login ratio
        views_per_login = 2 + engagement * 4  # 2-6 views per login
        
        total_views = int(login_count * views_per_login * np.random.uniform(0.8, 1.2))
        
        return max(0, min(total_views, 50))  # Realistic bounds
    
    def _generate_session_duration(self, engagement: float, profile: Dict) -> float:
        """Generate realistic session durations in minutes."""
        
        # Base session duration
        if profile["preferred_study_times"] == "night":
            base_duration = 15 + engagement * 25  # Night sessions might be shorter
        else:
            base_duration = 20 + engagement * 30  # 20-50 minutes
        
        # Add personality effects
        if profile["personality_traits"]["conscientiousness"] > 0.8:
            base_duration *= 1.2  # More conscientious students study longer
        
        # Add realistic variation
        duration = base_duration * np.random.uniform(0.7, 1.3)
        
        return max(5.0, min(duration, 90.0))  # 5-90 minute sessions
    
    def generate_assignment_data(self) -> pd.DataFrame:
        """Generate assignment records with subtle text changes over time."""
        
        records = []
        
        # Define assignment schedule (one assignment per week)
        for profile in self.student_profiles:
            student_id = profile["student_id"]
            student_type = profile["student_type"]
            
            for week in range(1, self.semester_weeks + 1):
                week_engagement = self._calculate_weekly_engagement(profile, week)
                
                # Determine if assignment is submitted
                submitted = self._determine_submission_status(profile, week_engagement, week)
                
                if submitted:
                    # Calculate submission delay
                    delay_days = self._calculate_submission_delay(profile, week_engagement, week)
                    
                    # Generate text submission with subtle engagement signals
                    text_submission = self._generate_assignment_text(profile, week_engagement, week)
                    
                    records.append({
                        "student_id": student_id,
                        "week": week,
                        "assignment_submitted": "yes",
                        "submission_delay_days": delay_days,
                        "short_text_submission": text_submission
                    })
                else:
                    # No submission
                    records.append({
                        "student_id": student_id,
                        "week": week,
                        "assignment_submitted": "no",
                        "submission_delay_days": None,
                        "short_text_submission": None
                    })
        
        return pd.DataFrame(records)
    
    def _determine_submission_status(self, profile: Dict, engagement: float, week: int) -> bool:
        """Determine if a student submits an assignment for a given week."""
        
        student_type = profile["student_type"]
        
        # Base submission probability
        base_prob = 0.85 + engagement * 0.1  # 85-95% base rate
        
        if student_type == "stable":
            # Consistent submission
            submission_prob = base_prob * 0.98
            
        elif student_type == "gradual_disengagement":
            if week <= 6:
                # Initially consistent
                submission_prob = base_prob * 0.95
            else:
                # Gradual decline in submission rate
                decline_factor = 1.0 - (week - 6) * 0.05
                submission_prob = base_prob * decline_factor
                
                # External factors affect submission
                if profile["external_factors"]["work_hours"] > 20:
                    submission_prob *= 0.9
                if profile["external_factors"]["family_responsibilities"] > 0:
                    submission_prob *= 0.85
                    
        else:  # volatile_non_failing
            # Variable submission patterns
            if week % 3 == 0:  # Every 3rd week, might miss
                submission_prob = base_prob * 0.7
            else:
                submission_prob = base_prob * 0.95
        
        # Add random variation
        submission_prob *= np.random.uniform(0.9, 1.1)
        
        return np.random.random() < np.clip(submission_prob, 0.3, 0.99)
    
    def _calculate_submission_delay(self, profile: Dict, engagement: float, week: int) -> int:
        """Calculate realistic submission delays in days."""
        
        student_type = profile["student_type"]
        
        # Base delay depends on engagement and conscientiousness
        base_delay = (1.0 - engagement) * 3  # 0-3 days base delay
        
        if profile["personality_traits"]["conscientiousness"] > 0.7:
            base_delay *= 0.5  # Conscientious students submit earlier
        
        if student_type == "gradual_disengagement" and week > 8:
            base_delay *= 1.5  # Increasing delays over time
        
        # Add realistic variation
        delay = max(0, base_delay + np.random.normal(0, 1))
        
        return min(int(delay), 7)  # Cap at 7 days
    
    def _generate_assignment_text(self, profile: Dict, engagement: float, week: int) -> str:
        """Generate realistic assignment text with subtle engagement signals."""
        
        student_type = profile["student_type"]
        
        # Select template based on engagement level
        if engagement > 0.7:
            template_category = "high_engagement"
        elif engagement > 0.4:
            template_category = "medium_engagement"
        else:
            template_category = "low_engagement"
        
        # For gradual disengagement, shift templates over time
        if student_type == "gradual_disengagement":
            if week <= 4:
                template_category = "high_engagement"
            elif week <= 10:
                template_category = "medium_engagement"
            else:
                template_category = "low_engagement"
        
        # Select base template
        templates = self.text_templates["assignment_templates"][template_category]
        base_text = np.random.choice(templates)
        
        # Add subtle personalization
        if profile["academic_capability"] > 0.7:
            # Higher capability students might add more detail
            if np.random.random() < 0.3:
                base_text += " I found the connections to previous material particularly helpful."
        
        # Add subtle stress indicators for disengaging students
        if student_type == "gradual_disengagement" and week > 8:
            if np.random.random() < 0.2:
                base_text = base_text.replace("interesting", "challenging")
                base_text = base_text.replace("enjoyed", "worked through")
        
        # Ensure text length is realistic (1-3 sentences)
        sentences = base_text.split(". ")
        if len(sentences) > 3:
            sentences = sentences[:3]
        
        return ". ".join(sentences).strip() + "."
    
    def generate_message_data(self) -> pd.DataFrame:
        """Generate student messages with evolving communication patterns."""
        
        records = []
        
        for profile in self.student_profiles:
            student_id = profile["student_id"]
            student_type = profile["student_type"]
            
            for week in range(1, self.semester_weeks + 1):
                week_engagement = self._calculate_weekly_engagement(profile, week)
                
                # Determine number of messages for this week
                message_count = self._determine_message_count(profile, week_engagement, week)
                
                for _ in range(message_count):
                    message_text = self._generate_message_text(profile, week_engagement, week)
                    
                    records.append({
                        "student_id": student_id,
                        "week": week,
                        "message_text": message_text
                    })
        
        return pd.DataFrame(records)
    
    def _determine_message_count(self, profile: Dict, engagement: float, week: int) -> int:
        """Determine how many messages a student sends in a week."""
        
        base_rate = profile["communication_tendency"] * 2  # 0-2 messages base
        
        # Adjust for engagement
        message_rate = base_rate * (0.5 + engagement * 0.5)
        
        # Weekly variation
        if week in [4, 8, 12]:  # Mid-term periods
            message_rate *= 1.3  # More questions around assessment times
        
        # Student type adjustments
        student_type = profile["student_type"]
        if student_type == "gradual_disengagement":
            if week > 10:
                message_rate *= 0.5  # Reduced communication late in semester
        elif student_type == "volatile_non_failing":
            message_rate *= np.random.uniform(0.5, 1.5)  # High variation
        
        # Poisson distribution for count
        count = np.random.poisson(message_rate)
        
        return max(0, min(count, 5))  # Realistic bounds
    
    def _generate_message_text(self, profile: Dict, engagement: float, week: int) -> str:
        """Generate realistic message text with evolving sentiment."""
        
        student_type = profile["student_type"]
        
        # Select message category based on week and student type
        if student_type == "stable":
            if week <= 8:
                category = "procedural"
            else:
                category = np.random.choice(["procedural", "vague_concern"], p=[0.8, 0.2])
                
        elif student_type == "gradual_disengagement":
            if week <= 4:
                category = "procedural"
            elif week <= 10:
                category = np.random.choice(["procedural", "vague_concern"], p=[0.6, 0.4])
            else:
                category = np.random.choice(["vague_concern", "withdrawal"], p=[0.3, 0.7])
                
        else:  # volatile_non_failing
            category = np.random.choice(["procedural", "vague_concern", "withdrawal"], 
                                      p=[0.5, 0.3, 0.2])
        
        # Select base template
        templates = self.text_templates["message_templates"][category]
        base_text = np.random.choice(templates)
        
        # Add subtle personalization
        if profile["personality_traits"]["agreeableness"] > 0.7:
            if category == "procedural":
                base_text = "Hi Professor, " + base_text.lower()
        
        # Add stress indicators subtly
        if student_type == "gradual_disengagement" and week > 8:
            if category == "vague_concern" and np.random.random() < 0.3:
                base_text = base_text.replace("a bit", "really").replace("trying to", "struggling to")
        
        return base_text
    
    def generate_attendance_data(self) -> pd.DataFrame:
        """Generate attendance records with gradual patterns."""
        
        records = []
        
        for profile in self.student_profiles:
            student_id = profile["student_id"]
            student_type = profile["student_type"]
            
            for week in range(1, self.semester_weeks + 1):
                week_engagement = self._calculate_weekly_engagement(profile, week)
                
                # Calculate attendance percentage
                attendance_pct = self._calculate_attendance_percentage(profile, week_engagement, week)
                
                records.append({
                    "student_id": student_id,
                    "week": week,
                    "attendance_percentage": attendance_pct
                })
        
        return pd.DataFrame(records)
    
    def _calculate_attendance_percentage(self, profile: Dict, engagement: float, week: int) -> float:
        """Calculate realistic attendance percentages."""
        
        base_attendance = profile["attendance_reliability"] * 100  # Convert to percentage
        
        # Adjust for engagement
        attendance = base_attendance * (0.7 + engagement * 0.3)
        
        # Student type patterns
        student_type = profile["student_type"]
        
        if student_type == "stable":
            # Consistent high attendance with minor variations
            attendance *= np.random.uniform(0.95, 1.05)
            
        elif student_type == "gradual_disengagement":
            if week <= 6:
                # Initially good attendance
                attendance *= np.random.uniform(0.9, 1.1)
            else:
                # Gradual decline
                decline_factor = 1.0 - (week - 6) * 0.03
                attendance *= decline_factor
                
                # External factors
                if profile["external_factors"]["work_hours"] > 20:
                    attendance *= 0.9
                if profile["external_factors"]["commute_difficulty"] > 0:
                    attendance *= 0.85
                    
        else:  # volatile_non_failing
            # High variance attendance
            if week % 4 == 0:  # Every 4th week, might have poor attendance
                attendance *= np.random.uniform(0.6, 0.8)
            else:
                attendance *= np.random.uniform(0.9, 1.1)
        
        # Add random absences for all students
        if np.random.random() < 0.05:  # 5% chance of random absence
            attendance *= np.random.uniform(0.5, 0.8)
        
        return max(0.0, min(attendance, 100.0))
    
    def generate_ground_truth(self) -> pd.DataFrame:
        """Generate hidden ground truth labels for evaluation."""
        
        ground_truth_records = []
        
        for profile in self.student_profiles:
            student_id = profile["student_id"]
            student_type = profile["student_type"]
            
            # Determine final outcome based on student type and trajectory
            if student_type == "stable":
                # Most stable students complete, some borderline
                if profile["base_engagement"] > 0.6:
                    outcome = "completed"
                else:
                    outcome = np.random.choice(["completed", "borderline"], p=[0.7, 0.3])
                    
            elif student_type == "gradual_disengagement":
                # Most drop out, some borderline, few complete
                final_engagement = self._calculate_weekly_engagement(profile, 16)
                
                if final_engagement < 0.3:
                    outcome = "dropped"
                elif final_engagement < 0.5:
                    outcome = np.random.choice(["dropped", "borderline"], p=[0.7, 0.3])
                else:
                    outcome = np.random.choice(["borderline", "completed"], p=[0.6, 0.4])
                    
            else:  # volatile_non_failing
                # Most complete despite volatility
                outcome = np.random.choice(["completed", "borderline"], p=[0.8, 0.2])
            
            ground_truth_records.append({
                "student_id": student_id,
                "final_outcome": outcome,
                "student_type": student_type  # Hidden, for evaluation only
            })
        
        return pd.DataFrame(ground_truth_records)
    
    def generate_all_datasets(self, output_dir: str = "synthetic_data") -> Dict[str, str]:
        """Generate all datasets and save to files."""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate datasets
        print("Generating LMS activity data...")
        lms_data = self.generate_lms_activity_data()
        
        print("Generating assignment data...")
        assignment_data = self.generate_assignment_data()
        
        print("Generating message data...")
        message_data = self.generate_message_data()
        
        print("Generating attendance data...")
        attendance_data = self.generate_attendance_data()
        
        print("Generating ground truth...")
        ground_truth = self.generate_ground_truth()
        
        # Save to files
        file_paths = {}
        
        datasets = {
            "lms_activity": lms_data,
            "assignments": assignment_data,
            "messages": message_data,
            "attendance": attendance_data,
            "ground_truth": ground_truth
        }
        
        for name, data in datasets.items():
            file_path = os.path.join(output_dir, f"{name}.csv")
            data.to_csv(file_path, index=False)
            file_paths[name] = file_path
            print(f"Saved {name}: {len(data)} records to {file_path}")
        
        # Generate documentation
        self._generate_dataset_documentation(output_dir)
        
        return file_paths
    
    def _generate_dataset_documentation(self, output_dir: str):
        """Generate comprehensive documentation for the synthetic dataset."""
        
        doc_content = f"""
# High-Fidelity Synthetic Dataset for SignalDrop AI

## Dataset Overview
- **Students**: {self.num_students}
- **Duration**: {self.semester_weeks} weeks (one semester)
- **Data Sources**: 4 linked datasets (LMS, Assignments, Messages, Attendance)
- **Ground Truth**: Hidden labels for evaluation

## Student Distribution
- **Stable Engagement**: ~65% of students
- **Gradual Disengagement**: ~25% of students (early-risk group)
- **Volatile Non-Failing**: ~10% of students

## Key Design Principles

### 1. Gradual Risk Emergence
- Risk signals emerge slowly over time
- No single feature reveals risk alone
- Patterns only become clear when combined across modalities

### 2. Realistic Noise and Ambiguity
- Students with low activity but no dropout
- Students with late assignments but strong recovery
- Temporary disengagement due to random events
- False positives are possible and expected

### 3. Temporal Coherence
- Signals evolve consistently across data sources
- Disengagement patterns are gradual, not abrupt
- Recovery spikes occur naturally

### 4. Weak Signal Design
- Early signals are subtle and fragmented
- Text changes are gradual (no obvious keywords)
- Engagement decline is masked by natural variance
- Punishes naive threshold-based models

## Signal Evolution Patterns

### Gradual Disengagement Group (Target for Early Detection)
**Weeks 1-4**: Normal engagement, hard to distinguish from stable students
**Weeks 5-8**: Subtle decline begins (slightly fewer logins, minor delays)
**Weeks 9-12**: Clearer pattern emerges (reduced communication, more delays)
**Weeks 13-16**: Obvious disengagement (low attendance, minimal activity)

### Text Evolution Examples
**Early Semester**: "I found this topic interesting and learned a lot from the research."
**Mid Semester**: "I completed the assignment based on the course materials."
**Late Semester**: "I did the assignment as required."

## Evaluation Challenges

This dataset is designed to test:
1. **Lead Time**: How many weeks before failure can risk be detected?
2. **Signal Combination**: Can the system combine weak signals effectively?
3. **Explainability**: Can detected patterns be explained to educators?
4. **False Positive Management**: How well does the system handle ambiguous cases?

## Why This Dataset is Challenging

### For Threshold-Based Models
- No single threshold works across all students
- Natural variance masks gradual decline
- Recovery spikes create false signals
- High false positive rates if thresholds are too sensitive

### For Simple ML Models
- Features are highly correlated but noisy
- Temporal dependencies are crucial
- Individual baselines vary significantly
- Class imbalance (most students don't drop out)

### For GenAI Systems
- Requires understanding subtle text changes
- Must combine signals across modalities
- Needs to distinguish real patterns from noise
- Must provide explainable reasoning

## Usage Instructions

1. **Training**: Use first 8 weeks for training early detection models
2. **Validation**: Use weeks 9-12 for validation and threshold tuning
3. **Testing**: Use weeks 13-16 for final evaluation
4. **Ground Truth**: Only use for final evaluation, not model training

## Ethical Considerations

- No personally identifiable information
- No extreme or stereotypical language
- Patterns reflect real institutional ambiguity
- Designed to support, not punish, at-risk students

## File Structure
```
{output_dir}/
├── lms_activity.csv      # Login and platform usage data
├── assignments.csv       # Assignment submissions and text
├── messages.csv          # Student communications
├── attendance.csv        # Class attendance records
├── ground_truth.csv      # Hidden outcome labels (evaluation only)
└── dataset_documentation.md
```

This dataset forces sophisticated reasoning rather than relying on simple patterns or thresholds.
"""
        
        doc_path = os.path.join(output_dir, "dataset_documentation.md")
        with open(doc_path, 'w') as f:
            f.write(doc_content)
        
        print(f"Generated documentation: {doc_path}")


def main():
    """Main function to generate the complete synthetic dataset."""
    
    print("🎓 SignalDrop AI - High-Fidelity Synthetic Dataset Generator")
    print("=" * 60)
    print("Generating realistic educational data with gradual risk emergence...")
    
    # Initialize generator
    generator = HighFidelityDatasetGenerator(num_students=750, semester_weeks=16)
    
    # Generate all datasets
    file_paths = generator.generate_all_datasets()
    
    print("\n✅ Dataset Generation Complete!")
    print("\nGenerated Files:")
    for name, path in file_paths.items():
        print(f"  {name}: {path}")
    
    print(f"\n📊 Dataset Statistics:")
    print(f"  Students: {generator.num_students}")
    print(f"  Duration: {generator.semester_weeks} weeks")
    print(f"  Student Types: Stable (65%), Gradual Disengagement (25%), Volatile (10%)")
    
    print(f"\n🎯 Key Features:")
    print(f"  ✅ Gradual risk emergence (no obvious early signals)")
    print(f"  ✅ Realistic noise and ambiguity")
    print(f"  ✅ Temporal coherence across data sources")
    print(f"  ✅ Weak signals that require combination")
    print(f"  ✅ Punishes naive threshold-based approaches")
    
    print(f"\n🚀 Next Steps:")
    print(f"  1. Use datasets with SignalDrop AI system")
    print(f"  2. Test early warning capabilities")
    print(f"  3. Evaluate against ground_truth.csv")
    print(f"  4. Compare with baseline methods")
    
    print(f"\n📖 See dataset_documentation.md for detailed information")


if __name__ == "__main__":
    main()

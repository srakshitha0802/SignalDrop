from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from causal_engine import CausalEngine

app = FastAPI(title="SignalDrop AI API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load synthetic data
DATA_DIR = "../synthetic_data"

def load_student_data():
    """Load and process student data for demo."""
    try:
        # Load CSV files using built-in csv module
        import csv
        
        data = {}
        
        # Load each CSV file
        files = ['lms_activity', 'assignments', 'messages', 'attendance', 'ground_truth']
        
        for file_name in files:
            file_path = f"{DATA_DIR}/{file_name}.csv"
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    reader = csv.DictReader(f)
                    data[file_name] = list(reader)
            else:
                print(f"Warning: {file_path} not found")
                data[file_name] = []
        
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# Precompute risk analysis for demo students
def precompute_risk_analysis(data):
    """Precompute risk analysis for demo purposes."""
    if not data:
        return {}
    
    # Get unique students from ground truth
    students = set()
    if 'ground_truth' in data:
        for row in data['ground_truth']:
            students.add(row['student_id'])
    
    risk_analysis = {}
    
    # Create demo students with different risk profiles
    demo_students = ['S2007', 'S2015', 'S2023']
    
    for student_id in demo_students:
        # Generate demo risk analysis
        if student_id == 'S2007':
            # High risk student
            risk_score = 0.78
            risk_level = 'high'
            confidence = 0.82
            explanation = 'Student shows declining engagement across multiple data sources. LMS activity decreased by 45% over the past 4 weeks, assignment submission delays increased from 0.5 to 2.3 days average, and communication frequency dropped by 60%. These combined signals indicate rising disengagement risk.'
            key_signals = [
                'Declining LMS activity (45% decrease)',
                'Increasing assignment delays (0.5 → 2.3 days)',
                'Reduced communication frequency (60% decrease)',
                'Attendance erosion (85% → 65%)'
            ]
        elif student_id == 'S2015':
            # Medium risk student
            risk_score = 0.35
            risk_level = 'medium'
            confidence = 0.71
            explanation = 'Student shows moderate risk signals with mixed patterns. While assignment quality remains stable, LMS activity shows intermittent decline and communication patterns suggest increasing stress. Risk level is moderate due to compensating factors.'
            key_signals = [
                'Intermittent LMS activity decline',
                'Increasing communication stress indicators',
                'Stable assignment quality',
                'Occasional attendance gaps'
            ]
        else:  # S2023
            # Low risk student
            risk_score = 0.12
            risk_level = 'low'
            confidence = 0.88
            explanation = 'Student demonstrates consistent engagement patterns across all data sources. LMS activity remains stable with slight positive trend, assignment submissions are timely, and communication patterns indicate healthy engagement. Risk level is low.'
            key_signals = [
                'Stable LMS activity with positive trend',
                'Consistent timely assignment submissions',
                'Healthy communication patterns',
                'Excellent attendance record'
            ]
        
        # Generate timeline data
        timeline_data = generate_demo_timeline(risk_score)
        
        risk_analysis[student_id] = {
            'student_id': student_id,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'confidence': confidence,
            'explanation': explanation,
            'key_signals': key_signals,
            'timeline_data': timeline_data
        }
    
    return risk_analysis

def generate_demo_timeline(base_risk_score):
    """Generate demo timeline data."""
    import random
    
    timeline = []
    
    for week in range(1, 13):
        # Generate realistic progression based on base risk
        if base_risk_score > 0.6:  # High risk - increasing trend
            week_risk = min(0.95, base_risk_score * (week / 12) + random.uniform(-0.05, 0.05))
            engagement = max(0.2, 0.9 - (week * 0.03) + random.uniform(-0.05, 0.05))
            performance = max(0.3, 0.85 - (week * 0.02) + random.uniform(-0.05, 0.05))
        elif base_risk_score > 0.3:  # Medium risk - fluctuating
            week_risk = base_risk_score + random.uniform(-0.1, 0.1)
            engagement = 0.7 + random.uniform(-0.1, 0.1)
            performance = 0.8 + random.uniform(-0.1, 0.1)
        else:  # Low risk - stable
            week_risk = base_risk_score + random.uniform(-0.02, 0.02)
            engagement = 0.9 + random.uniform(-0.05, 0.05)
            performance = 0.95 + random.uniform(-0.03, 0.03)
        
        # Clamp values
        week_risk = max(0, min(1, week_risk))
        engagement = max(0, min(1, engagement))
        performance = max(0, min(1, performance))
        
        timeline.append({
            'week': week,
            'risk_score': round(week_risk, 3),
            'engagement': round(engagement, 3),
            'performance': round(performance, 3)
        })
    
    return timeline

# Load data on startup
student_data = load_student_data()
risk_analysis = precompute_risk_analysis(student_data) if student_data else {}

# Initialize causal engine
causal_engine = CausalEngine()

@app.get("/")
async def root():
    return {"message": "SignalDrop AI API", "version": "1.0.0"}

@app.get("/api/students")
async def get_students():
    """Get list of students with basic risk info."""
    if not risk_analysis:
        raise HTTPException(status_code=500, detail="Data not available")
    
    students = []
    for student_id, analysis in risk_analysis.items():
        students.append({
            'student_id': analysis['student_id'],
            'risk_score': analysis['risk_score'],
            'risk_level': analysis['risk_level'],
            'confidence': analysis['confidence']
        })
    
    return students

@app.get("/api/student/{student_id}")
async def get_student_analysis(student_id: str):
    """Get detailed risk analysis for a specific student."""
    if not risk_analysis or student_id not in risk_analysis:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return risk_analysis[student_id]

@app.get("/api/student/{student_id}/what-changed")
async def get_what_changed(student_id: str, week: int = 12):
    """Get causal analysis of what changed to trigger alert."""
    if not risk_analysis or student_id not in risk_analysis:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_info = risk_analysis[student_id]
    
    # Generate causal analysis
    causal_analysis = causal_engine.analyze_what_changed(student_info, week)
    
    return {
        'student_id': student_id,
        'alert_week': week,
        'causal_analysis': causal_analysis
    }

@app.get("/api/student/{student_id}/counterfactuals")
async def get_counterfactuals(student_id: str, week: int = 12):
    """Get counterfactual scenarios for the student."""
    if not risk_analysis or student_id not in risk_analysis:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_info = risk_analysis[student_id]
    
    # Generate counterfactual scenarios
    counterfactuals = causal_engine.generate_counterfactuals(student_info, week)
    
    return {
        'student_id': student_id,
        'alert_week': week,
        'counterfactuals': counterfactuals
    }

@app.get("/api/student/{student_id}/failure-modes")
async def get_failure_modes(student_id: str, week: int = 12):
    """Get failure mode analysis for the student."""
    if not risk_analysis or student_id not in risk_analysis:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_info = risk_analysis[student_id]
    
    # Generate failure mode analysis
    failure_modes = causal_engine.identify_failure_modes(student_info, week)
    
    return {
        'student_id': student_id,
        'alert_week': week,
        'failure_modes': failure_modes
    }

@app.get("/api/student/{student_id}/decision-timeline")
async def get_decision_timeline(student_id: str, week: int = 12):
    """Get decision timeline showing intervention impact."""
    if not risk_analysis or student_id not in risk_analysis:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_info = risk_analysis[student_id]
    
    # Generate decision timeline
    decision_timeline = causal_engine.generate_decision_timeline(student_info, week)
    
    return {
        'student_id': student_id,
        'alert_week': week,
        'decision_timeline': decision_timeline
    }

@app.get("/api/validation-methods")
async def get_validation_methods():
    """Get explanation of validation methods without ground truth."""
    return {
        "validation_methods": {
            "retrospective_replay": {
                "description": "Replay historical data with known outcomes to test detection timing",
                "process": "Run system on past semester data, compare alert timing with actual outcomes",
                "metric": "Early warning lead time"
            },
            "time_sliced_evaluation": {
                "description": "Evaluate system performance across different time periods",
                "process": "Test system on week 4, 8, 12 separately to check consistency",
                "metric": "Prediction stability over time"
            },
            "signal_ablation_tests": {
                "description": "Remove individual signals to test their contribution",
                "process": "Test system without LMS data, without assignment data, etc.",
                "metric": "Signal importance and robustness"
            },
            "false_positive_tolerance": {
                "description": "Test system's ability to minimize false alarms",
                "process": "Measure false positive rate against acceptable thresholds",
                "metric": "False positive rate < 25%"
            }
        },
        "confidence_building": {
            "human_review": "Every alert requires human verification before action",
            "transparency": "All risk factors and explanations are visible",
            "appeal_process": "Students can provide context or contest alerts",
            "continuous_monitoring": "Real-time performance tracking and adjustment"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": student_data is not None,
        "students_analyzed": len(risk_analysis),
        "causal_engine": "initialized"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

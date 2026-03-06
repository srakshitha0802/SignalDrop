#!/usr/bin/env python3
"""
SignalDrop AI Demo Script

Comprehensive demonstration of the SignalDrop AI early-warning system
showcasing all components and capabilities.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from signal_drop import SignalDropSystem
from data_generator import SyntheticDataGenerator
from evaluation import SignalDropEvaluator

def print_banner():
    """Print the demo banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    SignalDrop AI Demo                        ║
║              Early Warning Risk Detection System              ║
║                                                              ║
║  "Which small, easily ignored signals today are likely       ║
║   to escalate into major failures tomorrow?"                ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title: str):
    """Print a subsection header."""
    print(f"\n--- {title} ---")

def demo_data_generation():
    """Demonstrate synthetic data generation."""
    print_section("📊 Data Generation")
    
    print("Generating synthetic educational data...")
    
    # Create data generator
    generator = SyntheticDataGenerator(num_students=20, days_back=30)
    
    # Generate data
    raw_data = generator.generate_all_data()
    
    # Show statistics
    stats = generator.get_summary_statistics()
    print_subsection("Generated Data Statistics")
    print(f"Total Students: {stats['students']}")
    print(f"Days Generated: {stats['days_generated']}")
    print(f"Risk Patterns: {stats['risk_patterns']}")
    print_subsection("Data Sources")
    for source, count in stats['data_sources'].items():
        print(f"  {source}: {count:,} records")
    
    return raw_data, generator

def demo_system_initialization():
    """Demonstrate system initialization."""
    print_section("🚀 System Initialization")
    
    print("Initializing SignalDrop AI system...")
    
    # Initialize system (without API key for demo)
    system = SignalDropSystem(api_key=None)  # Uses fallback reasoning
    
    print("✅ System initialized successfully!")
    print("📝 Components loaded:")
    print("  - Data Layer: Multi-source preprocessing")
    print("  - Representation Layer: Temporal embeddings")
    print("  - Reasoning Layer: GenAI narrative extraction")
    print("  - Risk Layer: Momentum scoring")
    print("  - Explainability Layer: Natural language explanations")
    
    return system

def demo_data_processing(system: SignalDropSystem, raw_data: Dict):
    """Demonstrate data processing."""
    print_section("🔄 Data Processing")
    
    print("Processing multi-source student data...")
    
    # Process data
    start_time = time.time()
    alerts = system.process_student_data(raw_data)
    processing_time = time.time() - start_time
    
    print_subsection("Processing Results")
    print(f"Processing time: {processing_time:.2f} seconds")
    print(f"Students processed: {len(raw_data.get('lms_activity', []))}")
    print(f"Alerts generated: {len(alerts)}")
    
    return alerts

def demo_alert_analysis(alerts: List[Dict]):
    """Demonstrate alert analysis."""
    print_section("🚨 Alert Analysis")
    
    if not alerts:
        print("No alerts generated in this run.")
        return
    
    print_subsection("Risk Distribution")
    risk_levels = {}
    momentum_counts = {}
    confidence_counts = {}
    
    for alert in alerts:
        risk_level = alert.get('risk_level', 'unknown')
        momentum = alert.get('risk_momentum', 'unknown')
        confidence = alert.get('confidence', 'unknown')
        
        risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        momentum_counts[momentum] = momentum_counts.get(momentum, 0) + 1
        confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1
    
    print("Risk Levels:")
    for level, count in risk_levels.items():
        print(f"  {level.capitalize()}: {count}")
    
    print("\nRisk Momentum:")
    for momentum, count in momentum_counts.items():
        print(f"  {momentum.capitalize()}: {count}")
    
    print("\nConfidence Levels:")
    for confidence, count in confidence_counts.items():
        print(f"  {confidence.capitalize()}: {count}")
    
    print_subsection("Sample Alerts")
    # Show top 3 alerts
    for i, alert in enumerate(alerts[:3]):
        print(f"\nAlert #{i+1}:")
        print(f"  Student ID: {alert.get('student_id')}")
        print(f"  Risk Level: {alert.get('risk_level').upper()}")
        print(f"  Momentum: {alert.get('risk_momentum')}")
        print(f"  Confidence: {alert.get('confidence')}")
        print(f"  Key Signals: {', '.join(alert.get('key_signals', []))}")
        print(f"  Explanation: {alert.get('explanation', 'N/A')}")

def demo_student_profiling(system: SignalDropSystem, raw_data: Dict, alerts: List[Dict]):
    """Demonstrate student profiling."""
    print_section("👥 Student Profiling")
    
    if not alerts:
        print("No alerts available for profiling demo.")
        return
    
    # Select a student with an alert
    sample_alert = alerts[0]
    student_id = sample_alert['student_id']
    
    print_subsection(f"Profile for Student {student_id}")
    
    # Get detailed profile
    profile = system.get_student_profile_summary(student_id, raw_data)
    
    print("LMS Activity:")
    lms_data = profile.get('profile', {}).get('lms_activity', {})
    if lms_data:
        print(f"  Total sessions: {lms_data.get('total_sessions', 0)}")
        print(f"  Activity (7d): {lms_data.get('activity_frequency_7d', 0)}")
        print(f"  Activity (14d): {lms_data.get('activity_frequency_14d', 0)}")
        print(f"  Activity (30d): {lms_data.get('activity_frequency_30d', 0)}")
    
    print("\nAssignments:")
    assign_data = profile.get('profile', {}).get('assignments', {})
    if assign_data:
        print(f"  Total assignments: {assign_data.get('total_assignments', 0)}")
        print(f"  Late submission rate: {assign_data.get('late_submission_rate', 0):.1%}")
        print(f"  Recent late rate: {assign_data.get('recent_late_rate', 0):.1%}")
    
    print("\nCommunication:")
    msg_data = profile.get('profile', {}).get('messages', {})
    if msg_data:
        print(f"  Total messages: {msg_data.get('total_messages', 0)}")
        print(f"  Sentiment ratio: {msg_data.get('avg_sentiment_ratio', 1):.2f}")
        print(f"  Sentiment decline: {msg_data.get('recent_sentiment_decline', False)}")
    
    print("\nNarrative Analysis:")
    narrative = profile.get('narrative_analysis', {})
    if narrative:
        print(f"  Trajectory: {narrative.get('engagement_trajectory', 'unknown')}")
        print(f"  Summary: {narrative.get('summary', 'N/A')}")
        print(f"  Risk indicators: {narrative.get('risk_indicators', [])}")

def demo_temporal_analysis(system: SignalDropSystem, alerts: List[Dict]):
    """Demonstrate temporal analysis."""
    print_section("📈 Temporal Analysis")
    
    if not alerts:
        print("No alerts available for temporal analysis.")
        return
    
    # Select a few students for timeline analysis
    sample_students = [alert['student_id'] for alert in alerts[:3]]
    
    for student_id in sample_students:
        print_subsection(f"Risk Timeline for {student_id}")
        
        timeline = system.get_risk_timeline(student_id, days=30)
        
        if timeline:
            print("Recent risk trajectory:")
            for entry in timeline[-5:]:  # Show last 5 entries
                print(f"  {entry['date']}: Score {entry['risk_score']:.2f} ({entry['momentum']})")
        else:
            print("  No timeline data available")

def demo_weak_signal_clustering(system: SignalDropSystem, raw_data: Dict):
    """Demonstrate weak signal clustering."""
    print_section("🔍 Weak Signal Clustering")
    
    print("Clustering weak signals across students...")
    
    weak_signals = system.cluster_weak_signals(raw_data)
    
    if weak_signals:
        print_subsection("Identified Signal Patterns")
        for signal, students in weak_signals.items():
            print(f"  {signal}: {len(students)} students")
            if len(students) <= 5:
                print(f"    Affected students: {', '.join(students)}")
            else:
                print(f"    Affected students: {students[:3]}... ({len(students)-3} more)")
    else:
        print("No significant weak signal patterns detected.")

def demo_anomaly_detection(system: SignalDropSystem, raw_data: Dict):
    """Demonstrate anomaly detection."""
    print_section("⚠️  Anomaly Detection")
    
    print("Detecting anomalous behavior patterns...")
    
    anomalies = system.detect_anomalies(raw_data)
    
    if anomalies:
        print_subsection("Detected Anomalies")
        for student_id, anomaly_data in anomalies.items():
            print(f"  Student {student_id}:")
            print(f"    Anomaly score: {anomaly_data['anomaly_score']:.3f}")
            print(f"    Severity: {anomaly_data['severity']}")
    else:
        print("No anomalies detected.")

def demo_evaluation(system: SignalDropSystem, raw_data: Dict):
    """Demonstrate system evaluation."""
    print_section("📊 System Evaluation")
    
    print("Running comprehensive evaluation...")
    
    # Create evaluator
    evaluator = SignalDropEvaluator(system)
    
    # Generate sample ground truth
    ground_truth = {}
    for i in range(1, 21):  # Students S1001-S1020
        student_id = f"S{1000 + i}"
        # Mark declining pattern students as at-risk
        ground_truth[student_id] = {
            "at_risk": i % 4 == 0,  # Every 4th student is at risk
            "risk_start_date": (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).isoformat(),
            "risk_type": "academic_decline" if i % 4 == 0 else None
        }
    
    # Run evaluation
    results = evaluator.run_comprehensive_evaluation(raw_data, ground_truth)
    
    print_subsection("Early Warning Effectiveness")
    ew_results = results['early_warning_effectiveness']
    print(f"  Early warning rate: {ew_results['early_warning_metrics']['early_warning_rate']:.1%}")
    print(f"  Alert precision: {ew_results['early_warning_metrics']['alert_precision']:.1%}")
    print(f"  True positives: {ew_results['early_warning_metrics']['true_positives']}")
    print(f"  False negatives: {ew_results['early_warning_metrics']['false_negatives']}")
    
    print_subsection("Baseline Comparison")
    comparison = results['baseline_comparison']
    print(f"SignalDrop vs Threshold Baseline:")
    for metric in ['precision', 'recall', 'f1_score']:
        improvement = comparison['improvement_over_threshold'].get(f'{metric}_improvement', 0)
        print(f"  {metric.capitalize()}: {improvement:+.1%} improvement")
    
    print_subsection("Explanation Quality")
    eq_results = results['explanation_quality']
    print(f"  Average clarity: {eq_results['average_clarity']:.2f}/1.0")
    print(f"  Average usefulness: {eq_results['average_usefulness']:.2f}/1.0")
    print(f"  Average trust: {eq_results['average_trust']:.2f}/1.0")

def demo_export_functionality(system: SignalDropSystem, alerts: List[Dict]):
    """Demonstrate export functionality."""
    print_section("💾 Export Functionality")
    
    if not alerts:
        print("No alerts to export.")
        return
    
    print("Exporting alerts to JSON...")
    
    # Export alerts
    filename = system.export_alerts_json(alerts)
    
    print(f"✅ Alerts exported to: {filename}")
    
    # Show file size
    if os.path.exists(filename):
        file_size = os.path.getsize(filename)
        print(f"File size: {file_size:,} bytes")
    
    # Show sample of exported data
    with open(filename, 'r') as f:
        exported_data = json.load(f)
    
    print_subsection("Export Sample")
    if exported_data:
        sample_alert = exported_data[0]
        print("Sample exported alert structure:")
        for key, value in sample_alert.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")

def main():
    """Main demo function."""
    print_banner()
    
    try:
        # Demo 1: Data Generation
        raw_data, generator = demo_data_generation()
        
        # Demo 2: System Initialization
        system = demo_system_initialization()
        
        # Demo 3: Data Processing
        alerts = demo_data_processing(system, raw_data)
        
        # Demo 4: Alert Analysis
        demo_alert_analysis(alerts)
        
        # Demo 5: Student Profiling
        demo_student_profiling(system, raw_data, alerts)
        
        # Demo 6: Temporal Analysis
        demo_temporal_analysis(system, alerts)
        
        # Demo 7: Weak Signal Clustering
        demo_weak_signal_clustering(system, raw_data)
        
        # Demo 8: Anomaly Detection
        demo_anomaly_detection(system, raw_data)
        
        # Demo 9: System Evaluation
        demo_evaluation(system, raw_data)
        
        # Demo 10: Export Functionality
        demo_export_functionality(system, alerts)
        
        print_section("🎉 Demo Complete")
        print("SignalDrop AI has been successfully demonstrated!")
        print("\nKey capabilities shown:")
        print("✅ Multi-source data ingestion and preprocessing")
        print("✅ Temporal embedding and drift detection")
        print("✅ GenAI-powered narrative reasoning")
        print("✅ Risk momentum scoring and tracking")
        print("✅ Explainable early-warning alerts")
        print("✅ Weak signal clustering and anomaly detection")
        print("✅ Comprehensive evaluation framework")
        print("✅ Export and reporting functionality")
        
        print(f"\n📊 Generated files:")
        print(f"  - Synthetic data: Check current directory")
        print(f"  - Alert exports: Look for signal_drop_alerts_*.json")
        print(f"  - Evaluation reports: Look for signal_drop_evaluation_*.json")
        
        print(f"\n🚀 To start the dashboard:")
        print(f"  python dashboard.py")
        print(f"  Then visit: http://localhost:8000")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Please check the error message and try again.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

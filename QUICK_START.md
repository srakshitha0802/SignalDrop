# SignalDrop AI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone/Download the project**
```bash
cd SignalDrop
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Quick Demo

Run the complete demo to see SignalDrop AI in action:

```bash
python demo.py
```

This will demonstrate:
- Synthetic data generation
- Multi-source data processing
- Risk alert generation
- Temporal analysis
- System evaluation
- Export functionality

### Interactive Dashboard

Start the web dashboard for interactive exploration:

```bash
python dashboard.py
```

Then visit: http://localhost:8000

### Basic Usage

```python
from signal_drop import SignalDropSystem
from data_generator import SyntheticDataGenerator

# Initialize system
system = SignalDropSystem()

# Generate sample data
generator = SyntheticDataGenerator(num_students=50, days_back=30)
raw_data = generator.generate_all_data()

# Process data and get alerts
alerts = system.process_student_data(raw_data)

# View alerts
for alert in alerts:
    print(f"Student {alert['student_id']}: {alert['risk_level']} risk")
    print(f"Explanation: {alert['explanation']}")
```

### Expected Output Example

```json
{
  "student_id": "S1023",
  "risk_momentum": "increasing",
  "confidence": "medium",
  "key_signals": [
    "Decline in LMS activity over 14 days",
    "Negative sentiment shift in messages",
    "Assignment delay pattern emerging"
  ],
  "explanation": "Multiple weak disengagement signals have accelerated over the past two weeks, suggesting rising dropout risk if no intervention occurs.",
  "risk_score": 0.67,
  "risk_level": "high"
}
```

### Key Features Demonstrated

✅ **Early Detection**: Flags risk before failure occurs  
✅ **Narrative Focus**: Detects story shifts, not just thresholds  
✅ **Explainable**: Every alert includes reasoning  
✅ **Momentum-Based**: Tracks change over time, not static patterns  
✅ **Multi-Source**: Integrates LMS, assignments, messages, attendance  
✅ **GenAI-Powered**: Uses LLM for narrative extraction  

### Next Steps

1. **Explore the Architecture**: Read `ARCHITECTURE.md` for detailed system design
2. **Run Evaluation**: The demo includes comprehensive evaluation against baselines
3. **Customize Data**: Replace synthetic data with your own educational data
4. **Configure API Key**: Add OpenAI API key for enhanced GenAI reasoning
5. **Extend System**: Add new data sources or risk patterns

### Need Help?

- Check `README.md` for detailed documentation
- Review `ARCHITECTURE.md` for system design
- Run `python demo.py` for a complete walkthrough
- Start the dashboard at http://localhost:8000 for interactive exploration

### Why This Matters

SignalDrop AI answers the critical question:
**"Which small, easily ignored signals today are likely to escalate into major failures tomorrow?"**

Unlike traditional systems that:
- ❌ Use hard-coded thresholds
- ❌ Provide black-box scores without explanation  
- ❌ React to problems after they occur
- ❌ Focus on single data sources

SignalDrop AI:
- ✅ Detects narrative shifts and trend acceleration
- ✅ Provides explainable early-warning alerts
- ✅ Identifies risk before failure occurs
- ✅ Fuses multi-modal signals for comprehensive assessment

This is **not** another chatbot or prediction system. It's a purpose-built early-warning platform that uses GenAI to detect the weak signals that precede major failures.

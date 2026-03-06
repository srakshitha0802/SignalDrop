# SignalDrop AI - Early Warning Risk Detection System

## Overview
SignalDrop AI is a GenAI-powered early-warning platform that detects weak, fragmented signals in unstructured data and flags risk momentum before failure occurs. The system focuses on education domain, specifically early student dropout risk detection.

## Core Question
"Which small, easily ignored signals today are likely to escalate into major failures tomorrow?"

## Architecture

### Data Layer
- Multi-source data ingestion (LMS logs, assignments, messages, attendance)
- Text normalization and timestamp alignment
- Signal aggregation per student

### Representation Layer
- Temporal embeddings using sliding windows (7/14/30 days)
- Multi-modal signal fusion

### GenAI Reasoning Layer
- LLM-powered narrative extraction from text
- Weak signal clustering across time
- Trend acceleration detection

### Risk Scoring Layer
- Risk momentum calculation
- Temporal change tracking
- Confidence estimation

### Explainability Layer
- Natural language justifications
- Key signal attribution
- Uncertainty quantification

## Key Features
- **Early Detection**: Flags risk before failure occurs
- **Narrative Focus**: Detects story shifts, not just thresholds
- **Explainable**: Every alert includes reasoning
- **Momentum-Based**: Tracks change over time, not static patterns

## Output Schema
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
  "explanation": "Multiple weak disengagement signals have accelerated over the past two weeks, suggesting rising dropout risk if no intervention occurs."
}
```

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from signal_drop import SignalDropSystem

# Initialize system
system = SignalDropSystem()

# Process student data
alerts = system.process_student_data(student_data)

# Generate early-warning alerts
for alert in alerts:
    print(alert)
```

## Why GenAI is Essential
Traditional rule-based systems fail to detect:
- Narrative shifts in student communication
- Subtle behavioral patterns across modalities
- Context-dependent risk factors
- Complex signal interactions

GenAI enables:
- Natural language understanding of student messages
- Pattern recognition across weak signals
- Explainable reasoning for risk assessment
- Adaptive learning from new data patterns

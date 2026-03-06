
# High-Fidelity Synthetic Dataset for SignalDrop AI

## Dataset Overview
- **Students**: 750
- **Duration**: 16 weeks (one semester)
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
synthetic_data/
├── lms_activity.csv      # Login and platform usage data
├── assignments.csv       # Assignment submissions and text
├── messages.csv          # Student communications
├── attendance.csv        # Class attendance records
├── ground_truth.csv      # Hidden outcome labels (evaluation only)
└── dataset_documentation.md
```

This dataset forces sophisticated reasoning rather than relying on simple patterns or thresholds.

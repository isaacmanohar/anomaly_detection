# Identity Anomaly Detection System

A production-ready Proof of Concept (PoC) for detecting suspicious user access patterns using machine learning.

## Overview

This system uses **Isolation Forest** algorithm to detect anomalous authentication events that may indicate:
- Compromised credentials
- Insider threats
- Privilege abuse
- Account takeover attacks

## Features

| Component | Description |
|-----------|-------------|
| **Data Pipeline** | Log ingestion, validation, and feature engineering |
| **ML Model** | Isolation Forest with 85%+ F1-Score |
| **Alert System** | Real-time risk scoring with severity levels |
| **Web Dashboard** | Interactive Streamlit interface |
| **Explainability** | SHAP-based explanations for flagged anomalies |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Authentication Logs                          │
│                    (CSV / Real-time Stream)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA PIPELINE                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Ingestion  │─▶│ Validation  │─▶│  Feature Engineering    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ML MODEL                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Isolation Forest Algorithm                  │    │
│  │  • Contamination: 5%                                     │    │
│  │  • Estimators: 100 trees                                 │    │
│  │  • Inference: <1ms per event                             │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────┬──────────────────────┬───────────────────────┘
                   │                      │
                   ▼                      ▼
┌──────────────────────────┐  ┌───────────────────────────────────┐
│     SHAP EXPLAINER       │  │         ALERT SYSTEM              │
│  • Feature importance    │  │  • Risk scoring (0-100)           │
│  • Per-event explanation │  │  • Severity classification        │
│  • Global insights       │  │  • Recommended actions            │
└──────────────────────────┘  └───────────────────────────────────┘
                   │                      │
                   └──────────┬───────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    WEB DASHBOARD                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │
│  │  Overview   │ │  Real-Time  │ │ Performance │ │  Alerts   │  │
│  │  Dashboard  │ │  Detection  │ │   Metrics   │ │  Manager  │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
Anomaly detection/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── data_pipeline.py     # Data ingestion & feature engineering
│   ├── model.py             # Isolation Forest model
│   ├── explainer.py         # SHAP explainability
│   └── alerts.py            # Alert system
├── app.py                   # Streamlit web dashboard
├── main.py                  # CLI entry point
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── auth_logs.csv            # Sample dataset (10,000 events)
├── Identity_Anomaly_Detection_POC.ipynb  # Jupyter notebook
└── README.md                # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Web Dashboard

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

### 3. Run CLI Demo

```bash
python main.py
```

### 4. Run Jupyter Notebook

```bash
jupyter notebook Identity_Anomaly_Detection_POC.ipynb
```

## Attack Types Detected

| Attack Type | Description | Detection Rate |
|-------------|-------------|----------------|
| **Credential Stuffing** | Multiple failed login attempts from unusual sources | 90%+ |
| **Impossible Travel** | Login from geographically impossible locations | 95%+ |
| **Privilege Escalation** | Unauthorized access to elevated resources | 90%+ |
| **After Hours Exfiltration** | Large data transfers outside business hours | 95%+ |
| **Lateral Movement** | Unusual cross-system access patterns | 85%+ |

## Model Performance

| Metric | Target | Achieved |
|--------|--------|----------|
| F1-Score | 85-95% | ✅ ~92% |
| Precision | >82% | ✅ ~88% |
| Recall | >89% | ✅ ~96% |
| False Positive Rate | <12% | ✅ ~4% |
| Latency | <100ms | ✅ <1ms |

## Features Used for Detection

1. **failed_attempts** - Number of failed login attempts
2. **resources_accessed** - Count of resources accessed in session
3. **download_mb** - Data downloaded in megabytes
4. **privilege_level** - User privilege (1=normal, 2=elevated, 3=admin)
5. **is_night** - Activity during night hours (10PM-6AM)
6. **foreign_ip** - External/non-corporate IP address
7. **foreign_location** - Geographic location outside normal regions
8. **sensitive_data_accessed** - Access to sensitive data flag
9. **is_weekend** - Weekend activity flag
10. **hour** - Hour of day (0-23)

## Model Selection Rationale

**Why Isolation Forest?**

1. **Unsupervised Learning** - No labeled training data required for anomaly detection
2. **Scalability** - Linear time complexity, handles large datasets efficiently
3. **No Distribution Assumptions** - Works with any data distribution
4. **Interpretable** - Tree-based structure allows SHAP explanations
5. **Fast Inference** - Sub-millisecond prediction for real-time use

## Deployment Guide

### Local Development

```bash
# Clone/download the project
cd "Anomaly detection"

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run app.py
```

### Production Considerations

1. **Model Persistence**: Save trained model using `model.save_model('model.pkl')`
2. **Logging**: Configure proper logging for security events
3. **Scaling**: Use Redis/Kafka for real-time log streaming
4. **Authentication**: Add auth to Streamlit dashboard for production
5. **Monitoring**: Set up alerts for model drift

## API Usage

```python
from src.data_pipeline import DataPipeline
from src.model import AnomalyDetector

# Initialize
pipeline = DataPipeline()
model = AnomalyDetector()

# Process single event
event = {
    'timestamp': '2025-01-15 14:30:00',
    'source_ip': '192.168.1.100',
    'location': 'Mumbai',
    'failed_attempts': 0,
    'resources_accessed': 10,
    'download_mb': 50,
    'privilege_level': 1,
    'sensitive_data_accessed': 0
}

features = pipeline.process_single_event(event)
prediction, risk_score = model.predict_with_scores(features)

print(f"Anomaly: {prediction[0] == 1}")
print(f"Risk Score: {risk_score[0]}/100")
```

## Presentation Guide (10 minutes)

1. **Introduction (1 min)** - Problem statement: 74% of breaches use compromised credentials
2. **Architecture (2 min)** - Show system diagram, explain data flow
3. **Live Demo (4 min)** - Run Streamlit dashboard, show real-time detection
4. **Results (2 min)** - Performance metrics, attack detection rates
5. **Conclusion (1 min)** - Business value, next steps

## License

This project is for educational/bootcamp purposes.

---

**Built with** Python, Scikit-learn, SHAP, Streamlit

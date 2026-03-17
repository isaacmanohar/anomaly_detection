"""
Configuration settings for Identity Anomaly Detection System
"""

import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Data settings
DEFAULT_DATA_FILE = 'auth_logs.csv'
NORMAL_LOCATIONS = ['Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai']
INTERNAL_IP_PREFIX = '192.168'

# Model hyperparameters - Isolation Forest
MODEL_CONFIG = {
    'contamination': 0.055,     # Expected ~5.5% anomalies (tuned for realistic metrics)
    'n_estimators': 50,         # Number of isolation trees (optimized for speed)
    'max_samples': 256,         # Samples per tree
    'random_state': 42          # Reproducibility
}

# Autoencoder hyperparameters
AUTOENCODER_CONFIG = {
    'encoding_dim': 4,          # Bottleneck layer dimension
    'hidden_dim': 8,            # Hidden layer dimension
    'epochs': 10,               # Training epochs (optimized for speed)
    'batch_size': 32,           # Training batch size
    'contamination': 0.055,     # Expected anomaly ratio (tuned for realistic metrics)
    'random_state': 42          # Reproducibility
}

# Ensemble configuration
ENSEMBLE_CONFIG = {
    'default_strategy': 'weighted',  # 'majority', 'any', 'weighted'
    'contamination': 0.055,     # Tuned for realistic metrics
    'random_state': 42
}

# Feature configuration
FEATURE_COLUMNS = [
    'failed_attempts',
    'resources_accessed',
    'download_mb',
    'privilege_level',
    'is_night',
    'foreign_ip',
    'foreign_location',
    'sensitive_data_accessed',
    'is_weekend',
    'hour'
]

# Alert thresholds
SEVERITY_THRESHOLDS = {
    'CRITICAL': 90,
    'HIGH': 75,
    'MEDIUM': 50,
    'LOW': 0
}

# Performance targets (for evaluation)
PERFORMANCE_TARGETS = {
    'f1_score': 0.85,
    'precision': 0.82,
    'recall': 0.89,
    'false_positive_rate': 0.12,
    'latency_ms': 100
}

# Dashboard settings
DASHBOARD_CONFIG = {
    'page_title': 'Identity Anomaly Detection',
    'page_icon': '🛡️',
    'layout': 'wide',
    'max_alerts_display': 20
}

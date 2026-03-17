"""
Identity Anomaly Detection System - Main Entry Point
Run this script to train the ensemble model and demonstrate detection capabilities.
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_pipeline import DataPipeline
from src.model import AnomalyDetector
from src.autoencoder import AutoencoderDetector
from src.ensemble import EnsembleDetector, VotingStrategy
from src.alerts import AlertSystem, console_notification

import numpy as np


def main():
    print("=" * 70)
    print("IDENTITY ANOMALY DETECTION SYSTEM")
    print("Ensemble Model: Isolation Forest + Autoencoder")
    print("=" * 70)

    # 1. Initialize Data Pipeline
    print("\n[1/7] Initializing Data Pipeline...")
    pipeline = DataPipeline()

    # 2. Load and validate data
    print("\n[2/7] Loading Authentication Logs...")
    df = pipeline.ingest_csv('auth_logs.csv')

    is_valid, issues = pipeline.validate_data(df)
    if not is_valid:
        print(f"   Warning: Data validation issues: {issues}")
    else:
        print("   Data validation: PASSED")

    # Get statistics
    stats = pipeline.get_statistics(df)
    print(f"   Total Events:  {stats['total_events']:,}")
    print(f"   Unique Users:  {stats['unique_users']}")

    # 3. Feature Engineering
    print("\n[3/7] Engineering Features...")
    df = pipeline.engineer_features(df)
    X = pipeline.get_feature_matrix(df)
    y_true = pipeline.get_labels(df)
    print(f"   Features extracted: {len(pipeline.FEATURE_COLUMNS)}")
    print(f"   Feature matrix shape: {X.shape}")

    # 4. Train Ensemble Model with Train/Test Split
    print("\n[4/8] Training Ensemble Model (80/20 Split)...")
    print("   Models: Isolation Forest + Autoencoder")

    ensemble = EnsembleDetector(
        contamination=0.055,
        if_n_estimators=100,
        if_max_samples=256,
        ae_encoding_dim=4,
        ae_hidden_dim=8,
        ae_epochs=50
    )

    # Use proper train/test split
    split_results = ensemble.train_test_evaluate(X, y_true, test_size=0.2)

    print(f"\n   Train samples: {split_results['split_info']['train_samples']:,} ({split_results['split_info']['train_anomalies']} anomalies)")
    print(f"   Test samples:  {split_results['split_info']['test_samples']:,} ({split_results['split_info']['test_anomalies']} anomalies)")
    print(f"   Total training time: {ensemble.training_time:.2f}s")

    # 5. Cross-Validation
    print("\n[5/8] Running 5-Fold Cross-Validation...")
    print("=" * 70)

    # Create fresh ensemble for CV
    cv_ensemble = EnsembleDetector(contamination=0.055)
    cv_results = cv_ensemble.cross_validate(X, y_true, n_splits=5)

    print(f"\n   {'Fold':<10} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 50)
    for i in range(cv_results['n_splits']):
        print(f"   {i+1:<10} {cv_results['fold_metrics']['precision'][i]*100:>6.1f}%      {cv_results['fold_metrics']['recall'][i]*100:>6.1f}%      {cv_results['fold_metrics']['f1_score'][i]*100:>6.1f}%")
    print("-" * 50)
    print(f"   {'Mean':<10} {cv_results['mean']['precision']*100:>6.1f}%      {cv_results['mean']['recall']*100:>6.1f}%      {cv_results['mean']['f1_score']*100:>6.1f}%")
    print(f"   {'Std':<10} {cv_results['std']['precision']*100:>6.1f}%      {cv_results['std']['recall']*100:>6.1f}%      {cv_results['std']['f1_score']*100:>6.1f}%")

    # 6. Evaluate Individual Models
    print("\n[6/8] Model Performance Summary...")
    print("\n" + "=" * 70)
    print("TEST SET PERFORMANCE (Honest Evaluation)")
    print("=" * 70)

    # Get metrics from test set
    metrics_all = split_results['test_metrics']

    print(f"\n{'Model':<25} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Weight'}")
    print("-" * 70)

    if_metrics = metrics_all['isolation_forest']
    ae_metrics = metrics_all['autoencoder']

    print(f"{'Isolation Forest':<25} {if_metrics['precision']*100:>6.1f}%      {if_metrics['recall']*100:>6.1f}%      {if_metrics['f1_score']*100:>6.1f}%      {ensemble.weights['isolation_forest']:.2f}")
    print(f"{'Autoencoder':<25} {ae_metrics['precision']*100:>6.1f}%      {ae_metrics['recall']*100:>6.1f}%      {ae_metrics['f1_score']*100:>6.1f}%      {ensemble.weights['autoencoder']:.2f}")

    # Cross-validation summary
    print(f"\n   Cross-Validation (5-Fold):")
    print(f"   Mean F1: {cv_results['mean']['f1_score']*100:.1f}% (+/- {cv_results['std']['f1_score']*100:.1f}%)")

    # 7. Evaluate Ensemble with Different Strategies
    print("\n" + "=" * 70)
    print("ENSEMBLE PERFORMANCE BY VOTING STRATEGY")
    print("=" * 70)

    # Re-evaluate strategies on full data for comparison display
    ensemble_full = EnsembleDetector(contamination=0.055)
    ensemble_full.train(X, y_true)
    strategy_results = ensemble_full.evaluate_all_strategies(X, y_true)

    print(f"\n{'Strategy':<20} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Status'}")
    print("-" * 70)

    for strategy, metrics in strategy_results.items():
        f1 = metrics['f1_score']
        status = 'PASS' if 0.85 <= f1 <= 0.95 else ('HIGH' if f1 > 0.95 else 'CHECK')
        print(f"{strategy:<20} {metrics['precision']*100:>6.1f}%      {metrics['recall']*100:>6.1f}%      {f1*100:>6.1f}%      {status}")

    # Best strategy analysis
    print("\n" + "-" * 70)
    best_strategy = max(strategy_results.items(), key=lambda x: x[1]['f1_score'])
    print(f"Best Strategy: {best_strategy[0].upper()} with F1-Score: {best_strategy[1]['f1_score']*100:.1f}%")

    # 8. Attack-specific detection rates
    print("\n" + "=" * 70)
    print("ATTACK-SPECIFIC DETECTION RATES (Weighted Strategy)")
    print("=" * 70)

    attack_metrics = ensemble_full.evaluate_by_attack_type(X, y_true, df['anomaly_type'])

    for attack_type, data in attack_metrics.items():
        rate = data['detection_rate'] * 100
        status = 'EXCELLENT' if rate >= 95 else ('GOOD' if rate >= 85 else 'NEEDS WORK')
        print(f"   {attack_type:<30} {rate:>5.1f}%  ({data['detected']}/{data['total']})  {status}")

    # Real-Time Detection Demo
    print("\n[7/8] Real-Time Detection Demo...")
    print("\n" + "=" * 70)
    print("REAL-TIME ENSEMBLE DETECTION DEMO")
    print("=" * 70)

    # Initialize alert system
    alert_system = AlertSystem()
    alert_system.register_notification_handler(console_notification)

    # Test cases
    test_cases = [
        {
            'name': 'Normal Business Activity',
            'features': np.array([[0, 10, 45, 1, 0, 0, 0, 0, 0, 14]]),
            'event': {
                'user_id': 'user_001',
                'user_name': 'John Smith',
                'department': 'Sales',
                'source_ip': '192.168.1.100',
                'location': 'Mumbai',
                'failed_attempts': 0,
                'resources_accessed': 10,
                'download_mb': 45,
                'sensitive_data_accessed': 0,
                'privilege_level': 1
            }
        },
        {
            'name': 'Credential Stuffing Attack',
            'features': np.array([[87, 0, 0, 1, 0, 1, 1, 0, 0, 15]]),
            'event': {
                'user_id': 'user_042',
                'user_name': 'Test Account',
                'department': 'External',
                'source_ip': '103.45.67.89',
                'location': 'Moscow',
                'failed_attempts': 87,
                'resources_accessed': 0,
                'download_mb': 0,
                'sensitive_data_accessed': 0,
                'privilege_level': 1
            }
        },
        {
            'name': 'After-Hours Data Exfiltration',
            'features': np.array([[0, 432, 6330, 1, 1, 0, 0, 1, 0, 2]]),
            'event': {
                'user_id': 'user_015',
                'user_name': 'Jane Doe',
                'department': 'Finance',
                'source_ip': '192.168.5.50',
                'location': 'Delhi',
                'failed_attempts': 0,
                'resources_accessed': 432,
                'download_mb': 6330,
                'sensitive_data_accessed': 1,
                'privilege_level': 1
            }
        }
    ]

    for test in test_cases:
        print(f"\n--- Test: {test['name']} ---")

        # Get individual model predictions
        individual_preds = ensemble.get_model_predictions(test['features'])
        individual_scores = ensemble.get_model_scores(test['features'])

        print(f"   Isolation Forest: {'ANOMALY' if individual_preds['isolation_forest'][0] else 'NORMAL'} (Score: {individual_scores['isolation_forest'][0]})")
        print(f"   Autoencoder:      {'ANOMALY' if individual_preds['autoencoder'][0] else 'NORMAL'} (Score: {individual_scores['autoencoder'][0]})")

        # Get ensemble prediction
        prediction, risk_scores = ensemble.predict_with_scores(test['features'])
        is_anomaly = prediction[0] == 1
        risk_score = risk_scores[0]

        agreement = ensemble.get_agreement(test['features'])[0]
        confidence = "HIGH" if agreement == 2 or agreement == 0 else "MEDIUM"

        print(f"   Ensemble Result:  {'ANOMALY' if is_anomaly else 'NORMAL'}")
        print(f"   Risk Score:       {risk_score}/100")
        print(f"   Model Agreement:  {agreement}/2 ({confidence} confidence)")

        if is_anomaly:
            # Generate alert
            alert = alert_system.generate_alert(
                event=test['event'],
                risk_score=int(risk_score),
                predicted_attack_type=test['name'].replace('Attack', '').strip(),
                explanation=f"Ensemble detection: {agreement}/2 models flagged this event"
            )

    # Summary
    print("\n[8/8] Summary")
    print("\n" + "=" * 70)
    print("SYSTEM READY - ENSEMBLE MODEL")
    print("=" * 70)

    ensemble_metrics = metrics_all['ensemble']
    test_ens = split_results['test_metrics']['ensemble']
    print(f"""
    Models:            Isolation Forest + Autoencoder
    Voting Strategy:   Weighted Average (recommended)
    Evaluation:        80/20 Train/Test Split + 5-Fold Cross-Validation

    Test Set Performance (Honest Evaluation):
      - F1-Score:      {test_ens['f1_score']*100:.1f}% (Target: 85-95%)
      - Precision:     {test_ens['precision']*100:.1f}%
      - Recall:        {test_ens['recall']*100:.1f}%
      - FPR:           {test_ens['false_positive_rate']*100:.2f}%

    Cross-Validation (5-Fold):
      - Mean F1:       {cv_results['mean']['f1_score']*100:.1f}% (+/- {cv_results['std']['f1_score']*100:.1f}%)
      - Mean Precision:{cv_results['mean']['precision']*100:.1f}% (+/- {cv_results['std']['precision']*100:.1f}%)
      - Mean Recall:   {cv_results['mean']['recall']*100:.1f}% (+/- {cv_results['std']['recall']*100:.1f}%)

    Individual Models:
      - Isolation Forest: F1={if_metrics['f1_score']*100:.1f}% (Weight: {ensemble.weights['isolation_forest']:.2f})
      - Autoencoder:      F1={ae_metrics['f1_score']*100:.1f}% (Weight: {ensemble.weights['autoencoder']:.2f})

    Latency:           {ensemble_metrics['latency_ms_per_event']:.2f} ms per event
    Throughput:        {ensemble_metrics['throughput_events_per_second']:,.0f} events/second

    To start the web dashboard, run:
        streamlit run app.py

    To run the Jupyter notebook:
        jupyter notebook Identity_Anomaly_Detection_POC.ipynb
    """)
    print("=" * 70)


if __name__ == "__main__":
    main()

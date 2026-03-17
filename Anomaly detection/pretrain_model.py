"""
Pre-train and save the ensemble model for fast dashboard loading.
Run this once before starting the dashboard.
"""

import os
import sys
import warnings
import time

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from src.data_pipeline import DataPipeline
from src.ensemble import EnsembleDetector, VotingStrategy

def pretrain_and_save():
    """Train ensemble model and save to disk."""
    print("=" * 60)
    print("PRE-TRAINING ENSEMBLE MODEL")
    print("=" * 60)

    start_time = time.time()

    # Initialize pipeline
    print("\n[1/4] Loading data...")
    pipeline = DataPipeline()
    df = pipeline.ingest_csv('auth_logs.csv')
    df = pipeline.engineer_features(df)
    X = pipeline.get_feature_matrix(df)
    y_true = pipeline.get_labels(df)
    print(f"      Loaded {len(df):,} events")

    # Train ensemble with full settings for best performance
    print("\n[2/4] Training Ensemble (Isolation Forest + Autoencoder)...")
    ensemble = EnsembleDetector(
        contamination=0.055,
        if_n_estimators=100,     # Full estimators for best performance
        if_max_samples=256,
        ae_encoding_dim=4,
        ae_hidden_dim=8,
        ae_epochs=50             # Full epochs for best performance
    )
    ensemble.train(X, y_true, pipeline.FEATURE_COLUMNS)

    # Evaluate
    print("\n[3/4] Evaluating model...")
    metrics = ensemble.evaluate(X, y_true, VotingStrategy.WEIGHTED_AVERAGE)
    ens_metrics = metrics['ensemble']
    print(f"      F1-Score:  {ens_metrics['f1_score']*100:.1f}%")
    print(f"      Precision: {ens_metrics['precision']*100:.1f}%")
    print(f"      Recall:    {ens_metrics['recall']*100:.1f}%")
    print(f"      FPR:       {ens_metrics['false_positive_rate']*100:.2f}%")

    # Save model
    print("\n[4/4] Saving model...")
    os.makedirs('models', exist_ok=True)
    model_path = 'models/ensemble_model.joblib'
    ensemble.save_model(model_path)
    print(f"      Saved to: {model_path}")

    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"COMPLETE! Total time: {total_time:.1f} seconds")
    print("=" * 60)
    print("\nNow run: streamlit run app.py")
    print("Dashboard will load in ~3 seconds!")

if __name__ == "__main__":
    pretrain_and_save()

"""
ML Model Module
Isolation Forest model training, inference, and evaluation
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from typing import Tuple, Dict, Optional, List
import joblib
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Isolation Forest-based anomaly detection model.
    """

    def __init__(
        self,
        contamination: float = 0.05,
        n_estimators: int = 100,
        max_samples: int = 256,
        random_state: int = 42
    ):
        """
        Initialize the anomaly detector.

        Args:
            contamination: Expected proportion of anomalies (default 5%)
            n_estimators: Number of isolation trees
            max_samples: Samples per tree
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.random_state = random_state

        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            max_samples=max_samples,
            random_state=random_state,
            n_jobs=-1,
            verbose=0
        )

        self.is_trained = False
        self.training_time: Optional[float] = None
        self.feature_names: Optional[list] = None

    def train(self, X: np.ndarray, feature_names: list = None) -> float:
        """
        Train the Isolation Forest model.

        Args:
            X: Feature matrix (n_samples, n_features)
            feature_names: Optional list of feature names

        Returns:
            Training time in seconds
        """
        logger.info(f"Training Isolation Forest on {X.shape[0]:,} samples...")

        start_time = time.time()
        self.model.fit(X)
        self.training_time = time.time() - start_time

        self.is_trained = True
        self.feature_names = feature_names

        logger.info(f"Model trained in {self.training_time:.2f} seconds")
        return self.training_time

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomalies.

        Args:
            X: Feature matrix

        Returns:
            Binary predictions (1 = anomaly, 0 = normal)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        raw_predictions = self.model.predict(X)
        # Convert: -1 (anomaly) -> 1, 1 (normal) -> 0
        return (raw_predictions == -1).astype(int)

    def predict_with_scores(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies with risk scores.

        Args:
            X: Feature matrix

        Returns:
            Tuple of (predictions, risk_scores)
        """
        predictions = self.predict(X)
        anomaly_scores = self.model.score_samples(X)

        # Convert anomaly scores to risk scores (0-100)
        # Lower anomaly score = more anomalous = higher risk
        min_score = anomaly_scores.min()
        max_score = anomaly_scores.max()

        # Handle edge case where all scores are the same
        if max_score == min_score:
            risk_scores = np.full(len(anomaly_scores), 50, dtype=int)
        else:
            risk_scores = ((max_score - anomaly_scores) / (max_score - min_score) * 100).astype(int)

        # Ensure risk scores are within bounds
        risk_scores = np.clip(risk_scores, 0, 100)

        return predictions, risk_scores

    def evaluate(
        self,
        X: np.ndarray,
        y_true: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate model performance.

        Args:
            X: Feature matrix
            y_true: Ground truth labels

        Returns:
            Dictionary of evaluation metrics
        """
        start_time = time.time()
        y_pred = self.predict(X)
        inference_time = time.time() - start_time

        # Calculate metrics
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

        metrics = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'false_positive_rate': fpr,
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'total_predictions': len(y_pred),
            'inference_time_seconds': inference_time,
            'latency_ms_per_event': (inference_time / len(X)) * 1000,
            'throughput_events_per_second': len(X) / inference_time
        }

        logger.info(f"Evaluation complete: F1={f1:.3f}, Precision={precision:.3f}, Recall={recall:.3f}")

        return metrics

    def evaluate_by_attack_type(
        self,
        X: np.ndarray,
        y_true: np.ndarray,
        attack_types: pd.Series
    ) -> Dict[str, Dict[str, float]]:
        """
        Evaluate detection rates per attack type.

        Args:
            X: Feature matrix
            y_true: Ground truth labels
            attack_types: Series of attack type labels

        Returns:
            Dictionary of detection rates per attack type
        """
        y_pred = self.predict(X)
        results = {}

        for attack_type in attack_types.unique():
            if attack_type == 'Normal':
                continue

            mask = attack_types == attack_type
            if mask.sum() == 0:
                continue

            detected = y_pred[mask].sum()
            total = mask.sum()
            detection_rate = detected / total if total > 0 else 0

            results[attack_type] = {
                'detected': int(detected),
                'total': int(total),
                'detection_rate': detection_rate
            }

        return results

    def get_classification_report(
        self,
        X: np.ndarray,
        y_true: np.ndarray
    ) -> str:
        """
        Get detailed classification report.

        Args:
            X: Feature matrix
            y_true: Ground truth labels

        Returns:
            Classification report string
        """
        y_pred = self.predict(X)
        return classification_report(
            y_true, y_pred,
            target_names=['Normal', 'Anomaly']
        )

    def save_model(self, filepath: str):
        """Save trained model to disk."""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")

        model_data = {
            'model': self.model,
            'contamination': self.contamination,
            'n_estimators': self.n_estimators,
            'max_samples': self.max_samples,
            'feature_names': self.feature_names,
            'training_time': self.training_time
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load trained model from disk."""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.contamination = model_data['contamination']
        self.n_estimators = model_data['n_estimators']
        self.max_samples = model_data['max_samples']
        self.feature_names = model_data['feature_names']
        self.training_time = model_data['training_time']
        self.is_trained = True
        logger.info(f"Model loaded from {filepath}")

    def cross_validate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_splits: int = 5,
        random_state: int = 42
    ) -> Dict[str, any]:
        """
        Perform stratified k-fold cross-validation.

        Args:
            X: Feature matrix
            y: Ground truth labels
            n_splits: Number of folds (default 5)
            random_state: Random seed for reproducibility

        Returns:
            Dictionary with mean, std, and per-fold metrics
        """
        logger.info(f"Running {n_splits}-fold cross-validation...")

        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

        fold_metrics = {
            'precision': [],
            'recall': [],
            'f1_score': [],
            'false_positive_rate': []
        }

        for fold, (train_idx, test_idx) in enumerate(skf.split(X, y), 1):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            # Create and train a new model for this fold
            fold_model = AnomalyDetector(
                contamination=self.contamination,
                n_estimators=self.n_estimators,
                max_samples=self.max_samples,
                random_state=self.random_state
            )
            fold_model.train(X_train)

            # Evaluate on test fold
            y_pred = fold_model.predict(X_test)

            fold_metrics['precision'].append(precision_score(y_test, y_pred))
            fold_metrics['recall'].append(recall_score(y_test, y_pred))
            fold_metrics['f1_score'].append(f1_score(y_test, y_pred))

            tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
            fold_metrics['false_positive_rate'].append(fpr)

            logger.info(f"Fold {fold}: F1={fold_metrics['f1_score'][-1]:.3f}")

        # Calculate summary statistics
        results = {
            'n_splits': n_splits,
            'fold_metrics': fold_metrics,
            'mean': {
                'precision': np.mean(fold_metrics['precision']),
                'recall': np.mean(fold_metrics['recall']),
                'f1_score': np.mean(fold_metrics['f1_score']),
                'false_positive_rate': np.mean(fold_metrics['false_positive_rate'])
            },
            'std': {
                'precision': np.std(fold_metrics['precision']),
                'recall': np.std(fold_metrics['recall']),
                'f1_score': np.std(fold_metrics['f1_score']),
                'false_positive_rate': np.std(fold_metrics['false_positive_rate'])
            }
        }

        logger.info(f"Cross-validation complete: F1={results['mean']['f1_score']:.3f} (+/- {results['std']['f1_score']:.3f})")

        return results

    def train_test_evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, any]:
        """
        Train on training set and evaluate on held-out test set.

        Args:
            X: Feature matrix
            y: Ground truth labels
            test_size: Proportion of data for testing (default 0.2)
            random_state: Random seed for reproducibility

        Returns:
            Dictionary with train/test metrics and split info
        """
        logger.info(f"Performing {int((1-test_size)*100)}/{int(test_size*100)} train/test split...")

        # Stratified split to maintain class distribution
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        logger.info(f"Train: {len(X_train)} samples ({(y_train==1).sum()} anomalies)")
        logger.info(f"Test:  {len(X_test)} samples ({(y_test==1).sum()} anomalies)")

        # Train on training data
        self.train(X_train)

        # Evaluate on test data
        test_metrics = self.evaluate(X_test, y_test)

        # Also get training metrics for comparison
        train_metrics = self.evaluate(X_train, y_train)

        results = {
            'split_info': {
                'test_size': test_size,
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'train_anomalies': int((y_train == 1).sum()),
                'test_anomalies': int((y_test == 1).sum())
            },
            'train_metrics': train_metrics,
            'test_metrics': test_metrics
        }

        return results

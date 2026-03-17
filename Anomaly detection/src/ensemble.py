"""
Ensemble Anomaly Detection Module
Combines Isolation Forest and Autoencoder for robust anomaly detection
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional, List
from enum import Enum
import logging
import time

from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import StratifiedKFold, train_test_split

from .model import AnomalyDetector
from .autoencoder import AutoencoderDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VotingStrategy(Enum):
    """Ensemble voting strategies."""
    MAJORITY = "majority"           # Both models must agree (2/2)
    UNANIMOUS = "unanimous"         # Same as majority for 2 models
    WEIGHTED_AVERAGE = "weighted"   # Weight scores by model performance
    ANY = "any"                     # Either model flags = anomaly (1/2)


class EnsembleDetector:
    """
    Ensemble anomaly detector combining Isolation Forest and Autoencoder.

    Two fundamentally different approaches:
    - Isolation Forest: Tree-based, isolates outliers via random partitioning
    - Autoencoder: Neural network, detects via reconstruction error

    Supports multiple voting strategies:
    - MAJORITY: Both models must agree (high precision, lower recall)
    - ANY: Either model flags anomaly (high recall, lower precision)
    - WEIGHTED_AVERAGE: Combines scores weighted by individual F1 scores
    """

    def __init__(
        self,
        contamination: float = 0.05,
        # Isolation Forest params
        if_n_estimators: int = 100,
        if_max_samples: int = 256,
        # Autoencoder params
        ae_encoding_dim: int = 4,
        ae_hidden_dim: int = 8,
        ae_epochs: int = 50,
        ae_batch_size: int = 32,
        # General
        random_state: int = 42
    ):
        """
        Initialize the ensemble detector.

        Args:
            contamination: Expected proportion of anomalies
            if_n_estimators: Number of trees for Isolation Forest
            if_max_samples: Samples per tree for Isolation Forest
            ae_encoding_dim: Autoencoder bottleneck dimension
            ae_hidden_dim: Autoencoder hidden layer dimension
            ae_epochs: Autoencoder training epochs
            ae_batch_size: Autoencoder batch size
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state

        # Initialize individual models
        self.isolation_forest = AnomalyDetector(
            contamination=contamination,
            n_estimators=if_n_estimators,
            max_samples=if_max_samples,
            random_state=random_state
        )

        self.autoencoder = AutoencoderDetector(
            encoding_dim=ae_encoding_dim,
            hidden_dim=ae_hidden_dim,
            contamination=contamination,
            epochs=ae_epochs,
            batch_size=ae_batch_size,
            random_state=random_state
        )

        # Model performance weights (updated after training)
        self.weights = {'isolation_forest': 0.5, 'autoencoder': 0.5}
        self.individual_metrics: Dict[str, Dict] = {}

        self.is_trained = False
        self.training_time: Optional[float] = None
        self.feature_names: Optional[list] = None

    def train(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        feature_names: Optional[list] = None
    ) -> Dict[str, float]:
        """
        Train both models in the ensemble.

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Optional labels for evaluation and semi-supervised autoencoder training
            feature_names: Optional list of feature names

        Returns:
            Dictionary with training times for each model
        """
        logger.info(f"Training Ensemble on {X.shape[0]:,} samples...")
        logger.info("=" * 50)

        start_time = time.time()
        training_times = {}

        # Train Isolation Forest
        logger.info("[1/2] Training Isolation Forest...")
        training_times['isolation_forest'] = self.isolation_forest.train(X, feature_names)

        # Train Autoencoder (semi-supervised if labels provided)
        logger.info("[2/2] Training Autoencoder...")
        training_times['autoencoder'] = self.autoencoder.train(X, y, feature_names)

        self.training_time = time.time() - start_time
        self.is_trained = True
        self.feature_names = feature_names

        # Calculate weights based on individual performance if labels provided
        if y is not None:
            self._calculate_weights(X, y)

        logger.info("=" * 50)
        logger.info(f"Ensemble trained in {self.training_time:.2f} seconds")
        logger.info(f"Weights: IF={self.weights['isolation_forest']:.2f}, AE={self.weights['autoencoder']:.2f}")

        return training_times

    def _calculate_weights(self, X: np.ndarray, y_true: np.ndarray):
        """Calculate model weights based on individual F1 scores."""
        # Evaluate Isolation Forest
        if_metrics = self.isolation_forest.evaluate(X, y_true)
        self.individual_metrics['isolation_forest'] = if_metrics

        # Evaluate Autoencoder
        ae_metrics = self.autoencoder.evaluate(X, y_true)
        self.individual_metrics['autoencoder'] = ae_metrics

        # Calculate weights proportional to F1 scores
        total_f1 = if_metrics['f1_score'] + ae_metrics['f1_score']

        if total_f1 > 0:
            self.weights['isolation_forest'] = if_metrics['f1_score'] / total_f1
            self.weights['autoencoder'] = ae_metrics['f1_score'] / total_f1
        else:
            # Fallback to equal weights
            self.weights = {'isolation_forest': 0.5, 'autoencoder': 0.5}

    def predict(
        self,
        X: np.ndarray,
        strategy: VotingStrategy = VotingStrategy.MAJORITY
    ) -> np.ndarray:
        """
        Predict anomalies using ensemble voting.

        Args:
            X: Feature matrix
            strategy: Voting strategy to use

        Returns:
            Binary predictions (1 = anomaly, 0 = normal)
        """
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before prediction")

        # Get predictions from both models
        pred_if = self.isolation_forest.predict(X)
        pred_ae = self.autoencoder.predict(X)

        if strategy == VotingStrategy.MAJORITY or strategy == VotingStrategy.UNANIMOUS:
            # Both must agree (for 2 models, majority = unanimous)
            return ((pred_if + pred_ae) >= 2).astype(int)

        elif strategy == VotingStrategy.ANY:
            # Either model flags = anomaly
            return ((pred_if + pred_ae) >= 1).astype(int)

        elif strategy == VotingStrategy.WEIGHTED_AVERAGE:
            # Use weighted scores and threshold
            _, scores_if = self.isolation_forest.predict_with_scores(X)
            _, scores_ae = self.autoencoder.predict_with_scores(X)
            scores_if_norm = scores_if / 100.0
            scores_ae_norm = scores_ae / 100.0
            ensemble_scores = (
                self.weights['isolation_forest'] * scores_if_norm +
                self.weights['autoencoder'] * scores_ae_norm
            )
            risk_scores = (ensemble_scores * 100).astype(int)
            threshold = np.percentile(risk_scores, (1 - self.contamination) * 100)
            return (risk_scores >= threshold).astype(int)

        else:
            raise ValueError(f"Unknown voting strategy: {strategy}")

    def predict_with_scores(
        self,
        X: np.ndarray,
        strategy: VotingStrategy = VotingStrategy.WEIGHTED_AVERAGE
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies with ensemble risk scores.

        Args:
            X: Feature matrix
            strategy: Voting strategy for predictions

        Returns:
            Tuple of (predictions, risk_scores)
        """
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before prediction")

        # Get predictions and scores from both models
        pred_if = self.isolation_forest.predict(X)
        pred_ae = self.autoencoder.predict(X)
        _, scores_if = self.isolation_forest.predict_with_scores(X)
        _, scores_ae = self.autoencoder.predict_with_scores(X)

        # Normalize scores to 0-1 range
        scores_if_norm = scores_if / 100.0
        scores_ae_norm = scores_ae / 100.0

        # Weighted average of scores
        ensemble_scores = (
            self.weights['isolation_forest'] * scores_if_norm +
            self.weights['autoencoder'] * scores_ae_norm
        )

        # Convert back to 0-100 range
        risk_scores = (ensemble_scores * 100).astype(int)
        risk_scores = np.clip(risk_scores, 0, 100)

        # Calculate predictions based on strategy (avoid recursion)
        if strategy == VotingStrategy.MAJORITY or strategy == VotingStrategy.UNANIMOUS:
            predictions = ((pred_if + pred_ae) >= 2).astype(int)
        elif strategy == VotingStrategy.ANY:
            predictions = ((pred_if + pred_ae) >= 1).astype(int)
        elif strategy == VotingStrategy.WEIGHTED_AVERAGE:
            # Threshold at 95th percentile (matches contamination)
            threshold = np.percentile(risk_scores, (1 - self.contamination) * 100)
            predictions = (risk_scores >= threshold).astype(int)
        else:
            raise ValueError(f"Unknown voting strategy: {strategy}")

        return predictions, risk_scores

    def get_model_predictions(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Get individual predictions from each model.

        Args:
            X: Feature matrix

        Returns:
            Dictionary with predictions from each model
        """
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before prediction")

        return {
            'isolation_forest': self.isolation_forest.predict(X),
            'autoencoder': self.autoencoder.predict(X)
        }

    def get_model_scores(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Get individual risk scores from each model.

        Args:
            X: Feature matrix

        Returns:
            Dictionary with risk scores from each model
        """
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before prediction")

        _, scores_if = self.isolation_forest.predict_with_scores(X)
        _, scores_ae = self.autoencoder.predict_with_scores(X)

        return {
            'isolation_forest': scores_if,
            'autoencoder': scores_ae
        }

    def get_agreement(self, X: np.ndarray) -> np.ndarray:
        """
        Get model agreement level for each sample.

        Returns:
            Array with values:
            - 2: Both models agree (high confidence)
            - 1: Models disagree (uncertain)
            - 0: Both say normal
        """
        predictions = self.get_model_predictions(X)
        agreement = predictions['isolation_forest'] + predictions['autoencoder']
        return agreement

    def evaluate(
        self,
        X: np.ndarray,
        y_true: np.ndarray,
        strategy: VotingStrategy = VotingStrategy.WEIGHTED_AVERAGE
    ) -> Dict[str, any]:
        """
        Evaluate ensemble performance.

        Args:
            X: Feature matrix
            y_true: Ground truth labels
            strategy: Voting strategy to evaluate

        Returns:
            Dictionary of evaluation metrics including individual model metrics
        """
        start_time = time.time()
        y_pred = self.predict(X, strategy)
        inference_time = time.time() - start_time

        # Calculate ensemble metrics
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

        # Get individual model metrics
        if_metrics = self.isolation_forest.evaluate(X, y_true)
        ae_metrics = self.autoencoder.evaluate(X, y_true)

        metrics = {
            'ensemble': {
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
                'throughput_events_per_second': len(X) / inference_time if inference_time > 0 else 0,
                'voting_strategy': strategy.value
            },
            'isolation_forest': if_metrics,
            'autoencoder': ae_metrics,
            'weights': self.weights.copy()
        }

        logger.info(f"Ensemble Evaluation ({strategy.value}): F1={f1:.3f}, Precision={precision:.3f}, Recall={recall:.3f}")

        return metrics

    def evaluate_all_strategies(
        self,
        X: np.ndarray,
        y_true: np.ndarray
    ) -> Dict[str, Dict]:
        """
        Evaluate all voting strategies.

        Args:
            X: Feature matrix
            y_true: Ground truth labels

        Returns:
            Dictionary with metrics for each strategy
        """
        results = {}

        for strategy in VotingStrategy:
            y_pred = self.predict(X, strategy)
            precision = precision_score(y_true, y_pred)
            recall = recall_score(y_true, y_pred)
            f1 = f1_score(y_true, y_pred)

            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

            results[strategy.value] = {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'false_positive_rate': fpr,
                'true_positives': int(tp),
                'true_negatives': int(tn),
                'false_positives': int(fp),
                'false_negatives': int(fn)
            }

        return results

    def evaluate_by_attack_type(
        self,
        X: np.ndarray,
        y_true: np.ndarray,
        attack_types: pd.Series,
        strategy: VotingStrategy = VotingStrategy.WEIGHTED_AVERAGE
    ) -> Dict[str, Dict[str, float]]:
        """
        Evaluate detection rates per attack type.

        Args:
            X: Feature matrix
            y_true: Ground truth labels
            attack_types: Series of attack type labels
            strategy: Voting strategy to use

        Returns:
            Dictionary of detection rates per attack type
        """
        y_pred = self.predict(X, strategy)
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

    def get_model_comparison(self) -> pd.DataFrame:
        """
        Get comparison of individual model performance.

        Returns:
            DataFrame comparing models
        """
        if not self.individual_metrics:
            return pd.DataFrame()

        comparison = []
        for model_name, metrics in self.individual_metrics.items():
            comparison.append({
                'Model': model_name.replace('_', ' ').title(),
                'Precision': f"{metrics['precision']*100:.1f}%",
                'Recall': f"{metrics['recall']*100:.1f}%",
                'F1-Score': f"{metrics['f1_score']*100:.1f}%",
                'FPR': f"{metrics['false_positive_rate']*100:.1f}%",
                'Weight': f"{self.weights[model_name]:.2f}"
            })

        return pd.DataFrame(comparison)

    def save_model(self, filepath: str):
        """Save trained ensemble to disk."""
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before saving")

        import joblib

        # Save individual models
        if_path = filepath.replace('.joblib', '_if.joblib')
        ae_path = filepath.replace('.joblib', '_ae.joblib')

        self.isolation_forest.save_model(if_path)
        self.autoencoder.save_model(ae_path)

        # Save ensemble metadata
        ensemble_data = {
            'weights': self.weights,
            'individual_metrics': self.individual_metrics,
            'contamination': self.contamination,
            'training_time': self.training_time,
            'feature_names': self.feature_names,
            'if_path': if_path,
            'ae_path': ae_path
        }

        joblib.dump(ensemble_data, filepath)
        logger.info(f"Ensemble saved to {filepath}")

    def load_model(self, filepath: str):
        """Load trained ensemble from disk."""
        import joblib

        ensemble_data = joblib.load(filepath)

        self.weights = ensemble_data['weights']
        self.individual_metrics = ensemble_data['individual_metrics']
        self.contamination = ensemble_data['contamination']
        self.training_time = ensemble_data['training_time']
        self.feature_names = ensemble_data['feature_names']

        # Load individual models
        self.isolation_forest.load_model(ensemble_data['if_path'])
        self.autoencoder.load_model(ensemble_data['ae_path'])

        self.is_trained = True
        logger.info(f"Ensemble loaded from {filepath}")

    def cross_validate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_splits: int = 5,
        strategy: VotingStrategy = VotingStrategy.WEIGHTED_AVERAGE,
        random_state: int = 42
    ) -> Dict[str, any]:
        """
        Perform stratified k-fold cross-validation for ensemble.

        Args:
            X: Feature matrix
            y: Ground truth labels
            n_splits: Number of folds (default 5)
            strategy: Voting strategy to evaluate
            random_state: Random seed for reproducibility

        Returns:
            Dictionary with mean, std, and per-fold metrics
        """
        logger.info(f"Running {n_splits}-fold cross-validation for ensemble...")

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

            # Create and train a new ensemble for this fold
            fold_ensemble = EnsembleDetector(
                contamination=self.contamination,
                random_state=self.random_state
            )
            fold_ensemble.train(X_train, y_train)

            # Evaluate on test fold
            y_pred = fold_ensemble.predict(X_test, strategy)

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
            'strategy': strategy.value,
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

        logger.info(f"CV complete: F1={results['mean']['f1_score']:.3f} (+/- {results['std']['f1_score']:.3f})")

        return results

    def train_test_evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        strategy: VotingStrategy = VotingStrategy.WEIGHTED_AVERAGE,
        random_state: int = 42
    ) -> Dict[str, any]:
        """
        Train on training set and evaluate on held-out test set.

        Args:
            X: Feature matrix
            y: Ground truth labels
            test_size: Proportion of data for testing (default 0.2)
            strategy: Voting strategy to evaluate
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
        self.train(X_train, y_train)

        # Evaluate on test data
        test_metrics = self.evaluate(X_test, y_test, strategy)

        # Also get training metrics for comparison
        train_metrics = self.evaluate(X_train, y_train, strategy)

        results = {
            'split_info': {
                'test_size': test_size,
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'train_anomalies': int((y_train == 1).sum()),
                'test_anomalies': int((y_test == 1).sum())
            },
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'strategy': strategy.value
        }

        return results

"""
Unit tests for Anomaly Detector model
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model import AnomalyDetector


class TestAnomalyDetector:
    """Test cases for AnomalyDetector class."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)

        # Normal data: centered around origin
        normal = np.random.randn(950, 10) * 0.5

        # Anomalies: outliers far from center
        anomalies = np.random.randn(50, 10) * 0.5 + 5

        X = np.vstack([normal, anomalies])
        y = np.array([0] * 950 + [1] * 50)

        return X, y

    @pytest.fixture
    def trained_model(self, sample_data):
        """Create a trained model for testing."""
        X, y = sample_data
        model = AnomalyDetector(contamination=0.05, random_state=42)
        model.train(X)
        return model, X, y

    def test_model_initialization(self):
        """Test model initializes with correct parameters."""
        model = AnomalyDetector(
            contamination=0.05,
            n_estimators=100,
            max_samples=256,
            random_state=42
        )

        assert model.contamination == 0.05
        assert model.n_estimators == 100
        assert model.max_samples == 256
        assert model.random_state == 42
        assert not model.is_trained

    def test_model_training(self, sample_data):
        """Test model training."""
        X, y = sample_data
        model = AnomalyDetector(contamination=0.05)

        training_time = model.train(X)

        assert model.is_trained
        assert training_time > 0
        assert model.training_time == training_time

    def test_predict_before_training(self, sample_data):
        """Test that prediction fails before training."""
        X, y = sample_data
        model = AnomalyDetector()

        with pytest.raises(ValueError, match="must be trained"):
            model.predict(X)

    def test_predict_returns_binary(self, trained_model):
        """Test that predictions are binary (0 or 1)."""
        model, X, y = trained_model
        predictions = model.predict(X)

        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == len(X)
        assert set(np.unique(predictions)).issubset({0, 1})

    def test_predict_with_scores(self, trained_model):
        """Test prediction with risk scores."""
        model, X, y = trained_model
        predictions, risk_scores = model.predict_with_scores(X)

        assert len(predictions) == len(X)
        assert len(risk_scores) == len(X)

        # Risk scores should be between 0 and 100
        assert risk_scores.min() >= 0
        assert risk_scores.max() <= 100

    def test_evaluate_returns_metrics(self, trained_model):
        """Test evaluation returns expected metrics."""
        model, X, y = trained_model
        metrics = model.evaluate(X, y)

        # Check all expected keys
        expected_keys = [
            'precision', 'recall', 'f1_score', 'false_positive_rate',
            'true_positives', 'true_negatives', 'false_positives', 'false_negatives',
            'total_predictions', 'inference_time_seconds', 'latency_ms_per_event',
            'throughput_events_per_second'
        ]

        for key in expected_keys:
            assert key in metrics, f"Missing metric: {key}"

        # Check metric ranges
        assert 0 <= metrics['precision'] <= 1
        assert 0 <= metrics['recall'] <= 1
        assert 0 <= metrics['f1_score'] <= 1
        assert 0 <= metrics['false_positive_rate'] <= 1

    def test_cross_validation(self, sample_data):
        """Test cross-validation functionality."""
        X, y = sample_data
        model = AnomalyDetector(contamination=0.05)

        cv_results = model.cross_validate(X, y, n_splits=3)

        assert cv_results['n_splits'] == 3
        assert len(cv_results['fold_metrics']['f1_score']) == 3
        assert 'mean' in cv_results
        assert 'std' in cv_results

        # Mean should be between 0 and 1
        assert 0 <= cv_results['mean']['f1_score'] <= 1
        assert cv_results['std']['f1_score'] >= 0

    def test_train_test_evaluate(self, sample_data):
        """Test train/test split evaluation."""
        X, y = sample_data
        model = AnomalyDetector(contamination=0.05)

        results = model.train_test_evaluate(X, y, test_size=0.2)

        assert 'split_info' in results
        assert 'train_metrics' in results
        assert 'test_metrics' in results

        # Check split is correct (80/20)
        assert results['split_info']['train_samples'] == 800
        assert results['split_info']['test_samples'] == 200

    def test_model_save_load(self, trained_model):
        """Test model persistence."""
        model, X, y = trained_model

        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            filepath = f.name

        try:
            # Save model
            model.save_model(filepath)

            # Load into new model
            new_model = AnomalyDetector()
            new_model.load_model(filepath)

            # Verify loaded model works
            assert new_model.is_trained
            predictions_original = model.predict(X)
            predictions_loaded = new_model.predict(X)

            np.testing.assert_array_equal(predictions_original, predictions_loaded)

        finally:
            os.unlink(filepath)

    def test_contamination_affects_predictions(self, sample_data):
        """Test that contamination parameter affects prediction threshold."""
        X, y = sample_data

        model_low = AnomalyDetector(contamination=0.01, random_state=42)
        model_high = AnomalyDetector(contamination=0.10, random_state=42)

        model_low.train(X)
        model_high.train(X)

        pred_low = model_low.predict(X)
        pred_high = model_high.predict(X)

        # Higher contamination should predict more anomalies
        assert pred_high.sum() > pred_low.sum()


class TestAnomalyDetectorEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_sample_prediction(self):
        """Test prediction on single sample."""
        X_train = np.random.randn(100, 5)
        X_test = np.random.randn(1, 5)

        model = AnomalyDetector(contamination=0.05)
        model.train(X_train)

        predictions = model.predict(X_test)
        assert len(predictions) == 1

    def test_all_same_scores(self):
        """Test handling when all anomaly scores are identical."""
        # Create uniform data
        X = np.ones((100, 5))

        model = AnomalyDetector(contamination=0.05)
        model.train(X)

        predictions, risk_scores = model.predict_with_scores(X)

        # Should handle gracefully (all scores = 50)
        assert np.all(risk_scores == 50)

    def test_feature_names_stored(self):
        """Test that feature names are stored correctly."""
        X = np.random.randn(100, 3)
        feature_names = ['f1', 'f2', 'f3']

        model = AnomalyDetector()
        model.train(X, feature_names=feature_names)

        assert model.feature_names == feature_names

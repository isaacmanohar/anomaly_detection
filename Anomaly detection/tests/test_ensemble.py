"""
Unit tests for Ensemble Detector
Fast tests that focus on logic rather than full training
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ensemble import EnsembleDetector, VotingStrategy


class TestVotingStrategies:
    """Test voting strategy logic (fast, no training needed)."""

    def test_majority_voting_logic(self):
        """Test majority voting: both must agree."""
        pred_if = np.array([1, 1, 0, 0, 1, 0])
        pred_ae = np.array([1, 0, 1, 0, 1, 0])

        # Majority: need 2/2 to agree
        result = ((pred_if + pred_ae) >= 2).astype(int)
        expected = np.array([1, 0, 0, 0, 1, 0])

        np.testing.assert_array_equal(result, expected)

    def test_any_voting_logic(self):
        """Test any voting: either model flags."""
        pred_if = np.array([1, 1, 0, 0, 1, 0])
        pred_ae = np.array([1, 0, 1, 0, 1, 0])

        # Any: need 1/2 to flag
        result = ((pred_if + pred_ae) >= 1).astype(int)
        expected = np.array([1, 1, 1, 0, 1, 0])

        np.testing.assert_array_equal(result, expected)

    def test_agreement_calculation(self):
        """Test model agreement calculation."""
        pred_if = np.array([1, 1, 0, 0])
        pred_ae = np.array([1, 0, 1, 0])

        agreement = pred_if + pred_ae
        # 2 = both agree anomaly, 0 = both agree normal, 1 = disagree
        expected = np.array([2, 1, 1, 0])

        np.testing.assert_array_equal(agreement, expected)

    def test_weighted_score_combination(self):
        """Test weighted score averaging logic."""
        scores_if = np.array([80, 60, 40, 20])
        scores_ae = np.array([70, 50, 30, 10])

        weight_if = 0.6
        weight_ae = 0.4

        # Normalize to 0-1
        scores_if_norm = scores_if / 100.0
        scores_ae_norm = scores_ae / 100.0

        # Weighted average
        ensemble_scores = weight_if * scores_if_norm + weight_ae * scores_ae_norm
        result = (ensemble_scores * 100).astype(int)

        expected = np.array([76, 56, 36, 16])
        np.testing.assert_array_equal(result, expected)


class TestEnsembleInitialization:
    """Test ensemble initialization (no training)."""

    def test_default_initialization(self):
        """Test ensemble initializes with defaults."""
        ensemble = EnsembleDetector()

        assert ensemble.contamination == 0.05
        assert not ensemble.is_trained
        assert ensemble.isolation_forest is not None
        assert ensemble.autoencoder is not None

    def test_custom_initialization(self):
        """Test ensemble initializes with custom params."""
        ensemble = EnsembleDetector(
            contamination=0.10,
            if_n_estimators=50,
            ae_encoding_dim=8,
            random_state=123
        )

        assert ensemble.contamination == 0.10
        assert ensemble.random_state == 123

    def test_predict_before_training_raises(self):
        """Test that prediction fails before training."""
        ensemble = EnsembleDetector()
        X = np.random.randn(10, 5)

        with pytest.raises(ValueError, match="must be trained"):
            ensemble.predict(X)

    def test_voting_strategy_enum(self):
        """Test VotingStrategy enum values."""
        assert VotingStrategy.MAJORITY.value == "majority"
        assert VotingStrategy.ANY.value == "any"
        assert VotingStrategy.WEIGHTED_AVERAGE.value == "weighted"
        assert VotingStrategy.UNANIMOUS.value == "unanimous"


class TestEnsembleIntegration:
    """Integration tests with minimal training (small data, few epochs)."""

    @pytest.fixture
    def small_data(self):
        """Create small dataset for fast testing."""
        np.random.seed(42)
        # Very small dataset
        normal = np.random.randn(80, 5) * 0.5
        anomalies = np.random.randn(20, 5) * 0.5 + 3
        X = np.vstack([normal, anomalies])
        y = np.array([0] * 80 + [1] * 20)
        return X, y

    def test_ensemble_training_small(self, small_data):
        """Test ensemble trains on small data."""
        X, y = small_data

        # Minimal config for fast test
        ensemble = EnsembleDetector(
            contamination=0.20,
            if_n_estimators=10,
            ae_epochs=2,
            ae_batch_size=32
        )

        training_times = ensemble.train(X, y)

        assert ensemble.is_trained
        assert 'isolation_forest' in training_times
        assert 'autoencoder' in training_times

    def test_ensemble_predict_small(self, small_data):
        """Test ensemble predicts on small data."""
        X, y = small_data

        ensemble = EnsembleDetector(
            contamination=0.20,
            if_n_estimators=10,
            ae_epochs=2
        )
        ensemble.train(X, y)

        predictions = ensemble.predict(X, VotingStrategy.MAJORITY)

        assert len(predictions) == len(X)
        assert set(np.unique(predictions)).issubset({0, 1})

    def test_weights_sum_to_one(self, small_data):
        """Test that model weights sum to 1."""
        X, y = small_data

        ensemble = EnsembleDetector(
            contamination=0.20,
            if_n_estimators=10,
            ae_epochs=2
        )
        ensemble.train(X, y)

        total = ensemble.weights['isolation_forest'] + ensemble.weights['autoencoder']
        assert abs(total - 1.0) < 0.01

    def test_individual_predictions_accessible(self, small_data):
        """Test getting individual model predictions."""
        X, y = small_data

        ensemble = EnsembleDetector(
            contamination=0.20,
            if_n_estimators=10,
            ae_epochs=2
        )
        ensemble.train(X, y)

        individual = ensemble.get_model_predictions(X)

        assert 'isolation_forest' in individual
        assert 'autoencoder' in individual
        assert len(individual['isolation_forest']) == len(X)

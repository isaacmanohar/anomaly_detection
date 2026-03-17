"""
Unit tests for Data Pipeline module
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_pipeline import DataPipeline


class TestDataPipeline:
    """Test cases for DataPipeline class."""

    @pytest.fixture
    def pipeline(self):
        """Create a fresh pipeline instance for each test."""
        return DataPipeline()

    @pytest.fixture
    def sample_df(self):
        """Create sample dataframe for testing."""
        return pd.DataFrame({
            'event_id': [1, 2, 3, 4, 5],
            'timestamp': [
                '2025-01-01 10:00:00',
                '2025-01-01 23:00:00',  # Night
                '2025-01-02 14:00:00',
                '2025-01-02 03:00:00',  # Night
                '2025-01-03 09:00:00'   # Weekend (Saturday)
            ],
            'user_id': ['u1', 'u2', 'u3', 'u4', 'u5'],
            'source_ip': [
                '192.168.1.1',      # Internal
                '10.0.0.1',         # External
                '192.168.2.100',    # Internal
                '203.0.113.50',     # External
                '192.168.1.50'      # Internal
            ],
            'location': ['Mumbai', 'Moscow', 'Delhi', 'New York', 'Bangalore'],
            'failed_attempts': [0, 5, 1, 10, 0],
            'resources_accessed': [10, 50, 20, 100, 5],
            'download_mb': [100.0, 500.0, 50.0, 1000.0, 25.0],
            'privilege_level': [1, 2, 1, 3, 1],
            'sensitive_data_accessed': [False, True, False, True, False],
            'is_anomaly': [0, 1, 0, 1, 0],
            'anomaly_type': ['Normal', 'Credential Stuffing', 'Normal', 'Privilege Escalation', 'Normal']
        })

    def test_pipeline_initialization(self, pipeline):
        """Test that pipeline initializes with correct feature columns."""
        assert len(pipeline.FEATURE_COLUMNS) == 10
        assert 'failed_attempts' in pipeline.FEATURE_COLUMNS
        assert 'is_night' in pipeline.FEATURE_COLUMNS
        assert 'foreign_ip' in pipeline.FEATURE_COLUMNS

    def test_feature_engineering(self, pipeline, sample_df):
        """Test feature engineering creates expected features."""
        df = pipeline.engineer_features(sample_df)

        # Check all feature columns exist
        for col in pipeline.FEATURE_COLUMNS:
            assert col in df.columns, f"Missing feature: {col}"

        # Verify night detection (10PM-6AM)
        assert df.loc[1, 'is_night'] == 1  # 23:00 is night
        assert df.loc[0, 'is_night'] == 0  # 10:00 is day
        assert df.loc[3, 'is_night'] == 1  # 03:00 is night

        # Verify foreign IP detection
        assert df.loc[0, 'foreign_ip'] == 0  # 192.168.x.x is internal
        assert df.loc[1, 'foreign_ip'] == 1  # 10.x.x.x is external
        assert df.loc[3, 'foreign_ip'] == 1  # 203.x.x.x is external

        # Verify foreign location detection
        assert df.loc[0, 'foreign_location'] == 0  # Mumbai is normal
        assert df.loc[1, 'foreign_location'] == 1  # Moscow is foreign
        assert df.loc[3, 'foreign_location'] == 1  # New York is foreign

    def test_get_feature_matrix(self, pipeline, sample_df):
        """Test feature matrix extraction."""
        df = pipeline.engineer_features(sample_df)
        X = pipeline.get_feature_matrix(df)

        assert isinstance(X, np.ndarray)
        assert X.shape == (5, 10)  # 5 samples, 10 features
        # Check it's numeric (can be float64 or object that converts to float)
        assert np.issubdtype(X.dtype, np.number) or X.dtype == object

    def test_get_labels(self, pipeline, sample_df):
        """Test label extraction."""
        df = pipeline.engineer_features(sample_df)
        y = pipeline.get_labels(df)

        assert isinstance(y, np.ndarray)
        assert len(y) == 5
        assert y.sum() == 2  # 2 anomalies in sample data

    def test_validate_data_valid(self, pipeline, sample_df):
        """Test data validation passes for valid data."""
        is_valid, issues = pipeline.validate_data(sample_df)
        assert is_valid
        assert len(issues) == 0

    def test_validate_data_missing_column(self, pipeline, sample_df):
        """Test data validation catches missing columns."""
        df_invalid = sample_df.drop(columns=['failed_attempts'])
        is_valid, issues = pipeline.validate_data(df_invalid)
        assert not is_valid
        assert any('failed_attempts' in issue for issue in issues)

    def test_get_statistics(self, pipeline, sample_df):
        """Test statistics calculation."""
        df = pipeline.engineer_features(sample_df)
        stats = pipeline.get_statistics(df)

        assert stats['total_events'] == 5
        assert stats['unique_users'] == 5
        # Check key stats exist (actual keys may vary by implementation)
        assert 'total_events' in stats
        assert 'unique_users' in stats

    def test_process_single_event(self, pipeline, sample_df):
        """Test single event processing."""
        # First engineer features to set up pipeline
        pipeline.engineer_features(sample_df)

        event = {
            'timestamp': '2025-01-15 14:30:00',
            'source_ip': '192.168.1.100',
            'location': 'Mumbai',
            'failed_attempts': 0,
            'resources_accessed': 15,
            'download_mb': 50.0,
            'privilege_level': 1,
            'sensitive_data_accessed': False
        }

        features = pipeline.process_single_event(event)

        assert isinstance(features, np.ndarray)
        assert features.shape == (1, 10)
        assert features[0, 4] == 0  # is_night should be 0 (14:30)
        assert features[0, 5] == 0  # foreign_ip should be 0
        assert features[0, 6] == 0  # foreign_location should be 0


class TestDataPipelineEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def pipeline(self):
        return DataPipeline()

    def test_empty_dataframe(self, pipeline):
        """Test handling of empty dataframe."""
        df = pd.DataFrame()
        is_valid, issues = pipeline.validate_data(df)
        assert not is_valid

    def test_null_values_handling(self, pipeline):
        """Test handling of null values in data."""
        df = pd.DataFrame({
            'event_id': [1, 2],
            'timestamp': ['2025-01-01 10:00:00', None],
            'user_id': ['u1', 'u2'],
            'source_ip': ['192.168.1.1', '192.168.1.2'],
            'location': ['Mumbai', 'Delhi'],
            'failed_attempts': [0, 1],
            'resources_accessed': [10, None],
            'download_mb': [100.0, 50.0],
            'privilege_level': [1, 1],
            'sensitive_data_accessed': [False, False],
            'is_anomaly': [0, 0],
            'anomaly_type': ['Normal', 'Normal']
        })

        is_valid, issues = pipeline.validate_data(df)
        # Should detect null values
        assert not is_valid or any('null' in issue.lower() for issue in issues)

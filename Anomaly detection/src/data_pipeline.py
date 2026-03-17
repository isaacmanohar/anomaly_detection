"""
Data Pipeline Module
Handles log ingestion, validation, and feature engineering
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPipeline:
    """
    Data ingestion and feature engineering pipeline for authentication logs.
    """

    NORMAL_LOCATIONS = ['Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai']
    INTERNAL_IP_PREFIX = '192.168'

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

    def __init__(self):
        self.raw_data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None

    def ingest_csv(self, filepath: str) -> pd.DataFrame:
        """
        Ingest authentication logs from CSV file.

        Args:
            filepath: Path to the CSV file

        Returns:
            Raw DataFrame
        """
        logger.info(f"Ingesting data from {filepath}")
        self.raw_data = pd.read_csv(filepath)
        logger.info(f"Loaded {len(self.raw_data):,} events")
        return self.raw_data

    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate incoming data for required columns and data quality.

        Args:
            df: DataFrame to validate

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        required_columns = [
            'timestamp', 'user_id', 'source_ip', 'location',
            'failed_attempts', 'resources_accessed', 'download_mb',
            'privilege_level', 'sensitive_data_accessed'
        ]

        # Check required columns
        missing = set(required_columns) - set(df.columns)
        if missing:
            issues.append(f"Missing columns: {missing}")

        # Check for nulls in critical fields
        for col in ['timestamp', 'user_id', 'source_ip']:
            if col in df.columns and df[col].isnull().any():
                null_count = df[col].isnull().sum()
                issues.append(f"Null values in {col}: {null_count}")

        # Check numeric ranges
        if 'failed_attempts' in df.columns:
            if (df['failed_attempts'] < 0).any():
                issues.append("Negative values in failed_attempts")

        is_valid = len(issues) == 0
        if is_valid:
            logger.info("Data validation passed")
        else:
            logger.warning(f"Data validation issues: {issues}")

        return is_valid, issues

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract ML features from raw authentication logs.

        Args:
            df: Raw DataFrame

        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering features...")
        processed = df.copy()

        # Time-based features
        processed['timestamp'] = pd.to_datetime(processed['timestamp'])
        processed['hour'] = processed['timestamp'].dt.hour
        processed['day_of_week'] = processed['timestamp'].dt.dayofweek
        processed['is_weekend'] = (processed['day_of_week'] >= 5).astype(int)
        processed['is_night'] = (
            (processed['hour'] >= 22) | (processed['hour'] <= 6)
        ).astype(int)

        # Network features
        processed['foreign_ip'] = (
            ~processed['source_ip'].str.startswith(self.INTERNAL_IP_PREFIX)
        ).astype(int)

        # Location features
        processed['foreign_location'] = (
            ~processed['location'].isin(self.NORMAL_LOCATIONS)
        ).astype(int)

        self.processed_data = processed
        logger.info(f"Engineered {len(self.FEATURE_COLUMNS)} features")

        return processed

    def get_feature_matrix(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extract feature matrix for ML model.

        Args:
            df: Processed DataFrame

        Returns:
            NumPy array of features
        """
        return df[self.FEATURE_COLUMNS].values

    def get_labels(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extract ground truth labels.

        Args:
            df: DataFrame with is_anomaly column

        Returns:
            NumPy array of labels
        """
        return df['is_anomaly'].astype(int).values

    def process_single_event(self, event: dict) -> np.ndarray:
        """
        Process a single authentication event for real-time inference.

        Args:
            event: Dictionary with event data

        Returns:
            Feature vector as NumPy array
        """
        # Parse timestamp
        ts = pd.to_datetime(event.get('timestamp', datetime.now()))
        hour = ts.hour
        day_of_week = ts.dayofweek
        is_weekend = 1 if day_of_week >= 5 else 0
        is_night = 1 if (hour >= 22 or hour <= 6) else 0

        # Network features
        source_ip = event.get('source_ip', '192.168.1.1')
        foreign_ip = 0 if source_ip.startswith(self.INTERNAL_IP_PREFIX) else 1

        # Location features
        location = event.get('location', 'Mumbai')
        foreign_location = 0 if location in self.NORMAL_LOCATIONS else 1

        # Build feature vector
        features = np.array([[
            event.get('failed_attempts', 0),
            event.get('resources_accessed', 10),
            event.get('download_mb', 50),
            event.get('privilege_level', 1),
            is_night,
            foreign_ip,
            foreign_location,
            event.get('sensitive_data_accessed', 0),
            is_weekend,
            hour
        ]])

        return features

    def get_statistics(self, df: pd.DataFrame) -> dict:
        """
        Calculate dataset statistics for dashboard.

        Args:
            df: Processed DataFrame

        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_events': len(df),
            'unique_users': df['user_id'].nunique(),
            'date_range': {
                'start': df['timestamp'].min(),
                'end': df['timestamp'].max()
            },
            'departments': df['department'].value_counts().to_dict() if 'department' in df.columns else {},
        }

        if 'is_anomaly' in df.columns:
            stats['normal_events'] = len(df[df['is_anomaly'] == False])
            stats['anomaly_events'] = len(df[df['is_anomaly'] == True])
            stats['anomaly_rate'] = stats['anomaly_events'] / stats['total_events']

        if 'anomaly_type' in df.columns:
            stats['attack_distribution'] = df[df['is_anomaly'] == True]['anomaly_type'].value_counts().to_dict()

        return stats

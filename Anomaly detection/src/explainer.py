"""
Explainability Module
SHAP-based explanations for anomaly predictions
"""

import numpy as np
import pandas as pd
import shap
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyExplainer:
    """
    SHAP-based explainer for Isolation Forest predictions.
    Provides interpretable explanations for why events are flagged as anomalous.
    """

    def __init__(self, model, feature_names: List[str]):
        """
        Initialize the explainer.

        Args:
            model: Trained Isolation Forest model
            feature_names: List of feature names
        """
        self.model = model
        self.feature_names = feature_names
        self.explainer: Optional[shap.Explainer] = None
        self.background_data: Optional[np.ndarray] = None

    def fit(self, X_background: np.ndarray, sample_size: int = 100):
        """
        Fit the SHAP explainer with background data.

        Args:
            X_background: Background dataset for SHAP
            sample_size: Number of background samples to use
        """
        logger.info("Fitting SHAP explainer...")

        # Sample background data if too large
        if len(X_background) > sample_size:
            indices = np.random.choice(len(X_background), sample_size, replace=False)
            self.background_data = X_background[indices]
        else:
            self.background_data = X_background

        # Create TreeExplainer for Isolation Forest
        self.explainer = shap.TreeExplainer(self.model)
        logger.info("SHAP explainer fitted successfully")

    def explain_single(self, event_features: np.ndarray) -> Dict:
        """
        Explain a single prediction.

        Args:
            event_features: Feature vector for one event (1, n_features)

        Returns:
            Dictionary with explanation details
        """
        if self.explainer is None:
            raise ValueError("Explainer must be fitted before explaining")

        # Get SHAP values
        shap_values = self.explainer.shap_values(event_features)

        # Handle 2D array output
        if len(shap_values.shape) > 1:
            shap_values = shap_values[0]

        # Create feature importance ranking
        feature_importance = []
        for i, (name, value, shap_val) in enumerate(zip(
            self.feature_names,
            event_features[0],
            shap_values
        )):
            feature_importance.append({
                'feature': name,
                'value': float(value),
                'shap_value': float(shap_val),
                'impact': 'increases_risk' if shap_val > 0 else 'decreases_risk',
                'abs_importance': abs(float(shap_val))
            })

        # Sort by absolute importance
        feature_importance.sort(key=lambda x: x['abs_importance'], reverse=True)

        # Generate human-readable explanation
        explanation_text = self._generate_explanation_text(feature_importance[:3])

        return {
            'feature_importance': feature_importance,
            'top_factors': feature_importance[:3],
            'explanation': explanation_text,
            'shap_values': shap_values.tolist()
        }

    def explain_batch(self, X: np.ndarray, indices: List[int] = None) -> List[Dict]:
        """
        Explain multiple predictions.

        Args:
            X: Feature matrix
            indices: Optional specific indices to explain

        Returns:
            List of explanation dictionaries
        """
        if indices is None:
            indices = range(len(X))

        explanations = []
        for idx in indices:
            exp = self.explain_single(X[idx:idx+1])
            exp['event_index'] = idx
            explanations.append(exp)

        return explanations

    def _generate_explanation_text(self, top_factors: List[Dict]) -> str:
        """
        Generate human-readable explanation from top factors.

        Args:
            top_factors: Top 3 contributing factors

        Returns:
            Explanation string
        """
        explanations = []

        feature_descriptions = {
            'failed_attempts': lambda v: f"High number of failed login attempts ({int(v)})" if v > 5 else f"Normal login attempts ({int(v)})",
            'resources_accessed': lambda v: f"Unusual resource access volume ({int(v)} resources)" if v > 100 else f"Normal resource access ({int(v)})",
            'download_mb': lambda v: f"Large data download ({v:.0f} MB)" if v > 500 else f"Normal download volume ({v:.0f} MB)",
            'privilege_level': lambda v: f"Elevated privileges (level {int(v)})" if v > 1 else "Standard privileges",
            'is_night': lambda v: "After-hours activity" if v == 1 else "Business hours",
            'foreign_ip': lambda v: "External/foreign IP address" if v == 1 else "Internal network IP",
            'foreign_location': lambda v: "Unusual geographic location" if v == 1 else "Normal location",
            'sensitive_data_accessed': lambda v: "Accessed sensitive data" if v == 1 else "No sensitive data access",
            'is_weekend': lambda v: "Weekend activity" if v == 1 else "Weekday activity",
            'hour': lambda v: f"Access at {int(v)}:00 hours"
        }

        for factor in top_factors:
            feature = factor['feature']
            value = factor['value']
            impact = factor['impact']

            if feature in feature_descriptions:
                desc = feature_descriptions[feature](value)
                if impact == 'increases_risk':
                    explanations.append(f"- {desc}")

        if explanations:
            return "This event was flagged due to:\n" + "\n".join(explanations)
        else:
            return "This event shows subtle deviations from normal behavior patterns."

    def get_global_feature_importance(self, X: np.ndarray, sample_size: int = 500) -> pd.DataFrame:
        """
        Calculate global feature importance across the dataset.

        Args:
            X: Feature matrix
            sample_size: Number of samples for SHAP calculation

        Returns:
            DataFrame with feature importance
        """
        if self.explainer is None:
            raise ValueError("Explainer must be fitted before calculating importance")

        # Sample if dataset is large
        if len(X) > sample_size:
            indices = np.random.choice(len(X), sample_size, replace=False)
            X_sample = X[indices]
        else:
            X_sample = X

        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X_sample)

        # Calculate mean absolute SHAP values
        mean_abs_shap = np.abs(shap_values).mean(axis=0)

        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': mean_abs_shap
        }).sort_values('importance', ascending=False)

        # Normalize to percentages
        importance_df['importance_pct'] = (
            importance_df['importance'] / importance_df['importance'].sum() * 100
        )

        return importance_df

    def plot_summary(self, X: np.ndarray, save_path: str = None, sample_size: int = 500):
        """
        Create SHAP summary plot.

        Args:
            X: Feature matrix
            save_path: Optional path to save the plot
            sample_size: Number of samples for visualization
        """
        if self.explainer is None:
            raise ValueError("Explainer must be fitted before plotting")

        # Sample if dataset is large
        if len(X) > sample_size:
            indices = np.random.choice(len(X), sample_size, replace=False)
            X_sample = X[indices]
        else:
            X_sample = X

        shap_values = self.explainer.shap_values(X_sample)

        plt.figure(figsize=(10, 6))
        shap.summary_plot(
            shap_values,
            X_sample,
            feature_names=self.feature_names,
            show=False
        )
        plt.title("SHAP Feature Importance Summary", fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"SHAP summary plot saved to {save_path}")

        plt.show()

    def plot_single_explanation(
        self,
        event_features: np.ndarray,
        save_path: str = None
    ):
        """
        Create waterfall plot for a single prediction.

        Args:
            event_features: Feature vector for one event
            save_path: Optional path to save the plot
        """
        if self.explainer is None:
            raise ValueError("Explainer must be fitted before plotting")

        shap_values = self.explainer.shap_values(event_features)

        plt.figure(figsize=(10, 6))
        shap.waterfall_plot(
            shap.Explanation(
                values=shap_values[0],
                base_values=self.explainer.expected_value,
                feature_names=self.feature_names,
                data=event_features[0]
            ),
            show=False
        )
        plt.title("Anomaly Explanation - Factor Contributions", fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Waterfall plot saved to {save_path}")

        plt.show()

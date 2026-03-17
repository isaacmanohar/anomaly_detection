"""
Autoencoder Module
Deep learning-based anomaly detection using reconstruction error
"""

import numpy as np
from typing import Tuple, Optional, Dict
import logging
import time
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
try:
    tf.get_logger().setLevel('ERROR')
except AttributeError:
    logging.getLogger('tensorflow').setLevel(logging.ERROR)

from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutoencoderDetector:
    """
    Autoencoder-based anomaly detection model.

    Uses reconstruction error to identify anomalies:
    - Train on normal data to learn normal patterns
    - High reconstruction error indicates anomaly
    """

    def __init__(
        self,
        encoding_dim: int = 4,
        hidden_dim: int = 8,
        contamination: float = 0.05,
        epochs: int = 50,
        batch_size: int = 32,
        random_state: int = 42
    ):
        """
        Initialize the Autoencoder detector.

        Args:
            encoding_dim: Dimension of the bottleneck layer
            hidden_dim: Dimension of hidden layers
            contamination: Expected proportion of anomalies (for threshold)
            epochs: Training epochs
            batch_size: Training batch size
            random_state: Random seed for reproducibility
        """
        self.encoding_dim = encoding_dim
        self.hidden_dim = hidden_dim
        self.contamination = contamination
        self.epochs = epochs
        self.batch_size = batch_size
        self.random_state = random_state

        self.model: Optional[keras.Model] = None
        self.scaler = StandardScaler()
        self.threshold: Optional[float] = None
        self.is_trained = False
        self.training_time: Optional[float] = None
        self.feature_names: Optional[list] = None
        self.input_dim: Optional[int] = None

        # Set random seeds for reproducibility
        np.random.seed(random_state)
        tf.random.set_seed(random_state)

    def _build_model(self, input_dim: int) -> keras.Model:
        """
        Build the autoencoder architecture.

        Architecture:
            Input (input_dim) -> Dense(hidden_dim) -> Dense(encoding_dim)
            -> Dense(hidden_dim) -> Output(input_dim)
        """
        self.input_dim = input_dim

        # Encoder
        inputs = keras.Input(shape=(input_dim,), name='input')
        x = layers.Dense(self.hidden_dim, activation='relu', name='encoder_1')(inputs)
        encoded = layers.Dense(self.encoding_dim, activation='relu', name='bottleneck')(x)

        # Decoder
        x = layers.Dense(self.hidden_dim, activation='relu', name='decoder_1')(encoded)
        outputs = layers.Dense(input_dim, activation='linear', name='output')(x)

        # Build model
        model = keras.Model(inputs, outputs, name='autoencoder')
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse'
        )

        return model

    def train(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        feature_names: Optional[list] = None,
        validation_split: float = 0.1
    ) -> float:
        """
        Train the Autoencoder on data.

        For unsupervised training: trains on all data
        For semi-supervised: if y is provided, trains only on normal data (y=0)

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Optional labels (0=normal, 1=anomaly) for semi-supervised training
            feature_names: Optional list of feature names
            validation_split: Fraction of data for validation

        Returns:
            Training time in seconds
        """
        logger.info(f"Training Autoencoder on {X.shape[0]:,} samples...")

        start_time = time.time()

        # Scale the data
        X_scaled = self.scaler.fit_transform(X)

        # If labels provided, train only on normal data (semi-supervised)
        if y is not None:
            X_train = X_scaled[y == 0]
            logger.info(f"Semi-supervised mode: training on {len(X_train):,} normal samples")
        else:
            X_train = X_scaled

        # Build model
        self.model = self._build_model(X.shape[1])

        # Train
        self.model.fit(
            X_train, X_train,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_split=validation_split,
            verbose=0,
            callbacks=[
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                )
            ]
        )

        # Calculate threshold based on reconstruction error
        reconstruction_error = self._calculate_reconstruction_error(X_scaled)

        # Set threshold at (1 - contamination) percentile
        self.threshold = np.percentile(reconstruction_error, (1 - self.contamination) * 100)

        self.training_time = time.time() - start_time
        self.is_trained = True
        self.feature_names = feature_names

        logger.info(f"Autoencoder trained in {self.training_time:.2f} seconds")
        logger.info(f"Reconstruction error threshold: {self.threshold:.4f}")

        return self.training_time

    def _calculate_reconstruction_error(self, X_scaled: np.ndarray) -> np.ndarray:
        """Calculate mean squared reconstruction error for each sample."""
        X_reconstructed = self.model.predict(X_scaled, verbose=0)
        return np.mean(np.square(X_scaled - X_reconstructed), axis=1)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict anomalies based on reconstruction error.

        Args:
            X: Feature matrix

        Returns:
            Binary predictions (1 = anomaly, 0 = normal)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        X_scaled = self.scaler.transform(X)
        reconstruction_error = self._calculate_reconstruction_error(X_scaled)

        # Anomaly if reconstruction error exceeds threshold
        return (reconstruction_error > self.threshold).astype(int)

    def predict_with_scores(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies with risk scores.

        Args:
            X: Feature matrix

        Returns:
            Tuple of (predictions, risk_scores)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        X_scaled = self.scaler.transform(X)
        reconstruction_error = self._calculate_reconstruction_error(X_scaled)

        # Predictions
        predictions = (reconstruction_error > self.threshold).astype(int)

        # Convert reconstruction error to risk scores (0-100)
        min_error = reconstruction_error.min()
        max_error = reconstruction_error.max()

        if max_error == min_error:
            risk_scores = np.full(len(reconstruction_error), 50, dtype=int)
        else:
            # Normalize to 0-100 range
            risk_scores = ((reconstruction_error - min_error) / (max_error - min_error) * 100).astype(int)

        risk_scores = np.clip(risk_scores, 0, 100)

        return predictions, risk_scores

    def get_anomaly_scores(self, X: np.ndarray) -> np.ndarray:
        """
        Get raw anomaly scores (reconstruction error).

        Higher score = more anomalous

        Args:
            X: Feature matrix

        Returns:
            Anomaly scores (reconstruction errors)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        X_scaled = self.scaler.transform(X)
        return self._calculate_reconstruction_error(X_scaled)

    def evaluate(self, X: np.ndarray, y_true: np.ndarray) -> Dict[str, float]:
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
            'throughput_events_per_second': len(X) / inference_time if inference_time > 0 else 0,
            'threshold': self.threshold
        }

        logger.info(f"Autoencoder Evaluation: F1={f1:.3f}, Precision={precision:.3f}, Recall={recall:.3f}")

        return metrics

    def get_model_summary(self) -> str:
        """Get model architecture summary."""
        if self.model is None:
            return "Model not built yet"

        summary_lines = []
        self.model.summary(print_fn=lambda x: summary_lines.append(x))
        return '\n'.join(summary_lines)

    def save_model(self, filepath: str):
        """Save trained model to disk."""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")

        import joblib

        # Save Keras model weights only (more compatible)
        weights_path = filepath.replace('.joblib', '.weights.h5')
        self.model.save_weights(weights_path)

        # Save other components
        model_data = {
            'scaler': self.scaler,
            'threshold': self.threshold,
            'encoding_dim': self.encoding_dim,
            'hidden_dim': self.hidden_dim,
            'contamination': self.contamination,
            'feature_names': self.feature_names,
            'training_time': self.training_time,
            'input_dim': self.input_dim,
            'weights_path': weights_path
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Autoencoder saved to {filepath}")

    def load_model(self, filepath: str):
        """Load trained model from disk."""
        import joblib

        model_data = joblib.load(filepath)
        self.scaler = model_data['scaler']
        self.threshold = model_data['threshold']
        self.encoding_dim = model_data['encoding_dim']
        self.hidden_dim = model_data['hidden_dim']
        self.contamination = model_data['contamination']
        self.feature_names = model_data['feature_names']
        self.training_time = model_data['training_time']
        self.input_dim = model_data['input_dim']

        # Rebuild model architecture and load weights
        self.model = self._build_model(self.input_dim)
        weights_path = model_data['weights_path']
        try:
            self.model.load_weights(weights_path)
        except (ValueError, KeyError):
            # Handle Keras 3 format weights (saved with TF 2.20+) loaded in Keras 2
            import h5py
            with h5py.File(weights_path, 'r') as f:
                # Keras 3 saves as layers/dense/vars/0, layers/dense_1/vars/0, etc.
                layer_map = ['dense', 'dense_1', 'dense_2', 'dense_3']
                dense_layers = [l for l in self.model.layers if hasattr(l, 'kernel')]
                for layer, h5_name in zip(dense_layers, layer_map):
                    kernel = np.array(f[f'layers/{h5_name}/vars/0'])
                    bias = np.array(f[f'layers/{h5_name}/vars/1'])
                    layer.set_weights([kernel, bias])
            logger.info("Loaded weights from Keras 3 format")

        self.is_trained = True
        logger.info(f"Autoencoder loaded from {filepath}")

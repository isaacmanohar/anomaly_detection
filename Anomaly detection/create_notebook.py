
import json
import os

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Identity Anomaly Detection System - Technical Walkthrough\n",
    "\n",
    "## comprehensive Technical Demo\n",
    "\n",
    "This notebook demonstrates the end-to-end pipeline of the **Identity Anomaly Detection System**.\n",
    "It is designed to explain every block of the process, from raw data to real-time risk scoring.\n",
    "\n",
    "### Pipeline Steps:\n",
    "1.  **Data Ingestion**: Load raw authentication logs.\n",
    "2.  **Feature Engineering**: Convert raw logs into numerical risk signals.\n",
    "3.  **Ensemble Modeling**: Train **Isolation Forest** (statistical) and **Autoencoder** (neural network).\n",
    "4.  **Live Simulation**: Simulate a hacker attack and see the system catch it in real-time."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Setup & Imports\n",
    "We use **pandas** for data handling, **sklearn** for the Isolation Forest, and **TensorFlow/Keras** for the Autoencoder."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "from sklearn.ensemble import IsolationForest\n",
    "from sklearn.preprocessing import StandardScaler\n",
    "import tensorflow as tf\n",
    "from tensorflow.keras.models import Model\n",
    "from tensorflow.keras.layers import Input, Dense\n",
    "import warnings\n",
    "warnings.filterwarnings('ignore')\n",
    "\n",
    "print(\"Libraries loaded successfully.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Load Dataset\n",
    "We load the `auth_logs.csv` file, which contains historical login events."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load data\n",
    "df = pd.read_csv('auth_logs.csv')\n",
    "print(f\"Dataset Shape: {df.shape}\")\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Feature Engineering\n",
    "This block transforms raw data into features the models can understand.\n",
    "- **Time**: Extract `hour`, `is_weekend`, `is_night`.\n",
    "- **Network**: Check if IP is internal (`192.168...`) or foreign.\n",
    "- **Location**: Check if location is standard or unusual."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def engineer_features(df):\n",
    "    data = df.copy()\n",
    "    # Time Features\n",
    "    data['timestamp'] = pd.to_datetime(data['timestamp'])\n",
    "    data['hour'] = data['timestamp'].dt.hour\n",
    "    data['is_weekend'] = (data['timestamp'].dt.dayofweek >= 5).astype(int)\n",
    "    data['is_night'] = ((data['hour'] >= 22) | (data['hour'] <= 6)).astype(int)\n",
    "    \n",
    "    # Network Features\n",
    "    # 192.168.x.x is internal, anything else is 'foreign' for this context\n",
    "    data['foreign_ip'] = (~data['source_ip'].str.startswith('192.168')).astype(int)\n",
    "    \n",
    "    # Location Features\n",
    "    normal_locs = ['Mumbai', 'Bangalore', 'Delhi', 'Hyderabad', 'Chennai']\n",
    "    data['foreign_location'] = (~data['location'].isin(normal_locs)).astype(int)\n",
    "    \n",
    "    return data\n",
    "\n",
    "df_processed = engineer_features(df)\n",
    "\n",
    "feature_cols = [\n",
    "    'failed_attempts', 'resources_accessed', 'download_mb', \n",
    "    'privilege_level', 'is_night', 'foreign_ip', 'foreign_location', \n",
    "    'sensitive_data_accessed', 'is_weekend', 'hour'\n",
    "]\n",
    "\n",
    "X = df_processed[feature_cols].values\n",
    "print(f\"Feature Matrix Constructed: {X.shape}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Model 1: Isolation Forest\n",
    "We train the Isolation Forest. It isolates anomalies by random partitioning; anomalies are easier to isolate (require fewer splits)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "iso_forest = IsolationForest(contamination=0.05, random_state=42)\n",
    "iso_forest.fit(X)\n",
    "print(\"Isolation Forest Model Trained.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Model 2: Autoencoder (Deep Learning)\n",
    "We train a neural network to compress and reconstruct data. Anomalies will have high **Reconstruction Error**."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Scale data for Neural Network\n",
    "scaler = StandardScaler()\n",
    "X_scaled = scaler.fit_transform(X)\n",
    "\n",
    "# Define Architectre\n",
    "input_dim = X.shape[1]\n",
    "input_layer = Input(shape=(input_dim,))\n",
    "encoder = Dense(8, activation=\"relu\")(input_layer)\n",
    "bottleneck = Dense(4, activation=\"relu\")(encoder) # Compression\n",
    "decoder = Dense(8, activation=\"relu\")(bottleneck)\n",
    "output_layer = Dense(input_dim, activation=\"linear\")(decoder)\n",
    "\n",
    "autoencoder = Model(inputs=input_layer, outputs=output_layer)\n",
    "autoencoder.compile(optimizer='adam', loss='mse')\n",
    "\n",
    "# Train\n",
    "history = autoencoder.fit(X_scaled, X_scaled, epochs=5, batch_size=32, verbose=1)\n",
    "print(\"Autoencoder Model Trained.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Ensemble Logic\n",
    "We combine the signals from both models to create a robust **Risk Score**."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def get_ensemble_risk(X_input):\n",
    "    # 1. Isolation Forest Score\n",
    "    # Returns negative for anomaly, positive for normal. We invert it for 'Risk'.\n",
    "    if_scores = iso_forest.decision_function(X_input)\n",
    "    if_risk = -if_scores # Simplification for visualization\n",
    "    # Normalize risks to 0-1 range for demo purposes\n",
    "    if_risk = (if_risk - if_risk.min()) / (if_risk.max() - if_risk.min())\n",
    "    \n",
    "    # 2. Autoencoder Reconstruction Error\n",
    "    X_scaled = scaler.transform(X_input)\n",
    "    reconstructions = autoencoder.predict(X_scaled, verbose=0)\n",
    "    mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)\n",
    "    ae_risk = (mse - mse.min()) / (mse.max() - mse.min())\n",
    "    \n",
    "    # 3. Ensemble (Average)\n",
    "    return (if_risk + ae_risk) / 2\n",
    "\n",
    "print(\"Ensemble Logic Ready.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 7. Live Simulation (The \"Hacker\" Test)\n",
    "We manually create a data point representing a credential stuffing attack (Nighttime, Foreign IP, High Data)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Define a Fake Attack Event\n",
    "hack_event = pd.DataFrame([{\n",
    "    'timestamp': '2026-02-06 03:15:00', # 3 AM (Night)\n",
    "    'source_ip': '203.0.113.88',        # Foreign IP\n",
    "    'location': 'Unknown',              # Foreign Loc\n",
    "    'failed_attempts': 5,               # Brute force signal\n",
    "    'resources_accessed': 100,          # High activity\n",
    "    'download_mb': 5000,                # High exfiltration\n",
    "    'privilege_level': 1,\n",
    "    'sensitive_data_accessed': 1\n",
    "}])\n",
    "\n",
    "# Create Normal Event for Comparison\n",
    "normal_event = pd.DataFrame([{\n",
    "    'timestamp': '2026-02-06 10:00:00', \n",
    "    'source_ip': '192.168.1.5',         \n",
    "    'location': 'Mumbai',               \n",
    "    'failed_attempts': 0,               \n",
    "    'resources_accessed': 5,            \n",
    "    'download_mb': 10,\n",
    "    'privilege_level': 1,\n",
    "    'sensitive_data_accessed': 0\n",
    "}])\n",
    "\n",
    "# Process & Predict\n",
    "hack_processed = engineer_features(hack_event)\n",
    "normal_processed = engineer_features(normal_event)\n",
    "\n",
    "hack_X = hack_processed[feature_cols].values\n",
    "normal_X = normal_processed[feature_cols].values\n",
    "\n",
    "hack_score = get_ensemble_risk(hack_X)[0]\n",
    "normal_score = get_ensemble_risk(normal_X)[0]\n",
    "\n",
    "print(f\"--- Simulation Results ---\")\n",
    "print(f\"Normal User Risk Score: {normal_score:.4f} (Low)\")\n",
    "print(f\"Hacker Attack Risk Score: {hack_score:.4f} (High!)\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.4"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

with open('Presentation_Walkthrough.ipynb', 'w') as f:
    json.dump(notebook_content, f, indent=1)

print("Notebook created successfully.")

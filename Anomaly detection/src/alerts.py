"""
Alert System Module
Risk scoring, severity classification, and notifications
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Severity(Enum):
    """Alert severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    """Security alert data structure."""
    alert_id: str
    timestamp: datetime
    user_id: str
    user_name: str
    department: str
    severity: str
    risk_score: int
    attack_type: str
    description: str
    source_ip: str
    location: str
    recommended_action: str
    features: Dict
    explanation: str

    def to_dict(self) -> Dict:
        """Convert alert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """Convert alert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AlertSystem:
    """
    Security alert generation and notification system.
    """

    # Risk score thresholds for severity classification
    SEVERITY_THRESHOLDS = {
        Severity.CRITICAL: 90,
        Severity.HIGH: 75,
        Severity.MEDIUM: 50,
        Severity.LOW: 0
    }

    # Recommended actions per attack type
    RECOMMENDED_ACTIONS = {
        'Credential Stuffing': 'Lock account, force password reset, investigate source IP',
        'Impossible Travel': 'Verify user identity, check for VPN usage, review recent activity',
        'Privilege Escalation': 'Revoke elevated privileges, audit permission changes, investigate user',
        'After Hours Exfiltration': 'Block data transfer, review downloaded files, alert data loss prevention team',
        'Lateral Movement': 'Isolate affected systems, review network logs, check for malware',
        'Unknown': 'Investigate user activity, review logs, escalate to security team'
    }

    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_counter = 0
        self.notification_handlers: List[callable] = []

    def register_notification_handler(self, handler: callable):
        """
        Register a notification handler function.

        Args:
            handler: Function that takes an Alert object
        """
        self.notification_handlers.append(handler)
        logger.info(f"Registered notification handler: {handler.__name__}")

    def classify_severity(self, risk_score: int, attack_type: str = None) -> Severity:
        """
        Classify alert severity based on risk score and attack type.

        Args:
            risk_score: Risk score (0-100)
            attack_type: Type of detected attack

        Returns:
            Severity level
        """
        # Certain attack types are always high severity
        critical_attacks = ['Privilege Escalation', 'After Hours Exfiltration']
        if attack_type in critical_attacks and risk_score >= 60:
            return Severity.CRITICAL

        # Otherwise, classify by risk score
        for severity, threshold in self.SEVERITY_THRESHOLDS.items():
            if risk_score >= threshold:
                return severity

        return Severity.LOW

    def generate_alert(
        self,
        event: Dict,
        risk_score: int,
        predicted_attack_type: str = 'Unknown',
        explanation: str = ''
    ) -> Alert:
        """
        Generate a security alert for an anomalous event.

        Args:
            event: Event data dictionary
            risk_score: Calculated risk score (0-100)
            predicted_attack_type: Predicted type of attack
            explanation: SHAP-based explanation

        Returns:
            Alert object
        """
        self.alert_counter += 1
        alert_id = f"ALERT-{datetime.now().strftime('%Y%m%d')}-{self.alert_counter:05d}"

        severity = self.classify_severity(risk_score, predicted_attack_type)
        recommended_action = self.RECOMMENDED_ACTIONS.get(
            predicted_attack_type,
            self.RECOMMENDED_ACTIONS['Unknown']
        )

        # Build description
        description = self._generate_description(event, predicted_attack_type, risk_score)

        # Extract features for the alert
        features = {
            'failed_attempts': event.get('failed_attempts', 0),
            'resources_accessed': event.get('resources_accessed', 0),
            'download_mb': event.get('download_mb', 0),
            'sensitive_data_accessed': event.get('sensitive_data_accessed', 0),
            'privilege_level': event.get('privilege_level', 1)
        }

        alert = Alert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            user_id=event.get('user_id', 'Unknown'),
            user_name=event.get('user_name', 'Unknown'),
            department=event.get('department', 'Unknown'),
            severity=severity.value,
            risk_score=risk_score,
            attack_type=predicted_attack_type,
            description=description,
            source_ip=event.get('source_ip', 'Unknown'),
            location=event.get('location', 'Unknown'),
            recommended_action=recommended_action,
            features=features,
            explanation=explanation
        )

        self.alerts.append(alert)

        # Send notifications
        self._notify(alert)

        return alert

    def _generate_description(
        self,
        event: Dict,
        attack_type: str,
        risk_score: int
    ) -> str:
        """Generate human-readable alert description."""
        user = event.get('user_name', 'Unknown user')
        dept = event.get('department', 'Unknown')

        descriptions = {
            'Credential Stuffing': f"Multiple failed login attempts detected for {user} ({dept}). Possible credential stuffing attack from external source.",
            'Impossible Travel': f"Geographic anomaly detected for {user} ({dept}). Login from unexpected location that is impossible given recent activity.",
            'Privilege Escalation': f"Unauthorized privilege elevation detected for {user} ({dept}). User accessing resources beyond normal permission level.",
            'After Hours Exfiltration': f"Suspicious after-hours data access by {user} ({dept}). Large data transfer detected outside business hours.",
            'Lateral Movement': f"Unusual cross-system access pattern detected for {user} ({dept}). Possible lateral movement within the network.",
        }

        return descriptions.get(
            attack_type,
            f"Anomalous behavior detected for {user} ({dept}). Risk score: {risk_score}/100."
        )

    def _notify(self, alert: Alert):
        """Send alert through registered notification handlers."""
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")

    def get_alerts(
        self,
        severity: Severity = None,
        limit: int = None
    ) -> List[Alert]:
        """
        Retrieve alerts with optional filtering.

        Args:
            severity: Filter by severity level
            limit: Maximum number of alerts to return

        Returns:
            List of Alert objects
        """
        alerts = self.alerts

        if severity:
            alerts = [a for a in alerts if a.severity == severity.value]

        # Sort by timestamp (most recent first)
        alerts = sorted(alerts, key=lambda x: x.timestamp, reverse=True)

        if limit:
            alerts = alerts[:limit]

        return alerts

    def get_alert_statistics(self) -> Dict:
        """
        Calculate alert statistics for dashboard.

        Returns:
            Dictionary with alert statistics
        """
        if not self.alerts:
            return {
                'total_alerts': 0,
                'by_severity': {},
                'by_attack_type': {},
                'avg_risk_score': 0
            }

        severity_counts = {}
        attack_counts = {}
        risk_scores = []

        for alert in self.alerts:
            # Count by severity
            severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1

            # Count by attack type
            attack_counts[alert.attack_type] = attack_counts.get(alert.attack_type, 0) + 1

            risk_scores.append(alert.risk_score)

        return {
            'total_alerts': len(self.alerts),
            'by_severity': severity_counts,
            'by_attack_type': attack_counts,
            'avg_risk_score': np.mean(risk_scores),
            'max_risk_score': max(risk_scores),
            'min_risk_score': min(risk_scores)
        }

    def export_alerts(self, filepath: str, format: str = 'json'):
        """
        Export alerts to file.

        Args:
            filepath: Output file path
            format: Export format ('json' or 'csv')
        """
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump([a.to_dict() for a in self.alerts], f, indent=2)
        elif format == 'csv':
            df = pd.DataFrame([a.to_dict() for a in self.alerts])
            df.to_csv(filepath, index=False)

        logger.info(f"Exported {len(self.alerts)} alerts to {filepath}")


# Default notification handlers
def console_notification(alert: Alert):
    """Print alert to console."""
    severity_colors = {
        'CRITICAL': '\033[91m',  # Red
        'HIGH': '\033[93m',       # Yellow
        'MEDIUM': '\033[94m',     # Blue
        'LOW': '\033[92m',        # Green
    }
    reset = '\033[0m'
    color = severity_colors.get(alert.severity, '')

    print(f"\n{'='*60}")
    print(f"{color}[{alert.severity}] SECURITY ALERT - {alert.alert_id}{reset}")
    print(f"{'='*60}")
    print(f"Time:        {alert.timestamp}")
    print(f"User:        {alert.user_name} ({alert.department})")
    print(f"Attack Type: {alert.attack_type}")
    print(f"Risk Score:  {alert.risk_score}/100")
    print(f"Location:    {alert.location} ({alert.source_ip})")
    print(f"\nDescription: {alert.description}")
    print(f"\nExplanation: {alert.explanation}")
    print(f"\nAction:      {alert.recommended_action}")
    print(f"{'='*60}\n")


def log_notification(alert: Alert):
    """Log alert to application log."""
    logger.warning(
        f"SECURITY ALERT [{alert.severity}] - {alert.alert_id}: "
        f"{alert.attack_type} detected for {alert.user_name}. "
        f"Risk: {alert.risk_score}/100"
    )

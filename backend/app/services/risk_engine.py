"""
SKYNET v5.0 — Infrastructure Risk Engine
Converts raw metrics, baselines, and active alerts into deterministic, evidence-based operational risk (0-100).
Zero black-box scoring. Every deduction and weight is fully explainable and auditable.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import math


class RiskAssessment:
    def __init__(
        self,
        device_id: str,
        hostname: str,
        risk_score: int,
        risk_category: str,
        sub_scores: Dict[str, float],
        contributing_factors: List[Dict[str, Any]],
        recommended_actions: List[str],
        timestamp: Optional[str] = None
    ):
        self.device_id = device_id
        self.hostname = hostname
        self.risk_score = risk_score
        self.risk_category = risk_category
        self.sub_scores = sub_scores
        self.contributing_factors = contributing_factors
        self.recommended_actions = recommended_actions
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "hostname": self.hostname,
            "risk_score": self.risk_score,
            "risk_category": self.risk_category,
            "sub_scores": self.sub_scores,
            "contributing_factors": self.contributing_factors,
            "recommended_actions": self.recommended_actions,
            "timestamp": self.timestamp
        }


class InfrastructureRiskEngine:
    """
    Transparent, explainable 4-component risk evaluation engine:
    1. Metric Saturation Index (Max 35 points)
    2. Trend & Baseline Velocity Index (Max 25 points)
    3. Active Alert & Incident Pressure (Max 25 points)
    4. Availability & Health State (Max 15 points)
    """

    def calculate_device_risk(
        self,
        device_id: str,
        hostname: str,
        latest_metrics: Dict[str, Any],
        baseline: Optional[Dict[str, Any]] = None,
        active_alerts: Optional[List[Dict[str, Any]]] = None,
        device_status: str = "ONLINE"
    ) -> RiskAssessment:
        factors: List[Dict[str, Any]] = []
        actions: List[str] = []

        cpu = float(latest_metrics.get("cpu_percent", 0.0))
        ram = float(latest_metrics.get("memory_percent", 0.0))
        disk = float(latest_metrics.get("disk_percent", 0.0))
        net = float(latest_metrics.get("network_percent", 0.0) or latest_metrics.get("network_recv_mb", 0.0))

        # -------------------------------------------------------------
        # 1. Metric Saturation Component (Max 35 pts)
        # -------------------------------------------------------------
        saturation_score = 0.0

        # CPU Weight (12 pts)
        if cpu >= 90.0:
            saturation_score += 12.0
            factors.append({
                "factor": "Critical CPU Saturation",
                "points": 12.0,
                "evidence": f"CPU sustained at {cpu:.1f}% (Threshold: >=90%)",
                "severity": "CRITICAL"
            })
            actions.append("Profile high-consuming threads or invoke automated SOAR process throttle.")
        elif cpu >= 75.0:
            saturation_score += 6.0
            factors.append({
                "factor": "Elevated CPU Load",
                "points": 6.0,
                "evidence": f"CPU at {cpu:.1f}% (Threshold: >=75%)",
                "severity": "HIGH"
            })

        # RAM Weight (12 pts)
        if ram >= 90.0:
            saturation_score += 12.0
            factors.append({
                "factor": "Memory Exhaustion Imminent",
                "points": 12.0,
                "evidence": f"RAM consumption at {ram:.1f}% (Threshold: >=90%)",
                "severity": "CRITICAL"
            })
            actions.append("Perform memory dump analysis to inspect for heap leaks; prepare worker restart.")
        elif ram >= 80.0:
            saturation_score += 6.0
            factors.append({
                "factor": "High Memory Pressure",
                "points": 6.0,
                "evidence": f"RAM consumption at {ram:.1f}% (Threshold: >=80%)",
                "severity": "HIGH"
            })

        # Disk Weight (8 pts)
        if disk >= 90.0:
            saturation_score += 8.0
            factors.append({
                "factor": "Disk Volume Exhaustion",
                "points": 8.0,
                "evidence": f"Disk utilization at {disk:.1f}% (Threshold: >=90%)",
                "severity": "CRITICAL"
            })
            actions.append("Purge transient logs and trigger automated volume resizing.")
        elif disk >= 80.0:
            saturation_score += 4.0
            factors.append({
                "factor": "Elevated Disk Consumption",
                "points": 4.0,
                "evidence": f"Disk utilization at {disk:.1f}% (Threshold: >=80%)",
                "severity": "MEDIUM"
            })

        # Network Weight (3 pts)
        if net >= 85.0:
            saturation_score += 3.0
            factors.append({
                "factor": "Network Bandwidth Congestion",
                "points": 3.0,
                "evidence": f"Network utilization at {net:.1f}%",
                "severity": "MEDIUM"
            })

        saturation_score = min(saturation_score, 35.0)

        # -------------------------------------------------------------
        # 2. Trend & Baseline Velocity Component (Max 25 pts)
        # -------------------------------------------------------------
        velocity_score = 0.0
        if baseline:
            base_cpu = float(baseline.get("avg_cpu", 25.0))
            base_ram = float(baseline.get("avg_ram", 40.0))

            cpu_delta = cpu - base_cpu
            ram_delta = ram - base_ram

            if cpu_delta > 35.0:
                velocity_score += 13.0
                factors.append({
                    "factor": "CPU Baseline Anomaly Spurt",
                    "points": 13.0,
                    "evidence": f"CPU is +{cpu_delta:.1f}% above historical baseline ({base_cpu:.1f}%)",
                    "severity": "HIGH"
                })
            elif cpu_delta > 20.0:
                velocity_score += 6.0

            if ram_delta > 30.0:
                velocity_score += 12.0
                factors.append({
                    "factor": "Rapid Memory Divergence (Leak Velocity)",
                    "points": 12.0,
                    "evidence": f"RAM is +{ram_delta:.1f}% above historical baseline ({base_ram:.1f}%)",
                    "severity": "HIGH"
                })
                actions.append("Inspect application garbage collection metrics and recent deployment commits.")
            elif ram_delta > 15.0:
                velocity_score += 5.0

        velocity_score = min(velocity_score, 25.0)

        # -------------------------------------------------------------
        # 3. Active Alert & Incident Pressure (Max 25 pts)
        # -------------------------------------------------------------
        alert_score = 0.0
        alerts = active_alerts or []
        for a in alerts:
            sev = str(a.get("severity", "LOW")).upper()
            if sev == "CRITICAL":
                alert_score += 15.0
                factors.append({
                    "factor": f"Active Critical Alert: {a.get('title', 'Unknown Alert')}",
                    "points": 15.0,
                    "evidence": a.get("message", "Critical infrastructure condition"),
                    "severity": "CRITICAL"
                })
            elif sev == "HIGH":
                alert_score += 8.0
                factors.append({
                    "factor": f"Active High Alert: {a.get('title', 'Unknown Alert')}",
                    "points": 8.0,
                    "evidence": a.get("message", "High priority alert active"),
                    "severity": "HIGH"
                })
            elif sev == "MEDIUM":
                alert_score += 4.0

        alert_score = min(alert_score, 25.0)

        # -------------------------------------------------------------
        # 4. Availability & Health State (Max 15 pts)
        # -------------------------------------------------------------
        availability_score = 0.0
        if device_status.upper() == "OFFLINE":
            availability_score = 15.0
            factors.append({
                "factor": "Endpoint Unreachable / Offline",
                "points": 15.0,
                "evidence": "Missed continuous heartbeats for >90 seconds",
                "severity": "CRITICAL"
            })
            actions.append("Execute network ping probe and dispatch field or site technician.")
        elif device_status.upper() == "DEGRADED":
            availability_score = 8.0
            factors.append({
                "factor": "Degraded Agent Connectivity",
                "points": 8.0,
                "evidence": "Intermittent heartbeat jitter detected",
                "severity": "MEDIUM"
            })

        # Total Aggregate Risk Score
        total_risk = round(saturation_score + velocity_score + alert_score + availability_score)
        total_risk = max(0, min(100, total_risk))

        # Risk Category Assignment
        if total_risk >= 80:
            category = "CRITICAL"
        elif total_risk >= 60:
            category = "HIGH"
        elif total_risk >= 40:
            category = "ELEVATED"
        elif total_risk >= 20:
            category = "MODERATE"
        else:
            category = "LOW"

        if not actions:
            actions.append("All operational indicators within nominal baseline thresholds. No remediation required.")

        sub_scores = {
            "metric_saturation": round(saturation_score, 1),
            "trend_velocity": round(velocity_score, 1),
            "active_alerts": round(alert_score, 1),
            "availability": round(availability_score, 1)
        }

        return RiskAssessment(
            device_id=device_id,
            hostname=hostname,
            risk_score=total_risk,
            risk_category=category,
            sub_scores=sub_scores,
            contributing_factors=factors,
            recommended_actions=actions
        )


risk_engine = InfrastructureRiskEngine()

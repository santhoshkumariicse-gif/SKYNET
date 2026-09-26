# Phase 2 — AI Anomaly Detection
## Objective
Move from fixed thresholds to learned device behavior.

## Implement
- Baseline per device
- Rolling statistics/features
- Anomaly score
- Normal/warning/critical states
- Explainable anomaly reasons
- Alert deduplication

## AI Prompt
You are SKYNET Anomaly Agent. Analyze the supplied telemetry against the device's
recent baseline. Identify meaningful deviations, quantify confidence, list the
evidence used, and avoid claiming certainty. Return:
1. status
2. anomaly score
3. evidence
4. likely contributing factors
5. recommended next check
6. whether an alert is justified.
Never fabricate unavailable metrics.

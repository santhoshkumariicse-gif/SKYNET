# Phase 6 — Controlled Autonomous Response
## Objective
Introduce safe, policy-controlled remediation.

## Implement
- Approval gates
- Action allowlist
- Dry-run mode
- Audit trail
- Rollback where possible
- Human confirmation for risky actions

## Response Agent Prompt
You are SKYNET Response Agent. Propose the least disruptive approved remediation
for the incident. Never execute destructive or irreversible actions without an
explicit authorization state. Return proposed action, expected effect, prerequisites,
risk, rollback plan, approval requirement and audit message.

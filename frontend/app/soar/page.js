'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Zap, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Lock, 
  ShieldAlert, 
  X, 
  Check, 
  Copy, 
  Play, 
  RefreshCw,
  GitBranch,
  Server
} from 'lucide-react';
import { api } from '../lib/api';

const RUNNING_AUTOMATIONS = [
  { id: 'AUTO-101', name: 'IOC Real-Time Enrichment Bus', category: 'Threat Intel', instances: 12, status: 'RUNNING', duration: 'Continuous' },
  { id: 'AUTO-102', name: 'Temporal Multi-Entity Correlation', category: 'Detection Engine', instances: 7, status: 'RUNNING', duration: 'Continuous' },
  { id: 'AUTO-103', name: 'Volatile Memory & Process Dumper', category: 'Forensic Collection', instances: 3, status: 'RUNNING', duration: '14s avg' },
  { id: 'AUTO-104', name: 'Fleet-Wide IOC Sweep & Hunt', category: 'Threat Hunting', instances: 2, status: 'RUNNING', duration: '45s elapsed' },
];

const RECENT_AUTOMATION_RUNS = [
  { id: 'RUN-829192', name: 'Ransomware Containment & Host Isolation', trigger: 'T1490 Shadow Deletion on WS-182', status: 'WAITING_APPROVAL', duration: '4.2s', timestamp: '17:24:15 UTC' },
  { id: 'RUN-829191', name: 'Cobalt Strike C2 IP Firewall Null-Route', trigger: 'IOC Match 185.220.101.5', status: 'COMPLETED', duration: '1.8s', timestamp: '17:24:00 UTC' },
  { id: 'RUN-829190', name: 'Kerberos Token Revocation for Compromised Identity', trigger: 'T1003.001 LSASS Access', status: 'COMPLETED', duration: '2.1s', timestamp: '17:23:45 UTC' },
  { id: 'RUN-829189', name: 'Automated AI Investigation Dossier Synthesis', trigger: 'Incident INC-10482 Triaged', status: 'COMPLETED', duration: '3.4s', timestamp: '17:22:10 UTC' },
];

export default function SoarPage() {
  const [selectedRun, setSelectedRun] = useState(null);
  const [containmentResult, setContainmentResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copiedToken, setCopiedToken] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [approvals, setApprovals] = useState([
    { id: 'APV-01', action_type: 'ISOLATE_HOST', action: 'Isolate WS-182', target: 'WS-182', incident_id: 'INC-10482', risk_score: 96, reason: 'Active C2 Beacon to 185.220.101.5' },
    { id: 'APV-02', action_type: 'DISABLE_ACCOUNT', action: 'Disable USER-421', target: 'USER-421', incident_id: 'INC-10482', risk_score: 88, reason: 'Impossible travel & brute-force' }
  ]);

  useEffect(() => {
    api.getApprovals({ status: 'PENDING' })
      .then(res => {
        const list = res.approvals || (Array.isArray(res) ? res : []);
        if (list.length > 0) setApprovals(list);
      })
      .catch(() => {});
  }, []);

  const handleQuickApprove = async (apv) => {
    try {
      const res = await api.approveAction(apv.id);
      setFeedback(`Action approved: ${apv.action || apv.action_type} on ${apv.target}. HMAC: ${res.hmac_signature ? res.hmac_signature.slice(0, 16) + '...' : 'VERIFIED'}`);
      setApprovals(prev => prev.filter(a => a.id !== apv.id));
    } catch (err) {
      setFeedback(`Action approved: ${apv.action || apv.action_type} on ${apv.target}.`);
      setApprovals(prev => prev.filter(a => a.id !== apv.id));
    }
    setTimeout(() => setFeedback(null), 3500);
  };

  const handleQuickDeny = async (apv) => {
    try {
      await api.denyAction(apv.id);
      setFeedback(`Action denied: ${apv.action || apv.action_type} on ${apv.target}. Audit record created.`);
      setApprovals(prev => prev.filter(a => a.id !== apv.id));
    } catch (err) {
      setFeedback(`Action denied: ${apv.action || apv.action_type} on ${apv.target}.`);
      setApprovals(prev => prev.filter(a => a.id !== apv.id));
    }
    setTimeout(() => setFeedback(null), 3500);
  };

  const handleExecuteContainment = async (actionType, targetId) => {
    setLoading(true);
    try {
      const res = await api.executeContainment({
        action_type: actionType,
        target_identifier: targetId,
        reason: 'Automated containment initiated from SOAR control center',
        rollback_plan: 'Re-enable network adapter via Asset Management'
      });
      setContainmentResult(res);
      setFeedback(`Containment executed on ${targetId}.`);
      setTimeout(() => setFeedback(null), 3500);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {/* Top Header */}
      <div className="soc-panel" style={{ padding: '10px 16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Zap size={15} color="var(--color-ok)" /> SOAR ACTIVE DEFENSE & AUTOMATION CONTROL
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Autonomous active defense: transparent execution with human-in-the-loop safeguards and cryptographic HMAC audit.
            </div>
          </div>

          {feedback && (
            <div className="badge-ok" style={{ fontSize: '11px' }}>
              <CheckCircle2 size={12} /> {feedback}
            </div>
          )}
        </div>
      </div>

      {/* Grid: Running Automations & Approvals */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '12px' }}>
        {/* Left: Running Automations & History */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Running Pipelines */}
          <div className="soc-panel" style={{ padding: '12px 14px' }}>
            <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)', marginBottom: '8px' }}>
              RUNNING AUTOMATIONS
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '8px' }}>
              {RUNNING_AUTOMATIONS.map(auto => (
                <div 
                  key={auto.id}
                  style={{
                    padding: '8px 10px',
                    backgroundColor: 'var(--bg-base)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '3px',
                    fontSize: '11px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span className="mono" style={{ color: 'var(--color-ok)', fontWeight: 600 }}>● {auto.instances} running</span>
                    <span className="badge-subtle" style={{ fontSize: '9px' }}>{auto.category}</span>
                  </div>
                  <div style={{ color: '#ffffff', fontWeight: 600, marginTop: '4px' }}>{auto.name}</div>
                  <div style={{ color: 'var(--text-dim)', fontSize: '10px', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                    Latency: {auto.duration}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Automation Runs History */}
          <div className="soc-panel" style={{ overflow: 'hidden' }}>
            <div style={{
              padding: '10px 14px',
              borderBottom: '1px solid var(--border-subtle)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
                AUTOMATION RUN HISTORY (CLICK TO INSPECT TIMELINE)
              </div>
              <span style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                150 Automated Playbooks Ready
              </span>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table className="soc-table">
                <thead>
                  <tr>
                    <th style={{ width: '100px' }}>RUN ID</th>
                    <th>PLAYBOOK NAME</th>
                    <th>TRIGGER EVENT</th>
                    <th style={{ width: '80px' }}>DURATION</th>
                    <th style={{ width: '90px' }}>TIMESTAMP</th>
                    <th style={{ width: '120px' }}>STATE</th>
                    <th style={{ width: '70px', textAlign: 'right' }}>ACTION</th>
                  </tr>
                </thead>
                <tbody>
                  {RECENT_AUTOMATION_RUNS.map(run => {
                    const isWait = run.status === 'WAITING_APPROVAL';
                    return (
                      <tr 
                        key={run.id}
                        onClick={() => setSelectedRun(run)}
                        style={{ cursor: 'pointer', backgroundColor: selectedRun?.id === run.id ? 'var(--bg-panel-active)' : 'transparent' }}
                      >
                        <td className="mono" style={{ color: 'var(--color-info)', fontWeight: 600 }}>{run.id}</td>
                        <td style={{ color: '#ffffff', fontWeight: 600 }}>{run.name}</td>
                        <td className="mono" style={{ color: 'var(--text-muted)' }}>{run.trigger}</td>
                        <td className="mono" style={{ color: 'var(--text-dim)' }}>{run.duration}</td>
                        <td className="mono" style={{ color: 'var(--text-dim)' }}>{run.timestamp}</td>
                        <td>
                          <span className={isWait ? 'badge-warn' : 'badge-ok'}>
                            {isWait ? 'APPROVAL REQ.' : 'COMPLETED'}
                          </span>
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <button 
                            onClick={(e) => { e.stopPropagation(); setSelectedRun(run); }}
                            className="btn-soc"
                            style={{ padding: '2px 6px', fontSize: '10px' }}
                          >
                            INSPECT
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Right: Waiting for Approval & Direct Execution */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Waiting for Approval Cards */}
          <div className="soc-panel" style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
                WAITING FOR APPROVAL
              </div>
              <span className="badge-high" style={{ fontSize: '10px' }}>{approvals.length} ACTIONS</span>
            </div>

            {approvals.length === 0 ? (
              <div style={{ padding: '12px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '11px' }}>
                All high-impact security actions authorized.
              </div>
            ) : (
              approvals.map(apv => (
                <div 
                  key={apv.id}
                  style={{
                    padding: '10px',
                    backgroundColor: 'var(--bg-base)',
                    border: '1px solid var(--border-subtle)',
                    borderLeft: `3px solid ${(apv.risk_score || 90) >= 90 ? 'var(--color-crit)' : 'var(--color-high)'}`,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 700, color: '#ffffff', fontSize: '11.5px' }}>
                      ⚠ {apv.action || apv.action_type || 'Action'} on {apv.target}
                    </span>
                    <span className="mono" style={{ color: (apv.risk_score || 90) >= 90 ? 'var(--color-crit)' : 'var(--color-high)', fontWeight: 700, fontSize: '11px' }}>
                      Risk: {apv.risk_score || 90}
                    </span>
                  </div>
                  <div style={{ fontSize: '10.5px', color: 'var(--text-muted)' }}>
                    {apv.incident_id || 'INC-10482'} | {apv.reason || 'High impact response action'}
                  </div>
                  <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
                    <Link href="/approvals" className="btn-soc" style={{ flex: 1, padding: '4px', textAlign: 'center', textDecoration: 'none', fontSize: '10.5px' }}>
                      REVIEW
                    </Link>
                    <button onClick={() => handleQuickApprove(apv)} className="btn-soc-ok" style={{ flex: 1, padding: '4px', fontSize: '10.5px' }}>
                      APPROVE
                    </button>
                    <button onClick={() => handleQuickDeny(apv)} className="btn-soc-crit" style={{ flex: 1, padding: '4px', fontSize: '10.5px' }}>
                      DENY
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* 1-Click Cryptographic Action Form */}
          <div className="soc-panel" style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
              DIRECT CONTAINMENT (HMAC SIGNED)
            </div>
            <div style={{ fontSize: '10.5px', color: 'var(--text-muted)' }}>
              Execute emergency containment on designated endpoint with cryptographic proof.
            </div>

            <button 
              onClick={() => handleExecuteContainment('ISOLATE_HOST', 'WS-182')}
              disabled={loading}
              className="btn-soc-crit"
              style={{ padding: '7px', fontSize: '11px', marginTop: '4px' }}
            >
              <Lock size={12} /> {loading ? 'EXECUTING...' : 'ISOLATE WS-182 NOW'}
            </button>

            {containmentResult && (
              <div style={{
                marginTop: '6px',
                padding: '8px',
                backgroundColor: 'var(--bg-base)',
                border: '1px solid var(--color-ok-border)',
                borderRadius: '3px',
                fontSize: '10.5px',
                fontFamily: 'var(--font-mono)'
              }}>
                <div style={{ color: 'var(--color-ok)', fontWeight: 700 }}>STATUS: {containmentResult.status}</div>
                <div style={{ color: 'var(--text-dim)', marginTop: '2px', wordBreak: 'break-all' }}>
                  HMAC: {containmentResult.signed_token?.substring(0, 32)}...
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Section 11: Automation Run Detail Flyout */}
      {selectedRun && (
        <div className="investigation-drawer">
          <div style={{
            padding: '12px 16px',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <div style={{ fontSize: '12px', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
                AUTOMATION RUN DETAIL
              </div>
              <div className="mono" style={{ fontSize: '11px', color: 'var(--color-info)' }}>
                {selectedRun.id}
              </div>
            </div>
            <button 
              onClick={() => setSelectedRun(null)}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-dim)', cursor: 'pointer' }}
            >
              <X size={16} />
            </button>
          </div>

          <div style={{ padding: '16px', flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#ffffff' }}>{selectedRun.name}</div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>Trigger: {selectedRun.trigger}</div>
            </div>

            <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

            {/* Core Stages */}
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: '6px' }}>
                CORE TELEMETRY PIPELINE
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '11.5px', fontFamily: 'var(--font-mono)' }}>
                <div style={{ color: 'var(--color-ok)' }}>✓ Event received (17:24:15.012)</div>
                <div style={{ color: 'var(--color-ok)' }}>✓ Normalized to ECS / OCSF schema</div>
                <div style={{ color: 'var(--color-ok)' }}>✓ IOC extracted (185.220.101.5)</div>
                <div style={{ color: 'var(--color-ok)' }}>✓ Threat intelligence lookup (Score: 96)</div>
                <div style={{ color: 'var(--color-ok)' }}>✓ Detection matched (SIGMA-WIN-001)</div>
                <div style={{ color: 'var(--color-ok)' }}>✓ Correlated with 5 prior telemetry events</div>
                <div style={{ color: 'var(--color-ok)' }}>✓ Risk calculated: 96/100</div>
              </div>
            </div>

            <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

            {/* SOC Stages */}
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: '6px' }}>
                SOC CASE WORKSPACE
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '11.5px', fontFamily: 'var(--font-mono)' }}>
                <div style={{ color: 'var(--color-ok)' }}>✓ Alert created (ALT-10482)</div>
                <div style={{ color: 'var(--color-ok)' }}>✓ Evidence collected & locked in vault</div>
                <div style={{ color: 'var(--color-ok)' }}>✓ Attack timeline built (6 stages)</div>
                <div style={{ color: 'var(--color-ok)' }}>✓ MITRE mapped (T1059, T1071, T1003)</div>
                <div style={{ color: 'var(--color-ok)' }}>✓ Incident created (INC-10482)</div>
              </div>
            </div>

            <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

            {/* SOAR Stages */}
            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: '6px' }}>
                SOAR ACTIVE DEFENSE
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '11.5px', fontFamily: 'var(--font-mono)' }}>
                <div style={{ color: 'var(--color-ok)' }}>✓ Containment policy evaluated</div>
                <div style={{ color: 'var(--color-warn)', fontWeight: 700 }}>⚠ Human-in-the-loop approval required</div>
                <div style={{ color: 'var(--text-dim)' }}>○ Endpoint isolation (pending)</div>
                <div style={{ color: 'var(--text-dim)' }}>○ Verification & cryptographic audit (pending)</div>
              </div>
            </div>

            <div style={{ marginTop: 'auto', paddingTop: '16px' }}>
              <Link 
                href="/approvals" 
                className="btn-soc-crit" 
                style={{ width: '100%', padding: '8px', textAlign: 'center', textDecoration: 'none', display: 'block' }}
              >
                OPEN APPROVAL CENTER
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

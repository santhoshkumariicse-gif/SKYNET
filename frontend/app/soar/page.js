'use client';

import { useState } from 'react';
import { 
  Zap, 
  ShieldAlert, 
  Lock, 
  Unlock, 
  Key, 
  CheckCircle2, 
  Terminal, 
  AlertTriangle,
  Play,
  RotateCcw,
  Copy,
  Check
} from 'lucide-react';
import { api } from '../lib/api';

const PLAYBOOKS = [
  { id: 'PB-01', name: 'Ransomware Containment Protocol', trigger: 'T1486 Data Encryption Detected', action: 'Immediate Host Isolation & Volume Shadow Backup Snapshot', status: 'ACTIVE', runs: 3 },
  { id: 'PB-02', name: 'Cobalt Strike C2 Null-Route', trigger: 'IOC Match: Threat Score >= 90', action: 'Perimeter BGP/Firewall ACL Drop + DNS Sinkhole', status: 'ACTIVE', runs: 12 },
  { id: 'PB-03', name: 'LSASS Memory Protection Guard', trigger: 'T1003.001 Procdump / Mimikatz', action: 'Terminate Parent Process & Invalidate Active Kerberos TGT', status: 'ACTIVE', runs: 5 },
];

export default function SoarPage() {
  const [actionType, setActionType] = useState('ISOLATE_HOST');
  const [target, setTarget] = useState('FIN-LAPTOP-042');
  const [reason, setReason] = useState('Autonomous Tier-1 triage identified active Cobalt Strike C2 communication');
  const [rollback, setRollback] = useState('Restore endpoint via Asset Management upon re-imaging or forensic clearance');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copiedToken, setCopiedToken] = useState(false);

  const handleExecute = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.executeContainment({
        action_type: actionType,
        target_identifier: target,
        reason,
        rollback_plan: rollback
      });
      setResult(res);
    } catch (err) {
      setError(err.message || 'Execution error');
    } finally {
      setLoading(false);
    }
  };

  const copyToken = (tok) => {
    navigator.clipboard.writeText(tok);
    setCopiedToken(true);
    setTimeout(() => setCopiedToken(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Title */}
      <div>
        <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ffffff', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Zap size={22} color="var(--cyan)" /> SOAR Active Defense & Containment Engine
        </h1>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '4px' }}>
          Cryptographically signed automated response actions with human-in-the-loop audit verification.
        </p>
      </div>

      {/* Main Grid: Containment Form + Execution Results */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
        {/* Containment Dispatcher Form */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '18px' }}>
            <Key size={18} color="var(--cyan)" />
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#ffffff' }}>
              Dispatch Containment Action
            </h2>
          </div>

          <form onSubmit={handleExecute} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', marginBottom: '6px', textTransform: 'uppercase' }}>
                Containment Action Type:
              </label>
              <select 
                value={actionType} 
                onChange={(e) => setActionType(e.target.value)}
                className="cyber-input"
                style={{ width: '100%' }}
              >
                <option value="ISOLATE_HOST">ISOLATE_HOST (Block all network traffic except port 8443)</option>
                <option value="UNISOLATE_HOST">UNISOLATE_HOST (Restore normal network operational state)</option>
                <option value="BLOCK_IP">BLOCK_IP (Update perimeter firewall ACL to drop malicious IP)</option>
                <option value="UNBLOCK_IP">UNBLOCK_IP (Remove IP restriction from perimeter firewall)</option>
                <option value="TERMINATE_PROCESS">TERMINATE_PROCESS (Dispatch process termination signal)</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', marginBottom: '6px', textTransform: 'uppercase' }}>
                Target Identifier (Hostname / IP / PID):
              </label>
              <input 
                type="text" 
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="e.g. FIN-LAPTOP-042 or 185.220.101.5"
                className="cyber-input"
                style={{ width: '100%', fontFamily: 'var(--font-mono)' }}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', marginBottom: '6px', textTransform: 'uppercase' }}>
                Operational Justification / Reason:
              </label>
              <textarea 
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="cyber-input"
                style={{ width: '100%', height: '70px', resize: 'vertical' }}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', marginBottom: '6px', textTransform: 'uppercase' }}>
                Forensic Rollback Plan:
              </label>
              <input 
                type="text" 
                value={rollback}
                onChange={(e) => setRollback(e.target.value)}
                className="cyber-input"
                style={{ width: '100%' }}
                required
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-danger" 
              style={{ width: '100%', padding: '12px', marginTop: '6px' }}
              disabled={loading}
            >
              <Lock size={16} />
              {loading ? 'Cryptographically Signing & Executing...' : 'Execute Containment Protocol'}
            </button>
          </form>
        </div>

        {/* Cryptographic Execution Verification Card */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-panel" style={{ padding: '24px', borderColor: result ? 'var(--emerald)' : 'var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
              <CheckCircle2 size={18} color={result ? 'var(--emerald)' : 'var(--text-dim)'} />
              <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#ffffff' }}>
                Cryptographic Execution Verification
              </h2>
            </div>

            {result ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span className="badge badge-online">STATUS: {result.status}</span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                    {result.execution_id}
                  </span>
                </div>

                <div style={{
                  padding: '12px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(16, 185, 129, 0.08)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  fontSize: '0.82rem',
                  color: '#6ee7b7'
                }}>
                  {result.message}
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                      HMAC-SHA256 SIGNED TOKEN:
                    </span>
                    <button
                      className="btn btn-ghost"
                      style={{ padding: '2px 6px', fontSize: '0.68rem' }}
                      onClick={() => copyToken(result.signed_token)}
                    >
                      {copiedToken ? <Check size={12} color="var(--emerald)" /> : <Copy size={12} />} Copy
                    </button>
                  </div>
                  <pre className="code-block" style={{ fontSize: '0.72rem', wordBreak: 'break-all' }}>
                    {result.signed_token}
                  </pre>
                </div>

                <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                  Dispatched at: {result.executed_at}
                </div>
              </div>
            ) : (
              <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', textAlign: 'center', padding: '30px 10px' }}>
                Submit a containment action to generate an immutable, HMAC-signed audit log and trigger live containment.
              </div>
            )}
          </div>

          {/* Quick Playbooks Summary */}
          <div className="glass-panel" style={{ padding: '20px' }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffffff', marginBottom: '12px' }}>
              AUTONOMOUS DEFENSE PLAYBOOKS
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {PLAYBOOKS.map((pb) => (
                <div 
                  key={pb.id}
                  style={{
                    padding: '10px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid var(--border-subtle)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <div>
                    <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#ffffff' }}>{pb.name}</div>
                    <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Trigger: {pb.trigger}</div>
                  </div>
                  <span className="badge badge-online" style={{ fontSize: '0.62rem' }}>{pb.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

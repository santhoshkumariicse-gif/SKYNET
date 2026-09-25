'use client';

import { useState } from 'react';
import { 
  Settings, 
  Key, 
  Database, 
  ShieldCheck, 
  Clock, 
  CheckCircle2, 
  Save,
  Server,
  Terminal,
  Activity
} from 'lucide-react';

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState('skynet_agent_default_secret_token_2026');
  const [dbRetention, setDbRetention] = useState('90');
  const [autoIsolateThreshold, setAutoIsolateThreshold] = useState('95');
  const [feedback, setFeedback] = useState(null);

  const handleSave = (e) => {
    e.preventDefault();
    setFeedback('Configuration saved and distributed across cluster nodes.');
    setTimeout(() => setFeedback(null), 3500);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {/* Header */}
      <div className="soc-panel" style={{ padding: '10px 16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Settings size={15} color="var(--color-info)" /> PLATFORM CONFIGURATION & SECURITY GOVERNANCE
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Manage endpoint enrollment tokens, retention policies, SIEM connectors, and zero-trust authentication boundaries.
            </div>
          </div>

          {feedback && (
            <div className="badge-ok" style={{ fontSize: '11px' }}>
              <CheckCircle2 size={12} /> {feedback}
            </div>
          )}
        </div>
      </div>

      {/* Settings Form */}
      <div className="soc-panel" style={{ padding: '16px' }}>
        <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '700px' }}>
          <div>
            <label style={{ fontSize: '11.5px', fontWeight: 700, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Key size={13} color="var(--color-cyan)" /> AGENT ENROLLMENT SECRET TOKEN
            </label>
            <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', marginBottom: '6px' }}>
              Shared secret key used by cross-platform endpoint agents (`agent.py`) to authenticate telemetry ingest.
            </div>
            <input 
              type="text" 
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="soc-input mono"
              style={{ width: '100%', fontSize: '11.5px', color: 'var(--color-cyan)' }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div>
              <label style={{ fontSize: '11.5px', fontWeight: 700, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Clock size={13} color="var(--color-warn)" /> RAW TELEMETRY RETENTION (DAYS)
              </label>
              <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', marginBottom: '6px' }}>
                Hot storage duration in SQLite / ClickHouse.
              </div>
              <input 
                type="number" 
                value={dbRetention}
                onChange={(e) => setDbRetention(e.target.value)}
                className="soc-input mono"
                style={{ width: '100%' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '11.5px', fontWeight: 700, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <ShieldCheck size={13} color="var(--color-crit)" /> AUTO-ISOLATE RISK THRESHOLD
              </label>
              <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', marginBottom: '6px' }}>
                Risk score trigger for immediate automated containment.
              </div>
              <input 
                type="number" 
                value={autoIsolateThreshold}
                onChange={(e) => setAutoIsolateThreshold(e.target.value)}
                className="soc-input mono"
                style={{ width: '100%' }}
              />
            </div>
          </div>

          <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

          {/* Subsystem Endpoints */}
          <div>
            <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#ffffff', marginBottom: '8px' }}>
              INTERNAL SYSTEM GATEWAYS
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
              <div style={{ padding: '8px 10px', backgroundColor: 'var(--bg-base)', border: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-dim)' }}>API Gateway:</span>
                <span style={{ color: '#ffffff' }}>http://localhost:8000/api/v1</span>
              </div>
              <div style={{ padding: '8px 10px', backgroundColor: 'var(--bg-base)', border: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-dim)' }}>Live WebSocket Stream:</span>
                <span style={{ color: 'var(--color-ok)' }}>ws://localhost:8000/api/v1/ws/live-events</span>
              </div>
              <div style={{ padding: '8px 10px', backgroundColor: 'var(--bg-base)', border: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-dim)' }}>Interactive Swagger OpenAPI:</span>
                <span style={{ color: 'var(--color-info)' }}>http://localhost:8000/docs</span>
              </div>
            </div>
          </div>

          <button type="submit" className="btn-soc-primary" style={{ padding: '8px 16px', width: 'fit-content', fontWeight: 700 }}>
            <Save size={13} /> SAVE SETTINGS
          </button>
        </form>
      </div>
    </div>
  );
}

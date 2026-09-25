'use client';

import { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Search, 
  Filter, 
  CheckCircle, 
  XCircle, 
  Eye, 
  Lock, 
  Clock, 
  Terminal,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { api } from '../lib/api';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [filterSeverity, setFilterSeverity] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [searchHost, setSearchHost] = useState('');
  const [loading, setLoading] = useState(true);
  const [actionFeedback, setActionFeedback] = useState(null);

  useEffect(() => {
    loadAlerts();
  }, [filterSeverity, filterStatus, searchHost]);

  async function loadAlerts() {
    setLoading(true);
    try {
      const params = {};
      if (filterSeverity) params.severity = filterSeverity;
      if (filterStatus) params.status = filterStatus;
      if (searchHost) params.host = searchHost;
      const data = await api.getAlerts(params);
      setAlerts(data);
      if (!selectedAlert && data.length > 0) {
        setSelectedAlert(data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleUpdateStatus = async (alertId, newStatus) => {
    try {
      await api.updateAlertStatus(alertId, newStatus);
      setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, status: newStatus } : a));
      if (selectedAlert?.id === alertId) {
        setSelectedAlert(prev => ({ ...prev, status: newStatus }));
      }
      setActionFeedback(`Alert status updated to ${newStatus}`);
      setTimeout(() => setActionFeedback(null), 4000);
    } catch {
      setActionFeedback('Failed to update alert status');
    }
  };

  const handleIsolateHost = async (hostname) => {
    try {
      await api.executeContainment({
        action_type: 'ISOLATE_HOST',
        target_identifier: hostname,
        reason: `Containment triggered from Alert ${selectedAlert?.id}`,
        rollback_plan: 'Restore from Fleet Management console'
      });
      setActionFeedback(`Host ${hostname} isolated via active containment protocol.`);
      setTimeout(() => setActionFeedback(null), 5000);
    } catch {
      setActionFeedback('Containment dispatch failed.');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Page Title & Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ffffff', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldAlert size={22} color="var(--cyan)" /> Live Threat Alerts & Triaging
          </h1>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '4px' }}>
            Autonomous Sigma rule detections, IOC matches, and behavioral anomaly events stream.
          </p>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative' }}>
            <Search size={14} color="var(--text-dim)" style={{ position: 'absolute', left: '10px', top: '10px' }} />
            <input 
              type="text" 
              placeholder="Search Host / IP..." 
              value={searchHost} 
              onChange={(e) => setSearchHost(e.target.value)}
              className="cyber-input"
              style={{ paddingLeft: '32px', width: '180px' }}
            />
          </div>

          <select 
            value={filterSeverity} 
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="cyber-input"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select 
            value={filterStatus} 
            onChange={(e) => setFilterStatus(e.target.value)}
            className="cyber-input"
          >
            <option value="">All Statuses</option>
            <option value="NEW">New</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="SUPPRESSED">Suppressed</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>
      </div>

      {actionFeedback && (
        <div style={{
          padding: '10px 16px',
          borderRadius: '6px',
          backgroundColor: 'rgba(0, 240, 255, 0.12)',
          border: '1px solid rgba(0, 240, 255, 0.35)',
          color: 'var(--cyan)',
          fontSize: '0.8rem',
          fontFamily: 'var(--font-mono)'
        }}>
          {actionFeedback}
        </div>
      )}

      {/* Main Grid: List + Detail Drawer */}
      <div style={{ display: 'grid', gridTemplateColumns: selectedAlert ? '1.5fr 1fr' : '1fr', gap: '20px' }}>
        {/* Alerts Table */}
        <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
                <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>SEV</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>THREAT TITLE</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>HOST / TARGET</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>MITRE</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>STATUS</th>
                <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((a) => {
                const isSelected = selectedAlert?.id === a.id;
                return (
                  <tr 
                    key={a.id}
                    onClick={() => setSelectedAlert(a)}
                    style={{
                      borderBottom: '1px solid var(--border-subtle)',
                      backgroundColor: isSelected ? 'rgba(0, 240, 255, 0.08)' : 'transparent',
                      cursor: 'pointer',
                      transition: 'background-color 0.15s ease'
                    }}
                  >
                    <td style={{ padding: '12px 16px' }}>
                      <span className={`badge badge-${a.severity?.toLowerCase()}`}>
                        {a.severity}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', fontWeight: 600, color: '#ffffff', maxWidth: '300px' }}>
                      <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {a.title}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                        Source: {a.source}
                      </div>
                    </td>
                    <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                      <div style={{ color: '#ffffff' }}>{a.host_name || 'N/A'}</div>
                      <div style={{ color: 'var(--text-dim)', fontSize: '0.72rem' }}>{a.host_ip}</div>
                    </td>
                    <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--cyan)' }}>
                      {a.mitre_technique || 'N/A'}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>
                        {a.status}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <button 
                        className="btn btn-ghost" 
                        style={{ padding: '4px 8px', fontSize: '0.72rem' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedAlert(a);
                        }}
                      >
                        Inspect <ChevronRight size={12} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Alert Details Sidebar */}
        {selectedAlert && (
          <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <span className={`badge badge-${selectedAlert.severity?.toLowerCase()}`} style={{ marginBottom: '8px' }}>
                  {selectedAlert.severity}
                </span>
                <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#ffffff', lineHeight: '1.3' }}>
                  {selectedAlert.title}
                </div>
              </div>
            </div>

            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
              {selectedAlert.description}
            </p>

            {/* Quick Metadata */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '8px',
              padding: '12px',
              backgroundColor: 'rgba(0, 0, 0, 0.35)',
              borderRadius: '6px',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.75rem'
            }}>
              <div><span style={{ color: 'var(--text-dim)' }}>Host:</span> {selectedAlert.host_name}</div>
              <div><span style={{ color: 'var(--text-dim)' }}>IP:</span> {selectedAlert.host_ip}</div>
              <div><span style={{ color: 'var(--text-dim)' }}>Source:</span> {selectedAlert.source}</div>
              <div><span style={{ color: 'var(--text-dim)' }}>MITRE:</span> {selectedAlert.mitre_technique || 'None'}</div>
            </div>

            {/* Status Change Buttons */}
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', marginBottom: '8px', textTransform: 'uppercase' }}>
                Triaging Workflow:
              </div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <button 
                  className="btn btn-ghost" 
                  style={{ fontSize: '0.75rem', padding: '6px 12px' }}
                  onClick={() => handleUpdateStatus(selectedAlert.id, 'ACKNOWLEDGED')}
                >
                  <CheckCircle size={13} color="var(--emerald)" /> Acknowledge
                </button>
                <button 
                  className="btn btn-ghost" 
                  style={{ fontSize: '0.75rem', padding: '6px 12px' }}
                  onClick={() => handleUpdateStatus(selectedAlert.id, 'SUPPRESSED')}
                >
                  <XCircle size={13} color="var(--amber)" /> Suppress
                </button>
                <button 
                  className="btn btn-ghost" 
                  style={{ fontSize: '0.75rem', padding: '6px 12px' }}
                  onClick={() => handleUpdateStatus(selectedAlert.id, 'CLOSED')}
                >
                  Close Alert
                </button>
              </div>
            </div>

            {/* Quick Host Isolation SOAR action */}
            {selectedAlert.host_name && (
              <div style={{
                padding: '12px',
                borderRadius: '6px',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                backgroundColor: 'rgba(239, 68, 68, 0.08)'
              }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#fca5a5', marginBottom: '6px' }}>
                  ACTIVE DEFENSE INTERVENTION
                </div>
                <button 
                  className="btn btn-danger" 
                  style={{ width: '100%', fontSize: '0.78rem' }}
                  onClick={() => handleIsolateHost(selectedAlert.host_name)}
                >
                  <Lock size={14} /> Isolate Host {selectedAlert.host_name}
                </button>
              </div>
            )}

            {/* Raw Event Data JSON Viewer */}
            <div>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', marginBottom: '6px' }}>
                RAW EVENT TELEMETRY PAYLOAD:
              </div>
              <pre className="code-block" style={{ maxHeight: '200px', fontSize: '0.75rem' }}>
                {JSON.stringify(selectedAlert.event_data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

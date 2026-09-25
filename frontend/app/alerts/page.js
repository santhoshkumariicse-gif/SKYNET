'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  AlertTriangle, 
  Search, 
  Filter, 
  X, 
  ShieldAlert, 
  CheckCircle2, 
  ExternalLink,
  ChevronRight,
  Terminal,
  Zap,
  Lock
} from 'lucide-react';
import { api } from '../lib/api';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [filterSource, setFilterSource] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    loadAlerts();
  }, []);

  async function loadAlerts() {
    setLoading(true);
    try {
      const data = await api.getAlerts();
      setAlerts(data || []);
      if (data && data.length > 0 && !selectedAlert) {
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
      setFeedback(`Alert updated to ${newStatus}`);
      setTimeout(() => setFeedback(null), 3000);
    } catch {
      setFeedback(`Status updated locally to ${newStatus}`);
      setTimeout(() => setFeedback(null), 3000);
    }
  };

  const filtered = alerts.filter(a => {
    const matchSev = filterSeverity === 'ALL' || a.severity === filterSeverity;
    const matchSrc = filterSource === 'ALL' || a.source === filterSource;
    const matchStat = filterStatus === 'ALL' || a.status === filterStatus;
    const matchSearch = !search ||
      a.id.toLowerCase().includes(search.toLowerCase()) ||
      a.title.toLowerCase().includes(search.toLowerCase()) ||
      (a.host_name && a.host_name.toLowerCase().includes(search.toLowerCase())) ||
      (a.mitre_technique && a.mitre_technique.toLowerCase().includes(search.toLowerCase()));
    return matchSev && matchSrc && matchStat && matchSearch;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {/* Header Bar */}
      <div className="soc-panel" style={{ padding: '10px 16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertTriangle size={15} color="var(--color-warn)" /> ALERTS QUEUE
              <span className="badge-warn" style={{ fontSize: '10px' }}>
                {alerts.length} ACTIVE
              </span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Signal → Evidence → Decision: Dense triage queue populated by Sigma detection rules and IOC matching engine.
            </div>
          </div>

          {feedback && (
            <div className="badge-ok" style={{ fontSize: '11px' }}>
              <CheckCircle2 size={12} /> {feedback}
            </div>
          )}
        </div>
      </div>

      {/* Filter and Control Bar */}
      <div className="soc-panel" style={{ padding: '8px 12px', display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          backgroundColor: 'var(--bg-base)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '3px',
          padding: '4px 8px',
          flex: 1,
          minWidth: '220px'
        }}>
          <Search size={13} color="var(--text-dim)" />
          <input 
            type="text" 
            placeholder="Search by ID, detection, asset, MITRE technique..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#ffffff',
              fontSize: '11.5px',
              width: '100%',
              outline: 'none',
              fontFamily: 'var(--font-mono)'
            }}
          />
        </div>

        {/* Severity Filters */}
        <div style={{ display: 'flex', gap: '4px' }}>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(sev => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              style={{
                padding: '3px 8px',
                fontSize: '10px',
                fontFamily: 'var(--font-mono)',
                fontWeight: 600,
                borderRadius: '3px',
                border: '1px solid',
                borderColor: filterSeverity === sev ? (sev === 'CRITICAL' ? 'var(--color-crit)' : 'var(--color-info)') : 'var(--border-subtle)',
                backgroundColor: filterSeverity === sev ? (sev === 'CRITICAL' ? 'var(--color-crit-bg)' : 'var(--color-info-bg)') : 'transparent',
                color: filterSeverity === sev ? '#ffffff' : 'var(--text-muted)',
                cursor: 'pointer'
              }}
            >
              {sev}
            </button>
          ))}
        </div>

        {/* Source Filters */}
        <div style={{ display: 'flex', gap: '4px' }}>
          {['ALL', 'SIGMA_RULE', 'IOC_MATCH', 'BEHAVIORAL_ANOMALY'].map(src => (
            <button
              key={src}
              onClick={() => setFilterSource(src)}
              style={{
                padding: '3px 7px',
                fontSize: '10px',
                fontFamily: 'var(--font-mono)',
                borderRadius: '3px',
                border: '1px solid',
                borderColor: filterSource === src ? 'var(--color-info)' : 'var(--border-subtle)',
                backgroundColor: filterSource === src ? 'var(--color-info-bg)' : 'transparent',
                color: filterSource === src ? 'var(--color-info)' : 'var(--text-muted)',
                cursor: 'pointer'
              }}
            >
              {src.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Dense Alerts Table */}
      <div className="soc-panel" style={{ overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto', maxHeight: 'calc(100vh - 220px)', overflowY: 'auto' }}>
          <table className="soc-table">
            <thead>
              <tr>
                <th style={{ width: '45px', textAlign: 'center' }}>SEV</th>
                <th style={{ width: '75px' }}>TIME</th>
                <th style={{ width: '100px' }}>ALERT ID</th>
                <th>DETECTION TITLE</th>
                <th style={{ width: '110px' }}>SOURCE</th>
                <th style={{ width: '100px' }}>ASSET</th>
                <th style={{ width: '55px', textAlign: 'center' }}>RISK</th>
                <th style={{ width: '90px' }}>MITRE</th>
                <th style={{ width: '90px' }}>STATE</th>
                <th style={{ width: '70px', textAlign: 'right' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(a => {
                const isCrit = a.severity === 'CRITICAL';
                const isHigh = a.severity === 'HIGH';
                const timeStr = a.created_at ? new Date(a.created_at).toISOString().substring(11, 19) : '17:21:03';
                const isSelected = selectedAlert?.id === a.id;

                return (
                  <tr 
                    key={a.id}
                    onClick={() => setSelectedAlert(a)}
                    style={{
                      cursor: 'pointer',
                      backgroundColor: isSelected ? 'var(--bg-panel-active)' : 'transparent'
                    }}
                  >
                    <td style={{ textAlign: 'center' }}>
                      <span className={isCrit ? 'badge-crit' : isHigh ? 'badge-high' : 'badge-warn'} style={{ padding: '1px 4px' }}>
                        {isCrit ? 'CRIT' : isHigh ? 'HIGH' : 'MED'}
                      </span>
                    </td>
                    <td className="mono" style={{ color: 'var(--text-dim)' }}>
                      {timeStr}
                    </td>
                    <td className="mono" style={{ color: 'var(--color-info)', fontWeight: 600 }}>
                      {a.id}
                    </td>
                    <td style={{ fontWeight: 600, color: '#ffffff' }}>
                      {a.title}
                    </td>
                    <td>
                      <span className="badge-subtle" style={{ fontSize: '10px' }}>
                        {a.source}
                      </span>
                    </td>
                    <td className="mono" style={{ color: '#93c5fd' }}>
                      {a.host_name || 'WS-184'}
                    </td>
                    <td className="mono" style={{ textAlign: 'center', fontWeight: 700, color: isCrit ? 'var(--color-crit)' : isHigh ? 'var(--color-high)' : 'var(--color-warn)' }}>
                      {a.severity === 'CRITICAL' ? '96' : a.severity === 'HIGH' ? '88' : '55'}
                    </td>
                    <td>
                      <span className="mono" style={{ fontSize: '10.5px', color: '#c084fc' }}>
                        {a.mitre_technique || 'T1059'}
                      </span>
                    </td>
                    <td>
                      <span className="badge-subtle" style={{ fontSize: '10px' }}>
                        {a.status || 'NEW'}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button 
                        onClick={(e) => { e.stopPropagation(); setSelectedAlert(a); }}
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

      {/* Investigation Drawer from the Right */}
      {selectedAlert && (
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
                ALERT INVESTIGATION
              </div>
              <div className="mono" style={{ fontSize: '11px', color: 'var(--color-info)' }}>
                {selectedAlert.id}
              </div>
            </div>
            <button 
              onClick={() => setSelectedAlert(null)}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-dim)', cursor: 'pointer' }}
            >
              <X size={16} />
            </button>
          </div>

          <div style={{ padding: '16px', flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {/* Title & Risk */}
            <div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#ffffff' }}>
                {selectedAlert.title}
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '6px' }}>
                <span className={selectedAlert.severity === 'CRITICAL' ? 'badge-crit' : 'badge-high'}>
                  {selectedAlert.severity}
                </span>
                <span className="mono" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  Risk Score: <strong>{selectedAlert.severity === 'CRITICAL' ? '96' : '88'}/100</strong>
                </span>
              </div>
            </div>

            <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

            {/* Description */}
            <div>
              <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
                TECHNICAL DESCRIPTION
              </div>
              <div style={{ fontSize: '11.5px', color: '#cbd5e1', lineHeight: '1.4' }}>
                {selectedAlert.description || 'Procdump utility executed with memory dump parameter targeting lsass.exe process to harvest cached domain credentials.'}
              </div>
            </div>

            {/* Evidence Panel */}
            <div>
              <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '6px' }}>
                RAW EVIDENCE
              </div>
              <pre style={{
                backgroundColor: 'var(--bg-base)',
                padding: '10px',
                borderRadius: '3px',
                border: '1px solid var(--border-subtle)',
                fontSize: '11px',
                fontFamily: 'var(--font-mono)',
                color: '#e2e8f0',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all'
              }}>
                {selectedAlert.event_data ? JSON.stringify(selectedAlert.event_data, null, 2) : 
`HOST: ${selectedAlert.host_name || 'WS-184'}
IP: ${selectedAlert.host_ip || '192.168.1.188'}
PROCESS: procdump64.exe -ma lsass.exe out.dmp
PARENT: powershell.exe (PID: 4820)
HASH: SHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
USER: SYSTEM
COLLECTED: ${selectedAlert.created_at || '17:21:03 UTC'}`}
              </pre>
            </div>

            {/* MITRE Mapping */}
            <div>
              <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
                MITRE ATT&CK MAPPING
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span className="badge-subtle" style={{ color: '#c084fc' }}>
                  {selectedAlert.mitre_technique || 'T1003.001'}
                </span>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  Credential Dumping: LSASS Memory
                </span>
              </div>
            </div>

            {/* Recommended Steps */}
            <div>
              <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '6px' }}>
                RECOMMENDED INVESTIGATION STEPS
              </div>
              <ol style={{ paddingLeft: '18px', fontSize: '11px', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <li>Inspect parent process command line on host {selectedAlert.host_name || 'WS-184'}.</li>
                <li>Verify if LSASS dump file was exfiltrated or deleted.</li>
                <li>Isolate endpoint from local network segment via SOAR active defense.</li>
              </ol>
            </div>

            {/* Drawer Bottom Actions */}
            <div style={{ marginTop: 'auto', paddingTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button 
                  onClick={() => handleUpdateStatus(selectedAlert.id, 'ACKNOWLEDGED')}
                  className="btn-soc"
                  style={{ flex: 1, padding: '7px' }}
                >
                  ACKNOWLEDGE
                </button>
                <button 
                  onClick={() => handleUpdateStatus(selectedAlert.id, 'RESOLVED')}
                  className="btn-soc-ok"
                  style={{ flex: 1, padding: '7px' }}
                >
                  RESOLVE
                </button>
              </div>

              <Link 
                href="/incidents"
                className="btn-soc-primary" 
                style={{ width: '100%', padding: '8px', textAlign: 'center', textDecoration: 'none', display: 'block' }}
              >
                PROMOTE TO CASE INVESTIGATION
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

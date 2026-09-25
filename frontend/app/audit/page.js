'use client';

import { useState, useEffect } from 'react';
import { 
  ClipboardList, 
  Search, 
  Filter, 
  Lock, 
  User, 
  Clock, 
  FileText,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { api } from '../lib/api';

export default function AuditPage() {
  const [logs, setLogs] = useState([]);
  const [searchAction, setSearchAction] = useState('');
  const [searchActor, setSearchActor] = useState('');
  const [expandedLog, setExpandedLog] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLogs();
  }, [searchAction, searchActor]);

  async function loadLogs() {
    setLoading(true);
    try {
      const params = {};
      if (searchAction) params.action = searchAction;
      if (searchActor) params.actor = searchActor;
      const data = await api.getAuditLogs(params);
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const toggleExpand = (id) => {
    setExpandedLog(expandedLog === id ? null : id);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Title */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ffffff', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ClipboardList size={22} color="var(--emerald)" /> Immutable Forensic Audit Trail
          </h1>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '4px' }}>
            Cryptographically sealed and tamper-evident event log for regulatory compliance and forensic post-mortems.
          </p>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <Search size={14} color="var(--text-dim)" style={{ position: 'absolute', left: '10px', top: '10px' }} />
            <input 
              type="text" 
              placeholder="Search Action..." 
              value={searchAction} 
              onChange={(e) => setSearchAction(e.target.value)}
              className="cyber-input"
              style={{ paddingLeft: '32px', width: '180px' }}
            />
          </div>

          <input 
            type="text" 
            placeholder="Search Actor..." 
            value={searchActor} 
            onChange={(e) => setSearchActor(e.target.value)}
            className="cyber-input"
            style={{ width: '160px' }}
          />
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)', backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>TIMESTAMP (UTC)</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>ACTOR</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>ACTION</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>RESOURCE TYPE</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>RESOURCE ID</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>CLIENT IP</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>PAYLOAD</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => {
              const isExpanded = expandedLog === log.id;
              const isSoar = log.action?.startsWith('SOAR_');

              return (
                <tr key={log.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                    {log.created_at ? log.created_at.substring(0, 19).replace('T', ' ') : 'N/A'}
                  </td>

                  <td style={{ padding: '12px 16px', fontWeight: 600, color: '#ffffff' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <User size={13} color="var(--cyan)" />
                      <span>{log.actor}</span>
                    </div>
                  </td>

                  <td style={{ padding: '12px 16px' }}>
                    <span className={`badge ${isSoar ? 'badge-critical' : 'badge-cyan'}`} style={{ fontSize: '0.68rem' }}>
                      {log.action}
                    </span>
                  </td>

                  <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {log.resource_type}
                  </td>

                  <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: '#ffffff' }}>
                    {log.resource_id}
                  </td>

                  <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                    {log.client_ip}
                  </td>

                  <td style={{ padding: '12px 16px' }}>
                    <button 
                      className="btn btn-ghost" 
                      style={{ padding: '3px 8px', fontSize: '0.72rem' }}
                      onClick={() => toggleExpand(log.id)}
                    >
                      {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />} Details
                    </button>
                    {isExpanded && (
                      <div style={{ marginTop: '8px' }}>
                        <pre className="code-block" style={{ fontSize: '0.72rem', maxHeight: '120px' }}>
                          {JSON.stringify(log.payload, null, 2)}
                        </pre>
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

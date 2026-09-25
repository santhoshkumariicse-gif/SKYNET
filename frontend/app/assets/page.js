'use client';

import { useState, useEffect } from 'react';
import { 
  Server, 
  Search, 
  Lock, 
  Unlock, 
  Cpu, 
  HardDrive, 
  Activity, 
  ShieldCheck, 
  AlertTriangle,
  Radio,
  CheckCircle2
} from 'lucide-react';
import { api } from '../lib/api';

export default function AssetsPage() {
  const [endpoints, setEndpoints] = useState([]);
  const [stats, setStats] = useState(null);
  const [filterStatus, setFilterStatus] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    loadAssets();
  }, [filterStatus, search]);

  async function loadAssets() {
    setLoading(true);
    try {
      const [eps, st] = await Promise.all([
        api.getAssets({ status: filterStatus, search }),
        api.getAssetStats()
      ]);
      setEndpoints(eps);
      setStats(st);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const handleIsolate = async (endpoint) => {
    try {
      await api.isolateEndpoint(endpoint.hostname);
      setEndpoints(prev => prev.map(e => e.hostname === endpoint.hostname ? { ...e, status: 'ISOLATED' } : e));
      setFeedback(`[CONTAINMENT VERIFIED] Host ${endpoint.hostname} isolated from network.`);
      setTimeout(() => setFeedback(null), 5000);
    } catch {
      setFeedback('Failed to isolate host.');
    }
  };

  const handleUnisolate = async (endpoint) => {
    try {
      await api.unisolateEndpoint(endpoint.hostname);
      setEndpoints(prev => prev.map(e => e.hostname === endpoint.hostname ? { ...e, status: 'ONLINE' } : e));
      setFeedback(`[ACCESS RESTORED] Host ${endpoint.hostname} restored to ONLINE status.`);
      setTimeout(() => setFeedback(null), 5000);
    } catch {
      setFeedback('Failed to restore host.');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ffffff', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Server size={22} color="var(--cyan)" /> Endpoint Fleet & Asset Inventory
          </h1>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '4px' }}>
            Real-time health, OS telemetry, resource utilization, and autonomous network containment.
          </p>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <Search size={14} color="var(--text-dim)" style={{ position: 'absolute', left: '10px', top: '10px' }} />
            <input 
              type="text" 
              placeholder="Search hostname or IP..." 
              value={search} 
              onChange={(e) => setSearch(e.target.value)}
              className="cyber-input"
              style={{ paddingLeft: '32px', width: '220px' }}
            />
          </div>

          <select 
            value={filterStatus} 
            onChange={(e) => setFilterStatus(e.target.value)}
            className="cyber-input"
          >
            <option value="">All Statuses</option>
            <option value="ONLINE">Online</option>
            <option value="WARNING">Warning</option>
            <option value="COMPROMISED">Compromised</option>
            <option value="ISOLATED">Isolated</option>
          </select>
        </div>
      </div>

      {feedback && (
        <div style={{
          padding: '12px 16px',
          borderRadius: '8px',
          backgroundColor: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          color: '#6ee7b7',
          fontSize: '0.82rem',
          fontFamily: 'var(--font-mono)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <CheckCircle2 size={16} />
          {feedback}
        </div>
      )}

      {/* Stats Summary Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px'
      }}>
        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Fleet Size</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
            {stats?.total || endpoints.length}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--cyan)' }}>Workstations & Servers</div>
        </div>

        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Online & Healthy</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--emerald)', fontFamily: 'var(--font-mono)' }}>
            {stats?.by_status?.ONLINE || 5}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--emerald)' }}>Active Agent Heartbeats</div>
        </div>

        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Compromised</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--crimson)', fontFamily: 'var(--font-mono)' }}>
            {stats?.by_status?.COMPROMISED || 1}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--crimson)' }}>Immediate Containment Needed</div>
        </div>

        <div className="glass-panel" style={{ padding: '16px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Isolated (Sandboxed)</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--purple)', fontFamily: 'var(--font-mono)' }}>
            {stats?.by_status?.ISOLATED || endpoints.filter(e => e.status === 'ISOLATED').length}
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--purple)' }}>Network Quarantined</div>
        </div>
      </div>

      {/* Endpoints Table */}
      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)', backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>STATUS</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>HOSTNAME</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>IP ADDRESS</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>OS PLATFORM</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>RESOURCE LOAD</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>ACTIVE DEFENSE</th>
            </tr>
          </thead>
          <tbody>
            {endpoints.map((ep) => {
              const isCompromised = ep.status === 'COMPROMISED';
              const isIsolated = ep.status === 'ISOLATED';

              return (
                <tr 
                  key={ep.id}
                  style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    backgroundColor: isCompromised ? 'rgba(239, 68, 68, 0.06)' : isIsolated ? 'rgba(168, 85, 247, 0.06)' : 'transparent'
                  }}
                >
                  <td style={{ padding: '12px 16px' }}>
                    <span className={`badge ${
                      isCompromised ? 'badge-critical' : isIsolated ? 'badge-isolated' : ep.status === 'WARNING' ? 'badge-medium' : 'badge-online'
                    }`}>
                      {ep.status}
                    </span>
                  </td>

                  <td style={{ padding: '12px 16px', fontWeight: 600, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
                    {ep.hostname}
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontWeight: 400 }}>
                      Type: {ep.device_type}
                    </div>
                  </td>

                  <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--cyan)' }}>
                    {ep.ip_address}
                  </td>

                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ color: '#ffffff' }}>{ep.os_name}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{ep.os_version}</div>
                  </td>

                  {/* Resource Gauges */}
                  <td style={{ padding: '12px 16px', minWidth: '180px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                        <span>CPU: {ep.cpu_usage}%</span>
                        <span>MEM: {ep.memory_usage}%</span>
                      </div>
                      <div style={{ height: '4px', backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                        <div style={{
                          height: '100%',
                          width: `${ep.cpu_usage}%`,
                          backgroundColor: ep.cpu_usage > 80 ? 'var(--crimson)' : 'var(--cyan)'
                        }}></div>
                      </div>
                    </div>
                  </td>

                  {/* SOAR Action */}
                  <td style={{ padding: '12px 16px' }}>
                    {isIsolated ? (
                      <button 
                        className="btn btn-ghost"
                        style={{ fontSize: '0.75rem', padding: '6px 12px', color: '#6ee7b7', borderColor: 'rgba(16, 185, 129, 0.4)' }}
                        onClick={() => handleUnisolate(ep)}
                      >
                        <Unlock size={13} /> Restore Access
                      </button>
                    ) : (
                      <button 
                        className="btn btn-danger"
                        style={{ fontSize: '0.75rem', padding: '6px 12px' }}
                        onClick={() => handleIsolate(ep)}
                      >
                        <Lock size={13} /> Isolate Host
                      </button>
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

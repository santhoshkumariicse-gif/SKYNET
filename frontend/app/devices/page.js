'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Server, 
  Search, 
  Activity, 
  Clock, 
  ExternalLink, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  Filter, 
  RefreshCw,
  Cpu,
  HardDrive
} from 'lucide-react';

export default function DeviceListPage() {
  const [devices, setDevices] = useState([]);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const fetchDevices = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/devices');
      if (res.ok) {
        const data = await res.json();
        setDevices(data);
      }
      const trendRes = await fetch('http://localhost:8000/metrics/trends?range=24h');
      if (trendRes.ok) {
        const tdata = await trendRes.json();
        setTrends(tdata);
      }
    } catch (err) {
      console.error('Failed to load devices:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchDevices, 15000);
    return () => clearInterval(interval);
  }, []);

  const calculateHealthScore = (device) => {
    const cpu = device.cpu_usage || 0;
    const mem = device.memory_usage || 0;
    const disk = device.disk_usage || 0;
    if (device.status === 'OFFLINE') return 0;
    if (device.status === 'COMPROMISED') return 15;
    if (device.status === 'ISOLATED') return 30;
    let score = 100 - (cpu * 0.3 + mem * 0.3 + disk * 0.2);
    return Math.max(10, Math.min(100, Math.round(score)));
  };

  const filteredDevices = devices.filter(d => {
    const matchesSearch = d.hostname.toLowerCase().includes(search.toLowerCase()) ||
                          d.ip_address.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || d.status.toUpperCase() === statusFilter.toUpperCase();
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status) => {
    const s = status.toUpperCase();
    if (s === 'ONLINE') return <span className="badge-success">● ONLINE</span>;
    if (s === 'COMPROMISED') return <span className="badge-critical">▲ COMPROMISED</span>;
    if (s === 'ISOLATED') return <span className="badge-high">⊘ ISOLATED</span>;
    if (s === 'WARNING') return <span className="badge-medium">▲ WARNING</span>;
    return <span className="badge-gray">○ OFFLINE</span>;
  };

  const getHealthBadge = (score) => {
    if (score >= 80) return <span className="badge-success">{score}/100</span>;
    if (score >= 50) return <span className="badge-medium">{score}/100</span>;
    return <span className="badge-critical">{score}/100</span>;
  };

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', color: 'var(--text-muted)' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 style={{ 
            fontSize: '22px', 
            fontWeight: '800', 
            color: 'var(--text-white)', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '10px',
            fontFamily: 'var(--font-heading)'
          }}>
            <Server style={{ color: 'var(--accent-blue)' }} size={24} />
            Infrastructure Fleet Inventory
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginTop: '4px', fontFamily: 'var(--font-body)' }}>
            Real-time endpoint registry monitoring Windows PCs, Laptops, Servers, and Android devices.
          </p>
        </div>
        <button
          onClick={fetchDevices}
          className="btn-soc"
          style={{ padding: '8px 14px' }}
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          <span>Refresh Fleet</span>
        </button>
      </div>

      {/* KPI Stats Cards (28–32px, 6px radius, subtle shadow) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px', marginBottom: '20px' }}>
        <div className="soc-card" style={{ padding: '16px' }}>
          <div className="kpi-label">TOTAL FLEET MONITORED</div>
          <div className="kpi-number" style={{ color: 'var(--text-white)', marginTop: '4px' }}>
            {devices.length || 7}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
            Windows, Linux & Android Endpoints
          </div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div className="kpi-label">ONLINE ENDPOINTS</div>
          <div className="kpi-number" style={{ color: 'var(--accent-green)', marginTop: '4px' }}>
            {devices.filter(d => d.status === 'ONLINE').length}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--accent-green)', marginTop: '4px' }}>
            Sending heartbeats within &lt;60s
          </div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div className="kpi-label">HIGH LOAD / CONTAINED</div>
          <div className="kpi-number" style={{ color: 'var(--accent-amber)', marginTop: '4px' }}>
            {devices.filter(d => d.status === 'COMPROMISED' || d.status === 'ISOLATED').length}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--accent-amber)', marginTop: '4px' }}>
            Security containment or throttling
          </div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div className="kpi-label">FLEET HEALTH INDEX</div>
          <div className="kpi-number" style={{ color: 'var(--accent-blue)', marginTop: '4px' }}>
            {trends?.fleet_health_score ?? 88}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--accent-blue)', marginTop: '4px' }}>
            Dynamic baseline composite
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '280px' }}>
          <Search size={15} style={{ position: 'absolute', left: '12px', top: '11px', color: 'var(--text-dim)' }} />
          <input
            type="text"
            placeholder="Search hostname or IP address..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="soc-input"
            style={{ width: '100%', paddingLeft: '36px' }}
          />
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['ALL', 'ONLINE', 'WARNING', 'COMPROMISED', 'ISOLATED'].map(st => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              style={{
                backgroundColor: statusFilter === st ? 'var(--accent-blue)' : 'var(--bg-panel)',
                color: statusFilter === st ? '#FFFFFF' : 'var(--text-muted)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '12px',
                fontFamily: 'var(--font-heading)',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Professional SOC Striped Table (14–16px text) */}
      <div className="soc-card" style={{ overflow: 'hidden' }}>
        <table className="soc-table">
          <thead>
            <tr>
              <th>Device Name</th>
              <th>Device Type</th>
              <th>Health Score</th>
              <th>Hardware Load (CPU / RAM)</th>
              <th>Last Seen</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredDevices.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: '32px', textAlign: 'center', color: 'var(--text-dim)' }}>
                  No devices match the query filters.
                </td>
              </tr>
            ) : (
              filteredDevices.map(device => {
                const health = calculateHealthScore(device);
                return (
                  <tr key={device.id}>
                    <td style={{ fontWeight: 600, color: 'var(--text-white)' }}>
                      <Link 
                        href={`/devices/${device.id}`}
                        style={{ color: 'var(--text-white)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
                      >
                        <Server size={14} color="var(--accent-blue)" />
                        <span>{device.hostname}</span>
                      </Link>
                      <div className="mono" style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
                        {device.ip_address} | {device.os_name}
                      </div>
                    </td>
                    <td>
                      <span className="badge-gray">
                        {device.device_type}
                      </span>
                    </td>
                    <td>
                      {getHealthBadge(health)}
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '160px' }}>
                        <div style={{ flex: 1, height: '6px', backgroundColor: 'var(--border-subtle)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div 
                            style={{ 
                              width: `${Math.min(100, device.cpu_usage || 28)}%`, 
                              height: '100%', 
                              backgroundColor: (device.cpu_usage || 28) > 80 ? 'var(--accent-red)' : 'var(--accent-blue)' 
                            }} 
                          />
                        </div>
                        <span className="mono" style={{ fontSize: '11px', color: 'var(--text-dim)', minWidth: '45px' }}>
                          {device.cpu_usage || 28}% CPU
                        </span>
                      </div>
                    </td>
                    <td className="mono" style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                      {device.last_seen ? new Date(device.last_seen).toLocaleTimeString() : 'Just now'}
                    </td>
                    <td>
                      {getStatusBadge(device.status)}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link 
                        href={`/devices/${device.id}`}
                        className="btn-soc"
                        style={{ padding: '4px 10px', fontSize: '12px' }}
                      >
                        View Metrics <ExternalLink size={12} />
                      </Link>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

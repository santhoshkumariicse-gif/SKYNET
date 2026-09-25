'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  ShieldAlert, 
  FileWarning, 
  Server, 
  Zap, 
  Activity, 
  ArrowUpRight, 
  CheckCircle2, 
  AlertTriangle,
  Cpu,
  Clock,
  Terminal,
  Crosshair,
  Lock
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  Cell 
} from 'recharts';
import { api } from './lib/api';

const TIME_SERIES_DATA = [
  { time: '08:00', alerts: 4, critical: 1 },
  { time: '09:00', alerts: 7, critical: 2 },
  { time: '10:00', alerts: 12, critical: 3 },
  { time: '11:00', alerts: 9, critical: 1 },
  { time: '12:00', alerts: 16, critical: 4 },
  { time: '13:00', alerts: 24, critical: 6 },
  { time: '14:00', alerts: 18, critical: 3 },
];

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [soarFeedback, setSoarFeedback] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, alertsData, incidentsData] = await Promise.all([
          api.getDashboardStats(),
          api.getAlerts({ limit: 5 }),
          api.getIncidents({ limit: 3 })
        ]);
        setStats(statsData);
        setAlerts(alertsData);
        setIncidents(incidentsData);
      } catch (err) {
        console.error('Error loading dashboard:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleQuickContain = async (hostname) => {
    try {
      const res = await api.executeContainment({
        action_type: 'ISOLATE_HOST',
        target_identifier: hostname,
        reason: 'Immediate 1-Click Containment from SOC Command Center',
        rollback_plan: 'Restore endpoint via Fleet Management'
      });
      setSoarFeedback(`[CONTAINMENT VERIFIED] Host ${hostname} isolated. HMAC Token: ${res.signed_token?.substring(0, 16)}...`);
      setTimeout(() => setSoarFeedback(null), 6000);
    } catch {
      setSoarFeedback('Containment dispatch error. Check logs.');
    }
  };

  const severityBarData = stats ? [
    { name: 'CRITICAL', count: stats.alerts.by_severity.CRITICAL || 0, color: '#ef4444' },
    { name: 'HIGH', count: stats.alerts.by_severity.HIGH || 0, color: '#f97316' },
    { name: 'MEDIUM', count: stats.alerts.by_severity.MEDIUM || 0, color: '#f59e0b' },
    { name: 'LOW', count: stats.alerts.by_severity.LOW || 0, color: '#3b82f6' },
  ] : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Banner / Headline */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px 20px',
        borderRadius: '10px',
        background: 'linear-gradient(90deg, rgba(239, 68, 68, 0.12) 0%, rgba(15, 23, 42, 0.6) 100%)',
        border: '1px solid rgba(239, 68, 68, 0.3)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div className="pulse-dot pulse-dot-red" style={{ width: '12px', height: '12px' }}></div>
          <div>
            <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fca5a5', letterSpacing: '0.04em' }}>
              CRITICAL INCIDENT ACTIVE: Cobalt Strike Ingress on Host FIN-LAPTOP-042
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Autonomous Tier-1 agent completed triage and mapped 4 MITRE ATT&CK techniques. Containment recommended.
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button 
            className="btn btn-danger"
            onClick={() => handleQuickContain('FIN-LAPTOP-042')}
          >
            <Lock size={14} /> 1-Click Isolate Host
          </button>
          <Link href="/incidents" className="btn btn-ghost">
            View AI Dossier <ArrowUpRight size={14} />
          </Link>
        </div>
      </div>

      {soarFeedback && (
        <div style={{
          padding: '12px 18px',
          borderRadius: '8px',
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          color: '#6ee7b7',
          fontSize: '0.82rem',
          fontFamily: 'var(--font-mono)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <CheckCircle2 size={16} />
          {soarFeedback}
        </div>
      )}

      {/* KPI Cards Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px',
      }}>
        {/* Total Alerts */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-dim)', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Detections</span>
            <ShieldAlert size={18} color="var(--cyan)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
            {stats?.alerts?.total || 48}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--crimson)', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>{stats?.alerts?.critical || 6} Critical Alerts</span>
          </div>
        </div>

        {/* Active Incidents */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-dim)', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Open Incidents</span>
            <FileWarning size={18} color="var(--amber)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
            {stats?.incidents?.open || 3}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--amber)', marginTop: '4px' }}>
            1 Under AI Deep Investigation
          </div>
        </div>

        {/* Fleet Security */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-dim)', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Compromised Hosts</span>
            <Server size={18} color="var(--crimson)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--crimson)', fontFamily: 'var(--font-mono)' }}>
            {stats?.endpoints?.compromised || 1} <span style={{ fontSize: '1rem', color: 'var(--text-dim)' }}>/ {stats?.endpoints?.total || 7}</span>
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Host: FIN-LAPTOP-042
          </div>
        </div>

        {/* AI MTTR Performance */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-dim)', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>MTTR Response</span>
            <Clock size={18} color="var(--emerald)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--emerald)', fontFamily: 'var(--font-mono)' }}>
            4.2m
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--emerald)', marginTop: '4px' }}>
            90% Autonomous AI Resolution
          </div>
        </div>

        {/* MITRE Coverage */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-dim)', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>ATT&CK Coverage</span>
            <Crosshair size={18} color="var(--purple)" />
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#c084fc', fontFamily: 'var(--font-mono)' }}>
            85%
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            17 of 20 Tracked Techniques
          </div>
        </div>
      </div>

      {/* Visual Analytics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Telemetry Stream Chart */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>Live Attack Ingress & Telemetry Volume</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Hourly event evaluation across Windows Sysmon & RFC 5424 Syslog</div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span className="pulse-dot pulse-dot-green"></span>
              <span style={{ fontSize: '0.7rem', color: 'var(--emerald)', fontFamily: 'var(--font-mono)' }}>REAL-TIME FEED</span>
            </div>
          </div>

          <div style={{ height: '220px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={TIME_SERIES_DATA}>
                <defs>
                  <linearGradient id="alertGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#00f0ff" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="critGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.6}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#475569" fontSize={11} fontFamily="var(--font-mono)" />
                <YAxis stroke="#475569" fontSize={11} fontFamily="var(--font-mono)" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0b1120', borderColor: '#1e293b', borderRadius: '6px' }}
                  itemStyle={{ fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="alerts" stroke="#00f0ff" strokeWidth={2} fillOpacity={1} fill="url(#alertGrad)" name="Total Events" />
                <Area type="monotone" dataKey="critical" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#critGrad)" name="Critical Threats" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '4px' }}>Threat Severity Breakdown</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '16px' }}>Current active alert distribution</div>

          <div style={{ height: '220px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityBarData} layout="vertical">
                <XAxis type="number" stroke="#475569" fontSize={11} fontFamily="var(--font-mono)" />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={11} width={80} fontFamily="var(--font-mono)" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0b1120', borderColor: '#1e293b', borderRadius: '6px' }}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {severityBarData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Grid: Live Alerts Feed & Active Incident Details */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px' }}>
        {/* Real-time Alerts Ticker */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={18} color="var(--cyan)" />
              <div style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>Live Correlated Alerts</div>
            </div>
            <Link href="/alerts" style={{ fontSize: '0.78rem', color: 'var(--cyan)', textDecoration: 'none' }}>
              View All 48 Alerts &rarr;
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {alerts.slice(0, 4).map((a) => (
              <div 
                key={a.id}
                style={{
                  padding: '12px 14px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '12px'
                }}
              >
                <div style={{ minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span className={`badge badge-${a.severity?.toLowerCase()}`}>
                      {a.severity}
                    </span>
                    <span style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: 'var(--cyan)' }}>
                      {a.mitre_technique || 'SIGMA'}
                    </span>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                      {a.host_name}
                    </span>
                  </div>
                  <div style={{
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    color: '#ffffff',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {a.title}
                  </div>
                </div>

                <div style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                  <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>
                    {a.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Autonomous Incident Spotlight */}
        <div className="glass-panel" style={{ padding: '20px', border: '1px solid rgba(239, 68, 68, 0.35)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Terminal size={18} color="var(--crimson)" />
              <div style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>AI Incident Dossier [INC-2026-0001]</div>
            </div>
            <span className="badge badge-critical">TRUE POSITIVE</span>
          </div>

          <div style={{
            fontSize: '0.85rem',
            color: 'var(--text-muted)',
            marginBottom: '14px',
            lineHeight: '1.5'
          }}>
            Cobalt Strike Beacon Infiltration & Credential Dumping detected across FIN-LAPTOP-042. Attacker established persistence and accessed LSASS memory.
          </div>

          {/* AI Root Cause Box */}
          <div style={{
            padding: '12px',
            borderRadius: '6px',
            backgroundColor: 'rgba(0, 0, 0, 0.45)',
            borderLeft: '3px solid var(--cyan)',
            marginBottom: '16px'
          }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--cyan)', fontFamily: 'var(--font-mono)', marginBottom: '4px' }}>
              ROOT CAUSE ANALYSIS (AI REASONING):
            </div>
            <div style={{ fontSize: '0.78rem', color: '#e2e8f0', lineHeight: '1.4' }}>
              Phishing attachment delivered obfuscated PowerShell script bypassing AMSI, downloading second-stage beacon from remote C2 node 185.220.101.5.
            </div>
          </div>

          {/* MITRE Tags */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '18px' }}>
            {['T1059.001 PowerShell', 'T1003.001 LSASS', 'T1105 Tool Transfer', 'T1071.001 C2'].map((tag) => (
              <span key={tag} style={{
                fontSize: '0.68rem',
                fontFamily: 'var(--font-mono)',
                padding: '3px 7px',
                borderRadius: '4px',
                backgroundColor: 'rgba(168, 85, 247, 0.15)',
                color: '#d8b4fe',
                border: '1px solid rgba(168, 85, 247, 0.3)'
              }}>
                {tag}
              </span>
            ))}
          </div>

          <Link href="/incidents" className="btn btn-primary" style={{ width: '100%' }}>
            Open Incident Investigation Cockpit &rarr;
          </Link>
        </div>
      </div>
    </div>
  );
}

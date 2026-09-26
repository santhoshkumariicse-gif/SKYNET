'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Shield, 
  AlertTriangle, 
  Activity, 
  Server, 
  ArrowUpRight, 
  CheckCircle2, 
  Clock, 
  X, 
  ExternalLink,
  ChevronRight,
  Filter,
  RefreshCw,
  Zap,
  Play
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { api } from './lib/api';

const TIME_SERIES_DATA = [
  { time: '11:00', events: 1420, alerts: 12, critical: 0 },
  { time: '12:00', events: 1890, alerts: 18, critical: 1 },
  { time: '13:00', events: 2100, alerts: 24, critical: 2 },
  { time: '14:00', events: 1650, alerts: 14, critical: 0 },
  { time: '15:00', events: 2410, alerts: 31, critical: 3 },
  { time: '16:00', events: 1980, alerts: 22, critical: 1 },
  { time: '17:00', events: 2210, alerts: 26, critical: 2 },
];

const INITIAL_LIVE_EVENTS = [
  { id: 'EVT-8F291A', time: '17:24:31', source: 'AUTH', asset: 'USER-421', event: 'Failed login (4625)', process: 'logon.exe', parent: 'winlogon.exe', user: 'user421@corp.local', dest: '10.0.4.12', raw_evidence: 'Event 4625 SubStatus 0xC000006A (Bad Password)' },
  { id: 'EVT-8F291B', time: '17:24:30', source: 'EDR', asset: 'WS-182', event: 'PowerShell spawned from Winword', process: 'powershell.exe', parent: 'winword.exe', user: 'finance_lead', dest: '185.220.101.5:443', raw_evidence: 'powershell -NoP -Enc SQBFAFgAIAAoAE4AZQB3AC0...' },
  { id: 'EVT-8F291C', time: '17:24:30', source: 'DNS', asset: 'WS-182', event: 'Query → suspicious-domain.top', process: 'svchost.exe', parent: 'services.exe', user: 'SYSTEM', dest: '185.220.101.5', raw_evidence: 'DNS Type A request to update-microsoft-verify.top' },
  { id: 'EVT-8F291D', time: '17:24:29', source: 'FIREWALL', asset: 'FW-01', event: 'Outbound TCP:443 blocked by policy', process: 'paloalto', parent: 'kernel', user: 'N/A', dest: '185.220.101.5:443', raw_evidence: 'RULE: Block-Malicious-C2-Feed hit on port 443' },
  { id: 'EVT-8F291E', time: '17:24:28', source: 'IAM', asset: 'USER-421', event: 'MFA challenge failed 3x', process: 'okta-verify', parent: 'system', user: 'user421@corp.local', dest: '10.0.4.12', raw_evidence: 'Okta push timeout and rejection from unknown geo: RU' },
  { id: 'EVT-8F291F', time: '17:24:21', source: 'EDR', asset: 'DC-02', event: 'LSASS memory read access handle', process: 'procdump64.exe', parent: 'cmd.exe', user: 'SYSTEM', dest: 'LOCAL', raw_evidence: 'procdump64.exe -ma lsass.exe C:\\Windows\\Temp\\lsass.dmp' },
  { id: 'EVT-8F2920', time: '17:24:15', source: 'EDR', asset: 'SRV-14', event: 'Shadow copy deletion attempted', process: 'vssadmin.exe', parent: 'powershell.exe', user: 'SYSTEM', dest: 'LOCAL', raw_evidence: 'vssadmin.exe delete shadows /all /quiet' },
];

export default function CommandCenterPage() {
  const [stats, setStats] = useState(null);
  const [fleetTrends, setFleetTrends] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [liveEvents, setLiveEvents] = useState(INITIAL_LIVE_EVENTS);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, incidentsData] = await Promise.all([
          api.getDashboardStats(),
          api.getIncidents({ limit: 6 })
        ]);
        setStats(statsData);
        setIncidents(incidentsData || []);

        try {
          const tRes = await fetch('http://localhost:8000/metrics/trends?range=24h');
          if (tRes.ok) {
            const tData = await tRes.json();
            setFleetTrends(tData);
          }
        } catch {}
      } catch (err) {
        console.error('Failed to load command center stats:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();

    let ws;
    try {
      ws = new WebSocket('ws://localhost:8000/api/v1/ws/live-events');
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          if (msg.event) {
            setLiveEvents(prev => [msg.event, ...prev.slice(0, 19)]);
          }
        } catch {}
      };
    } catch {}

    return () => {
      if (ws) ws.close();
    };
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Screen Title & Top Operational Status Bar */}
      <div className="soc-card" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <h1 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-white)', letterSpacing: '-0.01em', fontFamily: 'var(--font-heading)', margin: 0 }}>
              SKYNET COMMAND CENTER
            </h1>
            <div style={{ fontSize: '13px', color: 'var(--text-dim)', marginTop: '3px', fontFamily: 'var(--font-body)' }}>
              Autonomous SOC Command & SIEM Telemetry Correlation Grid
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-dim)', textTransform: 'uppercase', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>SYSTEM STATUS</div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--accent-green)', display: 'flex', alignItems: 'center', gap: '6px', fontFamily: 'var(--font-heading)' }}>
                <span style={{ fontSize: '9px' }}>●</span> ALL SYSTEMS OPERATIONAL
              </div>
            </div>

            <div style={{ height: '24px', width: '1px', backgroundColor: 'var(--border-subtle)' }} />

            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-dim)', textTransform: 'uppercase', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>LAST 24 HOURS</div>
              <div style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-white)' }}>
                <span style={{ fontWeight: 700 }}>12,481</span> EVENTS &nbsp;|&nbsp;
                <span style={{ fontWeight: 700, color: 'var(--accent-amber)' }}>137</span> ALERTS &nbsp;|&nbsp;
                <span style={{ fontWeight: 700, color: 'var(--accent-orange)' }}>18</span> INCIDENTS &nbsp;|&nbsp;
                <span style={{ fontWeight: 700, color: 'var(--accent-red)' }}>4</span> CRITICAL
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 6 High-Density Fleet Overview KPI Blocks (28–32px numbers, 6px radius) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
        <div className="soc-card" style={{ padding: '16px' }}>
          <div className="kpi-label">TOTAL DEVICES</div>
          <div className="kpi-number" style={{ color: 'var(--text-white)', marginTop: '4px' }}>
            {fleetTrends?.device_summary?.total ?? (stats?.endpoints_monitored || 48)}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--accent-blue)', fontFamily: 'var(--font-body)', marginTop: '3px' }}>Fleet CMDB Inventory</div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div className="kpi-label">ONLINE DEVICES</div>
          <div className="kpi-number" style={{ color: 'var(--accent-green)', marginTop: '4px' }}>
            {fleetTrends?.device_summary?.online ?? 44}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--accent-green)', fontFamily: 'var(--font-body)', marginTop: '3px' }}>Actively Heartbeating</div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div className="kpi-label">OFFLINE DEVICES</div>
          <div className="kpi-number" style={{ color: 'var(--accent-amber)', marginTop: '4px' }}>
            {fleetTrends?.device_summary?.offline ?? 4}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--accent-amber)', fontFamily: 'var(--font-body)', marginTop: '3px' }}>Requires Attention</div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div className="kpi-label">FLEET HEALTH SCORE</div>
          <div className="kpi-number" style={{ color: 'var(--accent-blue)', marginTop: '4px' }}>
            {fleetTrends?.fleet_health_score ?? 88}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--accent-green)', fontFamily: 'var(--font-body)', marginTop: '3px' }}>Composite Health Index</div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div className="kpi-label">ACTIVE ALERTS</div>
          <div className="kpi-number" style={{ color: 'var(--accent-amber)', marginTop: '4px' }}>
            {fleetTrends?.device_summary?.active_alerts ?? (stats?.active_alerts || 4)}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--accent-amber)', fontFamily: 'var(--font-body)', marginTop: '3px' }}>Threshold Breaches</div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div className="kpi-label">ACTIVE INCIDENTS</div>
          <div className="kpi-number" style={{ color: 'var(--accent-red)', marginTop: '4px' }}>
            {incidents.length || stats?.open_incidents || 1}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--accent-red)', fontFamily: 'var(--font-body)', marginTop: '3px' }}>Under Investigation</div>
        </div>
      </div>

      {/* ACTIVE INCIDENTS (Dense Enterprise Table) */}
      <div className="soc-card" style={{ overflow: 'hidden' }}>
        <div style={{
          padding: '12px 16px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-white)', fontFamily: 'var(--font-heading)' }}>
            ACTIVE INCIDENTS
          </div>
          <Link href="/incidents" style={{ color: 'var(--accent-blue)', fontSize: '12px', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px', fontFamily: 'var(--font-heading)', fontWeight: 600 }}>
            View All ({incidents.length}) <ChevronRight size={13} />
          </Link>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="soc-table">
            <thead>
              <tr>
                <th style={{ width: '80px' }}>SEV</th>
                <th style={{ width: '140px' }}>INCIDENT</th>
                <th>TITLE / DESCRIPTION</th>
                <th style={{ width: '110px' }}>ASSET</th>
                <th style={{ width: '100px' }}>USER</th>
                <th style={{ width: '70px' }}>RISK</th>
                <th style={{ width: '90px' }}>OWNER</th>
                <th style={{ width: '120px' }}>STATUS</th>
                <th style={{ width: '100px', textAlign: 'right' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {incidents.slice(0, 5).map(inc => {
                const sev = inc.severity || 'HIGH';
                const isCrit = sev === 'CRITICAL';
                return (
                  <tr key={inc.id}>
                    <td>
                      <span className={isCrit ? 'badge-critical' : sev === 'HIGH' ? 'badge-high' : 'badge-medium'}>
                        {sev.substring(0, 4)}
                      </span>
                    </td>
                    <td className="mono" style={{ color: 'var(--accent-blue)', fontWeight: 600 }}>
                      <Link href={`/incidents?id=${inc.id}`} style={{ color: 'inherit', textDecoration: 'none' }}>
                        {inc.incident_number || inc.id}
                      </Link>
                    </td>
                    <td style={{ fontWeight: 600 }}>
                      {inc.title}
                    </td>
                    <td className="mono" style={{ color: '#93c5fd' }}>
                      {inc.affected_assets?.[0] || 'DC-02'}
                    </td>
                    <td className="mono" style={{ color: 'var(--text-muted)' }}>
                      {inc.user || 'admin'}
                    </td>
                    <td className="mono" style={{ fontWeight: 700, color: isCrit ? 'var(--color-crit)' : 'var(--color-high)' }}>
                      {inc.risk_score || 92}
                    </td>
                    <td className="mono" style={{ color: 'var(--text-dim)' }}>
                      {inc.assigned_to || 'SOC'}
                    </td>
                    <td>
                      <span className="badge-subtle">
                        {inc.status || 'INVESTIGATING'}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link href={`/incidents?id=${inc.id}`} className="btn-soc" style={{ padding: '3px 8px', fontSize: '11px' }}>
                        INVESTIGATE
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Two Column Lower Section: LIVE EVENT STREAM & SECURITY ACTIVITY */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '14px' }}>
        {/* LEFT: LIVE EVENT STREAM */}
        <div className="soc-card" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{
            padding: '12px 16px',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-white)', fontFamily: 'var(--font-heading)' }}>
              LIVE EVENT STREAM
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--accent-green)', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>
              <span style={{ fontSize: '8px' }}>●</span> STREAM LIVE
            </div>
          </div>

          <div style={{ overflowX: 'auto', flex: 1, maxHeight: '280px', overflowY: 'auto' }}>
            <table className="soc-table">
              <thead>
                <tr>
                  <th style={{ width: '75px' }}>TIME</th>
                  <th style={{ width: '85px' }}>SOURCE</th>
                  <th style={{ width: '90px' }}>ASSET</th>
                  <th>EVENT DETAILS</th>
                </tr>
              </thead>
              <tbody>
                {liveEvents.map(evt => (
                  <tr 
                    key={evt.id} 
                    onClick={() => setSelectedEvent(evt)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td className="mono" style={{ color: 'var(--text-dim)' }}>{evt.time}</td>
                    <td>
                      <span className="badge-subtle" style={{ fontSize: '10px' }}>{evt.source}</span>
                    </td>
                    <td className="mono" style={{ color: 'var(--accent-blue)' }}>{evt.asset}</td>
                    <td style={{ color: 'var(--text-white)' }}>{evt.event}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* RIGHT: SECURITY ACTIVITY & AUTOMATION STATE */}
        <div className="soc-card" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{
            padding: '12px 16px',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-white)', fontFamily: 'var(--font-heading)' }}>
              SECURITY ACTIVITY & APPROVALS
            </div>
            <span className="badge-high" style={{ fontSize: '10.5px' }}>
              3 WAITING APPROVAL
            </span>
          </div>

          <div style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '11.5px' }}>
            {/* Approval Notice 1 */}
            <div style={{
              padding: '10px',
              backgroundColor: 'var(--bg-panel-subtle)',
              border: '1px solid var(--border-subtle)',
              borderLeft: '3px solid var(--color-crit)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <div style={{ fontWeight: 700, color: 'var(--text-white)' }}>
                  Isolate Endpoint WS-182
                </div>
                <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                  INC-10482 | Risk: 96 | Reason: Active C2 Beacon to 185.220.101.5
                </div>
              </div>
              <div style={{ display: 'flex', gap: '6px' }}>
                <Link href="/approvals" className="btn-soc-crit" style={{ padding: '4px 8px', fontSize: '11px', textDecoration: 'none' }}>
                  REVIEW & APPROVE
                </Link>
              </div>
            </div>

            {/* Approval Notice 2 */}
            <div style={{
              padding: '10px',
              backgroundColor: 'var(--bg-panel-subtle)',
              border: '1px solid var(--border-subtle)',
              borderLeft: '3px solid var(--color-high)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <div style={{ fontWeight: 700, color: 'var(--text-white)' }}>
                  Disable Account USER-421
                </div>
                <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                  INC-10482 | Risk: 88 | Reason: Impossible Travel & MFA Brute Force
                </div>
              </div>
              <div style={{ display: 'flex', gap: '6px' }}>
                <Link href="/approvals" className="btn-soc" style={{ padding: '4px 8px', fontSize: '11px', textDecoration: 'none' }}>
                  REVIEW
                </Link>
              </div>
            </div>

            {/* Pipeline Feed Status */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '8px',
              marginTop: '4px',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px'
            }}>
              <div style={{ padding: '6px 8px', backgroundColor: 'var(--bg-base)', border: '1px solid var(--border-subtle)' }}>
                <span style={{ color: 'var(--text-dim)' }}>CORRELATION:</span> <span style={{ color: 'var(--color-ok)' }}>12 RULES RUNNING</span>
              </div>
              <div style={{ padding: '6px 8px', backgroundColor: 'var(--bg-base)', border: '1px solid var(--border-subtle)' }}>
                <span style={{ color: 'var(--text-dim)' }}>TIP LOOKUPS:</span> <span style={{ color: 'var(--color-ok)' }}>5 FEEDS ACTIVE</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* THREAT ACTIVITY (Restrained Time-Series Line/Area) */}
      <div className="soc-card" style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-white)', fontFamily: 'var(--font-heading)' }}>
            THREAT ACTIVITY TIMELINE (HOURLY INGESTION & ANOMALIES)
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: 'var(--font-heading)', fontWeight: 600 }}>
            UTC OPERATIONAL BASELINE
          </span>
        </div>
        <div style={{ height: '140px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={TIME_SERIES_DATA} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <XAxis dataKey="time" stroke="var(--text-dim)" fontSize={10} tickLine={false} />
              <YAxis stroke="var(--text-dim)" fontSize={10} tickLine={false} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'var(--bg-panel)', 
                  borderColor: 'var(--border-subtle)', 
                  borderRadius: '6px',
                  fontSize: '12px',
                  color: 'var(--text-white)',
                  boxShadow: 'var(--card-shadow)'
                }} 
              />
              <Area type="monotone" dataKey="events" stroke="var(--accent-blue)" strokeWidth={1.8} fill="var(--accent-blue)" fillOpacity={0.12} dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Event Details Right-Side Investigation Drawer */}
      {selectedEvent && (
        <div className="investigation-drawer">
          <div style={{
            padding: '12px 16px',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <div style={{ fontSize: '12px', fontWeight: 800, color: 'var(--text-white)', fontFamily: 'var(--font-mono)' }}>
                EVENT DETAILS
              </div>
              <div className="mono" style={{ fontSize: '11px', color: 'var(--color-info)' }}>
                {selectedEvent.id}
              </div>
            </div>
            <button 
              onClick={() => setSelectedEvent(null)}
              style={{ background: 'transparent', border: 'none', color: 'var(--text-dim)', cursor: 'pointer' }}
            >
              <X size={16} />
            </button>
          </div>

          <div style={{ padding: '16px', flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '11.5px' }}>
              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10.5px' }}>SOURCE</div>
                <div className="mono" style={{ color: 'var(--text-white)', fontWeight: 600 }}>{selectedEvent.source} / {selectedEvent.asset}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10.5px' }}>TIMESTAMP</div>
                <div className="mono" style={{ color: 'var(--text-white)' }}>{selectedEvent.time} UTC</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10.5px' }}>PROCESS</div>
                <div className="mono" style={{ color: 'var(--color-crit)' }}>{selectedEvent.process}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10.5px' }}>PARENT</div>
                <div className="mono" style={{ color: 'var(--text-muted)' }}>{selectedEvent.parent}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10.5px' }}>USER</div>
                <div className="mono" style={{ color: 'var(--text-white)' }}>{selectedEvent.user}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10.5px' }}>DESTINATION</div>
                <div className="mono" style={{ color: 'var(--color-warn)' }}>{selectedEvent.dest}</div>
              </div>
            </div>

            <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

            <div>
              <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '6px' }}>RAW EVIDENCE</div>
              <pre style={{
                backgroundColor: 'var(--bg-panel-subtle)',
                padding: '10px',
                borderRadius: '3px',
                border: '1px solid var(--border-subtle)',
                fontSize: '11px',
                fontFamily: 'var(--font-mono)',
                color: 'var(--text-white)',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all'
              }}>
                {selectedEvent.raw_evidence}
              </pre>
            </div>

            <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-white)', marginBottom: '6px' }}>CORRELATIONS</div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div>• <strong>5</strong> related telemetry events within 300s window</div>
                <div>• <strong>2</strong> related Sigma detection alerts matched</div>
                <div>• <strong>1</strong> active security incident correlated (INC-10482)</div>
              </div>
            </div>

            <div style={{ marginTop: 'auto', paddingTop: '16px' }}>
              <Link 
                href="/incidents" 
                className="btn-soc-primary" 
                style={{ width: '100%', padding: '8px', textAlign: 'center', textDecoration: 'none', display: 'block' }}
              >
                OPEN INCIDENT INVESTIGATION
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

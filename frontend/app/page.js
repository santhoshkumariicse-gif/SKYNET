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
      <div className="soc-panel" style={{ padding: '12px 16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#ffffff', letterSpacing: '0.04em', fontFamily: 'var(--font-mono)' }}>
              SKYNET COMMAND CENTER
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Autonomous SOC Command & SIEM Telemetry Correlation Grid
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>SYSTEM STATUS</div>
              <div style={{ fontSize: '11.5px', fontWeight: 700, color: 'var(--color-ok)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '8px' }}>●</span> ALL SYSTEMS OPERATIONAL
              </div>
            </div>

            <div style={{ height: '24px', width: '1px', backgroundColor: 'var(--border-subtle)' }} />

            <div>
              <div style={{ fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>LAST 24 HOURS</div>
              <div style={{ fontSize: '11.5px', fontFamily: 'var(--font-mono)', color: 'var(--text-white)' }}>
                <span style={{ fontWeight: 700 }}>12,481</span> EVENTS &nbsp;|&nbsp;
                <span style={{ fontWeight: 700, color: 'var(--color-warn)' }}>137</span> ALERTS &nbsp;|&nbsp;
                <span style={{ fontWeight: 700, color: 'var(--color-high)' }}>18</span> INCIDENTS &nbsp;|&nbsp;
                <span style={{ fontWeight: 700, color: 'var(--color-crit)' }}>4</span> CRITICAL
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 6 High-Density KPI Blocks */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px' }}>
        <div className="soc-panel" style={{ padding: '12px 14px' }}>
          <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>EVENTS (24H)</div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>12,481</div>
          <div style={{ fontSize: '10.5px', color: 'var(--color-ok)', fontFamily: 'var(--font-mono)' }}>+8.2% vs yesterday</div>
        </div>

        <div className="soc-panel" style={{ padding: '12px 14px' }}>
          <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>TOTAL ALERTS</div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--color-warn)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>137</div>
          <div style={{ fontSize: '10.5px', color: 'var(--color-ok)', fontFamily: 'var(--font-mono)' }}>-4.1% de-duplicated</div>
        </div>

        <div className="soc-panel" style={{ padding: '12px 14px' }}>
          <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>CRITICAL ALERTS</div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--color-crit)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>4</div>
          <div style={{ fontSize: '10.5px', color: 'var(--color-crit)', fontFamily: 'var(--font-mono)' }}>Active C2 / Dump</div>
        </div>

        <div className="soc-panel" style={{ padding: '12px 14px' }}>
          <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>ACTIVE INCIDENTS</div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--color-high)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>18</div>
          <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>+2 in flight</div>
        </div>

        <div className="soc-panel" style={{ padding: '12px 14px' }}>
          <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>ASSETS AT RISK</div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: '#f59e0b', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>3</div>
          <div style={{ fontSize: '10.5px', color: 'var(--color-info)', fontFamily: 'var(--font-mono)' }}>1 Isolated (HMAC)</div>
        </div>

        <div className="soc-panel" style={{ padding: '12px 14px' }}>
          <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>AUTOMATION RUNS</div>
          <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--color-info)', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>142</div>
          <div style={{ fontSize: '10.5px', color: 'var(--color-ok)', fontFamily: 'var(--font-mono)' }}>98.2% Auto-Resolved</div>
        </div>
      </div>

      {/* ACTIVE INCIDENTS (Dense Enterprise Table) */}
      <div className="soc-panel">
        <div style={{
          padding: '10px 14px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)', letterSpacing: '0.04em' }}>
            ACTIVE INCIDENTS
          </div>
          <Link href="/incidents" style={{ color: 'var(--color-info)', fontSize: '11px', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '3px' }}>
            View All ({incidents.length}) <ChevronRight size={12} />
          </Link>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="soc-table">
            <thead>
              <tr>
                <th style={{ width: '70px' }}>SEV</th>
                <th style={{ width: '130px' }}>INCIDENT</th>
                <th>TITLE / DESCRIPTION</th>
                <th style={{ width: '100px' }}>ASSET</th>
                <th style={{ width: '90px' }}>USER</th>
                <th style={{ width: '60px' }}>RISK</th>
                <th style={{ width: '80px' }}>OWNER</th>
                <th style={{ width: '110px' }}>STATUS</th>
                <th style={{ width: '90px', textAlign: 'right' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {incidents.slice(0, 5).map(inc => {
                const sev = inc.severity || 'HIGH';
                const isCrit = sev === 'CRITICAL';
                return (
                  <tr key={inc.id}>
                    <td>
                      <span className={isCrit ? 'badge-crit' : sev === 'HIGH' ? 'badge-high' : 'badge-warn'}>
                        {sev.substring(0, 4)}
                      </span>
                    </td>
                    <td className="mono" style={{ color: 'var(--color-info)', fontWeight: 600 }}>
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
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '12px' }}>
        {/* LEFT: LIVE EVENT STREAM */}
        <div className="soc-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{
            padding: '10px 14px',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
              LIVE EVENT STREAM
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '10.5px', color: 'var(--color-ok)', fontFamily: 'var(--font-mono)' }}>
              <span>STREAM ●</span>
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
                    <td className="mono" style={{ color: '#93c5fd' }}>{evt.asset}</td>
                    <td style={{ color: '#ffffff' }}>{evt.event}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* RIGHT: SECURITY ACTIVITY & AUTOMATION STATE */}
        <div className="soc-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{
            padding: '10px 14px',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
              SECURITY ACTIVITY & APPROVALS
            </div>
            <span className="badge-high" style={{ fontSize: '10px' }}>
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
                <div style={{ fontWeight: 700, color: '#ffffff' }}>
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
                <div style={{ fontWeight: 700, color: '#ffffff' }}>
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

      {/* THREAT ACTIVITY (Restrained Time-Series) */}
      <div className="soc-panel" style={{ padding: '12px 16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
            THREAT ACTIVITY TIMELINE (HOURLY INGESTION & ANOMALIES)
          </div>
          <span style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            UTC BASELINE
          </span>
        </div>
        <div style={{ height: '140px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={TIME_SERIES_DATA} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="eventGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="time" stroke="#475569" fontSize={10} tickLine={false} />
              <YAxis stroke="#475569" fontSize={10} tickLine={false} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#0d131f', 
                  borderColor: '#1e293b', 
                  borderRadius: '3px',
                  fontSize: '11px',
                  fontFamily: 'var(--font-mono)'
                }} 
              />
              <Area type="monotone" dataKey="events" stroke="#3b82f6" strokeWidth={1.5} fillOpacity={1} fill="url(#eventGrad)" />
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
              <div style={{ fontSize: '12px', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
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
                <div className="mono" style={{ color: '#ffffff', fontWeight: 600 }}>{selectedEvent.source} / {selectedEvent.asset}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10.5px' }}>TIMESTAMP</div>
                <div className="mono" style={{ color: '#ffffff' }}>{selectedEvent.time} UTC</div>
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
                <div className="mono" style={{ color: '#ffffff' }}>{selectedEvent.user}</div>
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
                {selectedEvent.raw_evidence}
              </pre>
            </div>

            <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: '#ffffff', marginBottom: '6px' }}>CORRELATIONS</div>
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

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Radio, 
  Search, 
  Filter, 
  X, 
  Play, 
  Pause, 
  ExternalLink, 
  ShieldAlert, 
  CheckCircle2,
  Terminal,
  Activity
} from 'lucide-react';
import { api } from '../lib/api';

const SEED_STREAM_EVENTS = [
  { id: 'EVT-8F291A', time: '17:24:31', source: 'AUTH', asset: 'USER-421', event: 'Failed login (4625 SubStatus 0xC000006A)', process: 'logon.exe', parent: 'winlogon.exe', user: 'user421@corp.local', dest: '10.0.4.12', raw: '{"event_id":4625,"status":"failure","reason":"bad_password","ip":"10.0.4.12"}' },
  { id: 'EVT-8F291B', time: '17:24:30', source: 'EDR', asset: 'WS-182', event: 'PowerShell spawned from winword.exe', process: 'powershell.exe', parent: 'winword.exe', user: 'finance_lead', dest: '185.220.101.5:443', raw: '{"process":"powershell.exe -NoP -NonI -W Hidden -Enc SQBFAFgA...","parent":"winword.exe"}' },
  { id: 'EVT-8F291C', time: '17:24:30', source: 'DNS', asset: 'WS-182', event: 'Query → suspicious-domain.top (URLhaus hit)', process: 'svchost.exe', parent: 'services.exe', user: 'SYSTEM', dest: '185.220.101.5', raw: '{"query":"update-microsoft-verify.top","qtype":"A","resolved":"185.220.101.5"}' },
  { id: 'EVT-8F291D', time: '17:24:29', source: 'FIREWALL', asset: 'FW-01', event: 'Outbound TCP:443 connection blocked', process: 'paloalto', parent: 'kernel', user: 'N/A', dest: '185.220.101.5:443', raw: '{"rule":"Block-Malicious-C2-Feed","src":"192.168.1.188","dst":"185.220.101.5","action":"DROP"}' },
  { id: 'EVT-8F291E', time: '17:24:28', source: 'IAM', asset: 'USER-421', event: 'MFA challenge failed 3x in 60s', process: 'okta-verify', parent: 'system', user: 'user421@corp.local', dest: '10.0.4.12', raw: '{"mfa_method":"push","status":"rejected","origin_geo":"RU","latency_ms":120}' },
  { id: 'EVT-8F291F', time: '17:24:21', source: 'EDR', asset: 'DC-02', event: 'LSASS memory dumping via procdump64', process: 'procdump64.exe', parent: 'cmd.exe', user: 'SYSTEM', dest: 'LOCAL', raw: '{"cmdline":"procdump64.exe -ma lsass.exe C:\\Windows\\Temp\\lsass.dmp"}' },
  { id: 'EVT-8F2920', time: '17:24:15', source: 'EDR', asset: 'SRV-14', event: 'Volume shadow deletion via vssadmin', process: 'vssadmin.exe', parent: 'powershell.exe', user: 'SYSTEM', dest: 'LOCAL', raw: '{"cmdline":"vssadmin.exe delete shadows /all /quiet"}' },
  { id: 'EVT-8F2921', time: '17:24:10', source: 'SYSMON', asset: 'WS-184', event: 'Registry Run key persistence injected', process: 'reg.exe', parent: 'powershell.exe', user: 'SYSTEM', dest: 'HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run', raw: '{"key":"HKLM\\\\Run\\\\Updater","val":"C:\\\\Windows\\\\Temp\\\\updater.exe"}' },
  { id: 'EVT-8F2922', time: '17:24:02', source: 'EDR', asset: 'WS-184', event: 'AMSI bypass memory patching detected', process: 'powershell.exe', parent: 'explorer.exe', user: 'finance_lead', dest: 'LOCAL', raw: '{"technique":"AmsiScanBuffer patch","bytes":"0x48, 0x31, 0xC0, 0xC3"}' },
  { id: 'EVT-8F2923', time: '17:23:55', source: 'NETFLOW', asset: 'GW-CORE', event: 'Port scan burst on internal subnet 192.168.1.0/24', process: 'kernel', parent: 'system', user: 'N/A', dest: '192.168.1.0/24:445', raw: '{"ports":[445, 139, 3389],"packets_per_sec":840,"verdict":"SCAN"}' }
];

export default function LiveMonitorPage() {
  const [events, setEvents] = useState(SEED_STREAM_EVENTS);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [filterSource, setFilterSource] = useState('ALL');
  const [search, setSearch] = useState('');
  const [isPaused, setIsPaused] = useState(false);
  const [wsLive, setWsLive] = useState(false);

  useEffect(() => {
    let ws;
    try {
      ws = new WebSocket('ws://localhost:8000/api/v1/ws/live-events');
      ws.onopen = () => setWsLive(true);
      ws.onclose = () => setWsLive(false);
      ws.onmessage = (e) => {
        if (isPaused) return;
        try {
          const msg = JSON.parse(e.data);
          if (msg.event) {
            setEvents(prev => [msg.event, ...prev.slice(0, 49)]);
          }
        } catch {}
      };
    } catch {
      setWsLive(false);
    }

    return () => {
      if (ws) ws.close();
    };
  }, [isPaused]);

  const filtered = events.filter(e => {
    const matchSrc = filterSource === 'ALL' || e.source === filterSource;
    const matchSearch = !search || 
      e.id.toLowerCase().includes(search.toLowerCase()) ||
      e.asset.toLowerCase().includes(search.toLowerCase()) ||
      e.event.toLowerCase().includes(search.toLowerCase()) ||
      e.user.toLowerCase().includes(search.toLowerCase());
    return matchSrc && matchSearch;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {/* Top Header Bar */}
      <div className="soc-panel" style={{ padding: '10px 16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Radio size={15} color="var(--color-ok)" /> LIVE MONITOR
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Real-time normalized security event stream directly from endpoint agents and perimeter firewalls.
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              color: isPaused ? 'var(--color-warn)' : 'var(--color-ok)',
            }}>
              <span>●</span>
              <span>{isPaused ? 'STREAM PAUSED' : wsLive ? 'STREAM LIVE (WEBSOCKET)' : 'STREAM BUFFERED'}</span>
            </div>

            <button 
              onClick={() => setIsPaused(!isPaused)} 
              className="btn-soc"
              style={{ padding: '4px 10px', fontSize: '11px' }}
            >
              {isPaused ? <Play size={12} /> : <Pause size={12} />}
              {isPaused ? 'RESUME STREAM' : 'PAUSE'}
            </button>
          </div>
        </div>
      </div>

      {/* Filter and Query Bar */}
      <div className="soc-panel" style={{ padding: '8px 12px', display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          backgroundColor: 'var(--bg-base)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '3px',
          padding: '4px 8px',
          flex: 1,
          minWidth: '240px'
        }}>
          <Search size={13} color="var(--text-dim)" />
          <input 
            type="text" 
            placeholder="Filter by event ID, asset, user, process..."
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

        {/* Source Pills */}
        <div style={{ display: 'flex', gap: '4px' }}>
          {['ALL', 'EDR', 'AUTH', 'DNS', 'FIREWALL', 'IAM', 'SYSMON'].map(src => (
            <button
              key={src}
              onClick={() => setFilterSource(src)}
              style={{
                padding: '3px 8px',
                fontSize: '10.5px',
                fontFamily: 'var(--font-mono)',
                borderRadius: '3px',
                border: '1px solid',
                borderColor: filterSource === src ? 'var(--color-info)' : 'var(--border-subtle)',
                backgroundColor: filterSource === src ? 'var(--color-info-bg)' : 'transparent',
                color: filterSource === src ? 'var(--color-info)' : 'var(--text-muted)',
                cursor: 'pointer'
              }}
            >
              {src}
            </button>
          ))}
        </div>

        <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
          {filtered.length} events buffered
        </div>
      </div>

      {/* Dense Live Stream Table */}
      <div className="soc-panel" style={{ overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto', maxHeight: 'calc(100vh - 240px)', overflowY: 'auto' }}>
          <table className="soc-table">
            <thead>
              <tr>
                <th style={{ width: '80px' }}>TIME</th>
                <th style={{ width: '90px' }}>SOURCE</th>
                <th style={{ width: '100px' }}>ASSET</th>
                <th>EVENT ACTIVITY</th>
                <th style={{ width: '120px' }}>PROCESS</th>
                <th style={{ width: '120px' }}>USER</th>
                <th style={{ width: '130px' }}>DESTINATION</th>
                <th style={{ width: '80px', textAlign: 'right' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(evt => (
                <tr 
                  key={evt.id}
                  onClick={() => setSelectedEvent(evt)}
                  style={{
                    cursor: 'pointer',
                    backgroundColor: selectedEvent?.id === evt.id ? 'var(--bg-panel-active)' : 'transparent'
                  }}
                >
                  <td className="mono" style={{ color: 'var(--text-dim)' }}>{evt.time}</td>
                  <td>
                    <span className="badge-subtle" style={{ fontSize: '10px' }}>{evt.source}</span>
                  </td>
                  <td className="mono" style={{ color: '#93c5fd', fontWeight: 600 }}>{evt.asset}</td>
                  <td style={{ color: '#ffffff', fontWeight: 500 }}>{evt.event}</td>
                  <td className="mono" style={{ color: 'var(--color-crit)' }}>{evt.process}</td>
                  <td className="mono" style={{ color: 'var(--text-muted)' }}>{evt.user}</td>
                  <td className="mono" style={{ color: 'var(--color-warn)' }}>{evt.dest}</td>
                  <td style={{ textAlign: 'right' }}>
                    <button 
                      onClick={(e) => { e.stopPropagation(); setSelectedEvent(evt); }}
                      className="btn-soc" 
                      style={{ padding: '2px 6px', fontSize: '10.5px' }}
                    >
                      INSPECT
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Contextual Right-Side Investigation Drawer */}
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
                <div style={{ color: 'var(--text-dim)', fontSize: '10.5px' }}>PARENT PROCESS</div>
                <div className="mono" style={{ color: 'var(--text-muted)' }}>{selectedEvent.parent}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10.5px' }}>USER IDENTITY</div>
                <div className="mono" style={{ color: '#ffffff' }}>{selectedEvent.user}</div>
              </div>
              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10.5px' }}>DESTINATION</div>
                <div className="mono" style={{ color: 'var(--color-warn)' }}>{selectedEvent.dest}</div>
              </div>
            </div>

            <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

            <div>
              <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '6px' }}>RAW TELEMETRY EVIDENCE</div>
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
                {selectedEvent.raw}
              </pre>
            </div>

            <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

            <div>
              <div style={{ fontSize: '11px', fontWeight: 700, color: '#ffffff', marginBottom: '6px' }}>CORRELATIONS</div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '5px' }}>
                <div>• <strong>5</strong> related events in same session</div>
                <div>• <strong>2</strong> related Sigma detection alerts</div>
                <div>• <strong>1</strong> active incident (INC-10482)</div>
              </div>
            </div>

            <div style={{ marginTop: 'auto', paddingTop: '16px' }}>
              <Link 
                href="/incidents" 
                className="btn-soc-primary" 
                style={{ width: '100%', padding: '8px', textAlign: 'center', textDecoration: 'none', display: 'block' }}
              >
                OPEN INVESTIGATION
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

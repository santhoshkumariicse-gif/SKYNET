'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Shield, 
  Activity, 
  AlertTriangle, 
  Briefcase, 
  Sparkles, 
  Send, 
  Server, 
  TrendingUp, 
  CheckCircle2, 
  ArrowRight,
  RefreshCw,
  Cpu,
  Bot
} from 'lucide-react';

export default function ExecutiveDashboardPage() {
  const [healthData, setHealthData] = useState(null);
  const [trends, setTrends] = useState(null);
  const [copilotQuery, setCopilotQuery] = useState('');
  const [copilotHistory, setCopilotHistory] = useState([
    {
      sender: 'copilot',
      text: 'Good morning, Commander. I am monitoring 48 fleet infrastructure endpoints across Windows PCs, servers, and Android edge layers. All core systems are operating with a composite Fleet Health score of 88%. Ask me anything regarding fleet anomalies, capacity bottlenecks, or incident causes.'
    }
  ]);
  const [copilotLoading, setCopilotLoading] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [hRes, tRes] = await Promise.all([
        fetch('http://localhost:8000/health-score'),
        fetch('http://localhost:8000/metrics/trends?range=24h')
      ]);
      if (hRes.ok) setHealthData(await hRes.json());
      if (tRes.ok) setTrends(await tRes.json());
    } catch (e) {
      console.error('Failed to load executive stats:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleCopilotSubmit = async (e) => {
    e?.preventDefault();
    if (!copilotQuery.trim() || copilotLoading) return;

    const userText = copilotQuery;
    setCopilotHistory(prev => [...prev, { sender: 'user', text: userText }]);
    setCopilotQuery('');
    setCopilotLoading(true);

    try {
      const res = await fetch('http://localhost:8000/copilot/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userText })
      });
      if (res.ok) {
        const data = await res.json();
        setCopilotHistory(prev => [...prev, { 
          sender: 'copilot', 
          text: data.answer,
          intent: data.intent,
          followups: data.suggested_followups
        }]);
      }
    } catch (err) {
      setCopilotHistory(prev => [...prev, { 
        sender: 'copilot', 
        text: 'Apologies, I encountered an error querying the fleet database.' 
      }]);
    } finally {
      setCopilotLoading(false);
    }
  };

  const riskIndex = trends ? Math.round(100 - (trends.fleet_health_score || 88)) : 14;

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', color: 'var(--text-muted)' }}>
      {/* Top Banner */}
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
            <Sparkles size={22} style={{ color: 'var(--accent-blue)' }} />
            Executive Leadership & AI Command Center
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginTop: '4px', fontFamily: 'var(--font-body)' }}>
            High-level infrastructure posture, predictive risk analysis, and generative Copilot insights.
          </p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="btn-soc"
          style={{ padding: '8px 14px' }}
        >
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
          <span>Refresh Briefing</span>
        </button>
      </div>

      {/* 4 Executive KPI Cards (28–32px numbers, 6px radius, subtle shadow) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px', marginBottom: '20px' }}>
        {/* Fleet Health */}
        <div className="soc-card" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)', fontSize: '11px', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>
            <span>FLEET HEALTH INDEX</span>
            <Activity size={16} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div className="kpi-number" style={{ color: 'var(--accent-green)', marginTop: '8px' }}>
            {healthData?.fleet_health_score ?? 88}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
            {healthData?.status_distribution?.healthy ?? 42} Healthy / {healthData?.total_monitored ?? 48} Supervised
          </div>
        </div>

        {/* Infrastructure Risk Index */}
        <div className="soc-card" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)', fontSize: '11px', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>
            <span>INFRASTRUCTURE RISK INDEX</span>
            <AlertTriangle size={16} style={{ color: riskIndex > 25 ? 'var(--accent-red)' : 'var(--accent-amber)' }} />
          </div>
          <div className="kpi-number" style={{ color: riskIndex > 25 ? 'var(--accent-red)' : 'var(--accent-amber)', marginTop: '8px' }}>
            {riskIndex}/100
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
            Calculated across resource stress & active anomalies
          </div>
        </div>

        {/* Active Incidents */}
        <div className="soc-card" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)', fontSize: '11px', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>
            <span>OPEN DEFENSE CASES</span>
            <Briefcase size={16} style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div className="kpi-number" style={{ color: 'var(--text-white)', marginTop: '8px' }}>
            1
          </div>
          <div style={{ fontSize: '11px', color: 'var(--accent-blue)', marginTop: '4px' }}>
            INC-2026-0001 (Cobalt Strike Ingress)
          </div>
        </div>

        {/* Autonomous Mitigations */}
        <div className="soc-card" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)', fontSize: '11px', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>
            <span>AUTONOMOUS ACTIONS</span>
            <Shield size={16} style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div className="kpi-number" style={{ color: 'var(--accent-blue)', marginTop: '8px' }}>
            98.2%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>
            SOAR auto-containment rate
          </div>
        </div>
      </div>

      {/* Main 2-Column Content: Left = Incidents & Recommendations, Right = AI Copilot */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '16px' }}>
        
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Priority Incidents */}
          <div className="soc-card" style={{ padding: '18px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-white)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-heading)' }}>
              <Briefcase size={16} style={{ color: 'var(--accent-red)' }} /> Priority Infrastructure Incidents
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ backgroundColor: 'var(--bg-panel-subtle)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="badge-critical">CRITICAL DEFCON 2</span>
                  <span className="mono" style={{ fontSize: '11px', color: 'var(--text-dim)' }}>INC-2026-0001</span>
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-white)', marginTop: '8px', fontFamily: 'var(--font-heading)' }}>
                  Cobalt Strike Beacon Infiltration & Credential Dumping
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px', lineHeight: '1.4' }}>
                  Impacted host: FIN-LAPTOP-042 (192.168.1.188). Autonomous Tier-1 AI investigated obfuscated PowerShell cradle and Procdump LSASS dump.
                </p>
                <div style={{ marginTop: '10px', display: 'flex', gap: '8px' }}>
                  <Link href="/incidents" style={{ color: 'var(--accent-blue)', fontSize: '12px', fontWeight: 600, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px', fontFamily: 'var(--font-heading)' }}>
                    Review Evidence Dossier <ArrowRight size={12} />
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* AI Strategic Recommendations */}
          <div className="soc-card" style={{ padding: '18px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-white)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-heading)' }}>
              <Sparkles size={16} style={{ color: 'var(--accent-blue)' }} /> AI Proactive Recommendations
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ backgroundColor: 'var(--bg-panel-subtle)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span className="badge-high">STORAGE PRESSURE</span>
                  <span style={{ fontSize: '12.5px', fontWeight: 600, color: 'var(--text-white)' }}>DC-PRIMARY-01 write threshold breach</span>
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  System volume C: at 88.4% capacity. Recommend rotating Windows Event Forwarding logs or provisioning 50GB storage.
                </p>
              </div>

              <div style={{ backgroundColor: 'var(--bg-panel-subtle)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span className="badge-medium">MEMORY SATURATION</span>
                  <span style={{ fontSize: '12.5px', fontWeight: 600, color: 'var(--text-white)' }}>DEV-BUILD-RUNNER RAM sustained &gt;89%</span>
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Docker worker processes causing potential memory starvation. Auto-restart policy suggested.
                </p>
              </div>

              <div style={{ backgroundColor: 'var(--bg-panel-subtle)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span className="badge-info">LATENCY OPTIMIZATION</span>
                  <span style={{ fontSize: '12.5px', fontWeight: 600, color: 'var(--text-white)' }}>CORP-GATEWAY-FW ingress variance</span>
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Network baseline shows +14% weekend surge. Consider traffic shaping during backup windows.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: AI Infrastructure Copilot (Enterprise RAG) */}
        <div className="soc-card" style={{ padding: '18px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '10px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-white)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0, fontFamily: 'var(--font-heading)' }}>
              <Bot size={18} style={{ color: 'var(--accent-blue)' }} /> AI Infrastructure Copilot
            </h2>
            <span className="badge-low" style={{ fontSize: '10px' }}>RAG ACTIVE</span>
          </div>

          {/* Quick Prompts */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '12px' }}>
            {[
              "Why is TEST-RIG-01 slow?",
              "Show unhealthy devices.",
              "Which devices need attention?"
            ].map(q => (
              <button
                key={q}
                onClick={() => { setCopilotQuery(q); }}
                style={{
                  backgroundColor: 'var(--bg-panel-subtle)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-muted)',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  cursor: 'pointer',
                  fontFamily: 'var(--font-body)',
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--accent-blue)'; e.currentTarget.style.color = 'var(--accent-blue)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border-subtle)'; e.currentTarget.style.color = 'var(--text-muted)'; }}
              >
                "{q}"
              </button>
            ))}
          </div>

          {/* Chat History Box */}
          <div style={{ 
            flex: 1, 
            minHeight: '340px', 
            maxHeight: '440px', 
            overflowY: 'auto', 
            backgroundColor: 'var(--bg-panel-subtle)', 
            border: '1px solid var(--border-subtle)', 
            borderRadius: '6px', 
            padding: '12px', 
            display: 'flex', 
            flexDirection: 'column', 
            gap: '10px',
            marginBottom: '12px'
          }}>
            {copilotHistory.map((msg, idx) => (
              <div 
                key={idx} 
                style={{ 
                  alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '88%',
                  backgroundColor: msg.sender === 'user' ? 'var(--accent-blue)' : 'var(--bg-panel)',
                  color: msg.sender === 'user' ? '#FFFFFF' : 'var(--text-white)',
                  padding: '10px 12px',
                  borderRadius: '6px',
                  border: msg.sender === 'user' ? 'none' : '1px solid var(--border-subtle)',
                  fontSize: '12.5px',
                  lineHeight: '1.45',
                  boxShadow: 'var(--card-shadow)'
                }}
              >
                {msg.sender === 'copilot' && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '4px', color: 'var(--accent-blue)', fontSize: '11px', fontWeight: 700, fontFamily: 'var(--font-heading)' }}>
                    <Bot size={13} /> SKYNET INTELLIGENCE
                  </div>
                )}
                <div style={{ whiteSpace: 'pre-wrap' }}>
                  {msg.text}
                </div>
                {msg.followups && msg.followups.length > 0 && (
                  <div style={{ marginTop: '8px', borderTop: '1px solid var(--border-subtle)', paddingTop: '6px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {msg.followups.map((f, i) => (
                      <span 
                        key={i} 
                        onClick={() => { setCopilotQuery(f); }}
                        style={{ fontSize: '10.5px', color: 'var(--accent-blue)', cursor: 'pointer', textDecoration: 'underline' }}
                      >
                        → {f}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {copilotLoading && (
              <div style={{ alignSelf: 'flex-start', backgroundColor: 'var(--bg-panel)', color: 'var(--text-dim)', padding: '8px 12px', borderRadius: '6px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '8px', border: '1px solid var(--border-subtle)' }}>
                <RefreshCw size={12} className="animate-spin" />
                Querying fleet vector database & analyzing telemetry...
              </div>
            )}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleCopilotSubmit} style={{ display: 'flex', gap: '8px' }}>
            <input
              type="text"
              placeholder="Ask Copilot about any host, incident, or metric..."
              value={copilotQuery}
              onChange={(e) => setCopilotQuery(e.target.value)}
              className="soc-input"
              style={{ flex: 1 }}
            />
            <button
              type="submit"
              disabled={copilotLoading}
              className="btn-soc btn-soc-primary"
              style={{ padding: '0 16px' }}
            >
              <Send size={14} />
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}

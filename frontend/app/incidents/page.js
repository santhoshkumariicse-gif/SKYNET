'use client';

import { useState, useEffect } from 'react';
import { 
  FileWarning, 
  Terminal, 
  Clock, 
  ShieldCheck, 
  Cpu, 
  Zap, 
  Lock, 
  Copy, 
  Check, 
  Sparkles, 
  Activity,
  Layers,
  Fingerprint,
  RotateCw
} from 'lucide-react';
import { api } from '../lib/api';

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [investigating, setInvestigating] = useState(false);
  const [copiedHash, setCopiedHash] = useState(null);
  const [containmentMsg, setContainmentMsg] = useState(null);

  useEffect(() => {
    loadIncidents();
  }, []);

  async function loadIncidents() {
    try {
      const data = await api.getIncidents();
      setIncidents(data);
      if (data.length > 0) {
        selectIncident(data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function selectIncident(inc) {
    setSelectedIncident(inc);
    try {
      const tData = await api.getIncidentTimeline(inc.id);
      setTimeline(tData.timeline || []);
    } catch {
      setTimeline([]);
    }
  }

  const handleReInvestigate = async () => {
    if (!selectedIncident) return;
    setInvestigating(true);
    try {
      const dossier = await api.triggerInvestigation(selectedIncident.id);
      setSelectedIncident(prev => ({
        ...prev,
        ai_summary: dossier.summary || prev.ai_summary,
        verdict: dossier.verdict || prev.verdict,
        ai_recommended_action: dossier.containment_plan || prev.ai_recommended_action
      }));
      if (dossier.timeline) {
        setTimeline(dossier.timeline);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setInvestigating(false);
    }
  };

  const handleUpdateVerdict = async (verdict) => {
    if (!selectedIncident) return;
    try {
      await api.updateIncident(selectedIncident.id, { verdict });
      setSelectedIncident(prev => ({ ...prev, verdict }));
      setIncidents(prev => prev.map(i => i.id === selectedIncident.id ? { ...i, verdict } : i));
    } catch (err) {
      console.error(err);
    }
  };

  const handleExecuteContainment = async () => {
    try {
      const res = await api.executeContainment({
        action_type: 'ISOLATE_HOST',
        target_identifier: 'FIN-LAPTOP-042',
        reason: 'Automated containment dispatched from AI Incident Dossier',
        rollback_plan: 'SOC manual verification required'
      });
      setContainmentMsg(`Containment Executed! HMAC Verified: ${res.signed_token?.substring(0, 18)}...`);
      setTimeout(() => setContainmentMsg(null), 6000);
    } catch {
      setContainmentMsg('Containment failed.');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(text);
    setTimeout(() => setCopiedHash(null), 2500);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ffffff', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileWarning size={22} color="var(--amber)" /> Autonomous Incident Cases & AI Dossier
          </h1>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '4px' }}>
            Multi-stage attack correlation, causality timeline builder, and automated executive triage reports.
          </p>
        </div>

        {selectedIncident && (
          <button 
            className="btn btn-primary"
            onClick={handleReInvestigate}
            disabled={investigating}
          >
            <RotateCw size={14} className={investigating ? 'animate-spin' : ''} />
            {investigating ? 'AI Agent Reasoning in Progress...' : 'Run AI Re-Investigation'}
          </button>
        )}
      </div>

      {containmentMsg && (
        <div style={{
          padding: '12px 18px',
          borderRadius: '8px',
          backgroundColor: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          color: '#6ee7b7',
          fontSize: '0.82rem',
          fontFamily: 'var(--font-mono)'
        }}>
          {containmentMsg}
        </div>
      )}

      {/* Main Grid: Incident Selector + Deep Dossier View */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '20px' }}>
        {/* Incident Case Selector */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>
            TRACKED CASES ({incidents.length})
          </div>

          {incidents.map((inc) => {
            const isSelected = selectedIncident?.id === inc.id;
            return (
              <div
                key={inc.id}
                onClick={() => selectIncident(inc)}
                className="glass-panel"
                style={{
                  padding: '14px',
                  cursor: 'pointer',
                  borderColor: isSelected ? 'var(--cyan)' : 'var(--border-subtle)',
                  backgroundColor: isSelected ? 'rgba(0, 240, 255, 0.08)' : 'var(--bg-card)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--cyan)' }}>
                    {inc.incident_number}
                  </span>
                  <span className={`badge badge-${inc.severity?.toLowerCase()}`}>
                    {inc.severity}
                  </span>
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#ffffff', marginBottom: '6px', lineHeight: '1.3' }}>
                  {inc.title}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                  <span>Status: <strong style={{ color: '#ffffff' }}>{inc.status}</strong></span>
                  <span className="badge badge-cyan" style={{ fontSize: '0.62rem' }}>{inc.verdict}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Selected Incident Deep Dossier */}
        {selectedIncident ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Incident Header Card */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '14px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.82rem', fontFamily: 'var(--font-mono)', color: 'var(--cyan)', fontWeight: 700 }}>
                      {selectedIncident.incident_number}
                    </span>
                    <span className={`badge badge-${selectedIncident.severity?.toLowerCase()}`}>
                      {selectedIncident.severity}
                    </span>
                    <span className="badge badge-cyan">
                      {selectedIncident.status}
                    </span>
                  </div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#ffffff' }}>
                    {selectedIncident.title}
                  </h2>
                </div>

                {/* Verdict Picker */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>VERDICT:</span>
                  {['TRUE_POSITIVE', 'FALSE_POSITIVE', 'BENIGN'].map((v) => (
                    <button
                      key={v}
                      className="btn"
                      onClick={() => handleUpdateVerdict(v)}
                      style={{
                        padding: '4px 10px',
                        fontSize: '0.72rem',
                        backgroundColor: selectedIncident.verdict === v ? 'var(--cyan)' : 'rgba(255, 255, 255, 0.05)',
                        color: selectedIncident.verdict === v ? '#000000' : 'var(--text-main)',
                        fontWeight: 700
                      }}
                    >
                      {v.replace('_', ' ')}
                    </button>
                  ))}
                </div>
              </div>

              <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: '1.5', marginBottom: '20px' }}>
                {selectedIncident.description}
              </p>

              {/* AI Tier-1 Analyst Findings Card */}
              <div style={{
                borderRadius: '8px',
                border: '1px solid rgba(0, 240, 255, 0.35)',
                backgroundColor: 'rgba(0, 240, 255, 0.04)',
                padding: '18px',
                display: 'flex',
                flexDirection: 'column',
                gap: '14px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={18} color="var(--cyan)" />
                  <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#ffffff', letterSpacing: '0.04em' }}>
                    AUTONOMOUS TIER-1 AI SOC ANALYST DOSSIER
                  </span>
                </div>

                <div>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--cyan)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Executive Summary:
                  </div>
                  <div style={{ fontSize: '0.84rem', color: '#f1f5f9', lineHeight: '1.4' }}>
                    {selectedIncident.ai_summary || 'Analysis pending.'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--cyan)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Root Cause Analysis:
                  </div>
                  <div style={{ fontSize: '0.84rem', color: '#f1f5f9', lineHeight: '1.4' }}>
                    {selectedIncident.ai_root_cause || 'Root cause identification running...'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--emerald)', fontFamily: 'var(--font-mono)', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Recommended Active Containment Plan:
                  </div>
                  <div style={{ fontSize: '0.84rem', color: '#6ee7b7', lineHeight: '1.4', whiteSpace: 'pre-line' }}>
                    {selectedIncident.ai_recommended_action || '1. Isolate target endpoint\n2. Block C2 IP address at firewall'}
                  </div>
                </div>

                <div style={{ paddingTop: '6px' }}>
                  <button 
                    className="btn btn-danger"
                    onClick={handleExecuteContainment}
                  >
                    <Lock size={15} /> Execute Containment Plan Now (SOAR Active Defense)
                  </button>
                </div>
              </div>
            </div>

            {/* Attack Causality Timeline */}
            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                <Clock size={18} color="var(--cyan)" />
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>
                  Interactive Attack Causality Timeline
                </h3>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', position: 'relative', paddingLeft: '24px' }}>
                {/* Timeline vertical line */}
                <div style={{
                  position: 'absolute',
                  left: '7px',
                  top: '6px',
                  bottom: '6px',
                  width: '2px',
                  backgroundColor: 'rgba(0, 240, 255, 0.3)'
                }}></div>

                {timeline.map((step, idx) => (
                  <div key={idx} style={{ position: 'relative' }}>
                    {/* Node Dot */}
                    <div style={{
                      position: 'absolute',
                      left: '-21px',
                      top: '4px',
                      width: '10px',
                      height: '10px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--cyan)',
                      boxShadow: '0 0 8px var(--cyan)'
                    }}></div>

                    <div style={{
                      padding: '12px 14px',
                      borderRadius: '6px',
                      backgroundColor: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid var(--border-subtle)'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '0.72rem', color: 'var(--cyan)', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
                            {step.timestamp}
                          </span>
                          <span className="badge badge-cyan" style={{ fontSize: '0.62rem' }}>
                            {step.stage || 'Event'}
                          </span>
                        </div>
                        {step.severity && (
                          <span className={`badge badge-${step.severity?.toLowerCase()}`}>
                            {step.severity}
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#ffffff' }}>
                        {step.title || step.description}
                      </div>
                      {step.title && step.description && (
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                          {step.description}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Forensic Evidence Locker */}
            <div className="glass-panel" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                <Fingerprint size={18} color="var(--purple)" />
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>
                  Forensic Evidence Locker
                </h3>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {selectedIncident.evidence?.map((ev) => (
                  <div 
                    key={ev.id}
                    style={{
                      padding: '14px',
                      borderRadius: '6px',
                      backgroundColor: 'rgba(0, 0, 0, 0.45)',
                      border: '1px solid var(--border-subtle)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>
                        {ev.evidence_type}
                      </span>
                      {ev.hash_sha256 && (
                        <button
                          className="btn btn-ghost"
                          style={{ padding: '2px 8px', fontSize: '0.7rem' }}
                          onClick={() => copyToClipboard(ev.hash_sha256)}
                        >
                          {copiedHash === ev.hash_sha256 ? <Check size={12} color="var(--emerald)" /> : <Copy size={12} />}
                          Copy SHA-256
                        </button>
                      )}
                    </div>

                    <div style={{ fontSize: '0.8rem', color: '#e2e8f0', marginBottom: '8px' }}>
                      {ev.notes}
                    </div>

                    {ev.hash_sha256 && (
                      <div style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', color: 'var(--cyan)', wordBreak: 'break-all', marginBottom: '8px' }}>
                        SHA256: {ev.hash_sha256}
                      </div>
                    )}

                    <pre className="code-block" style={{ maxHeight: '120px', fontSize: '0.72rem' }}>
                      {JSON.stringify(ev.raw_payload, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-dim)' }}>
            Select an incident case to inspect the AI investigation dossier.
          </div>
        )}
      </div>
    </div>
  );
}

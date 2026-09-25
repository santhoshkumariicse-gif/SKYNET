'use client';

import { useState, useEffect } from 'react';
import { 
  Grid3X3, 
  ShieldCheck, 
  Crosshair, 
  CheckCircle2, 
  AlertTriangle, 
  Layers,
  Activity
} from 'lucide-react';
import { api } from '../lib/api';

export default function MitrePage() {
  const [coverage, setCoverage] = useState(null);
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMitre() {
      try {
        const [cov, det] = await Promise.all([
          api.getMitreCoverage(),
          api.getMitreDetections()
        ]);
        setCoverage(cov);
        setDetections(det.observed_techniques || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadMitre();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Title */}
      <div>
        <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ffffff', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Grid3X3 size={22} color="var(--purple)" /> MITRE ATT&CK® Enterprise Matrix Coverage
        </h1>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '4px' }}>
          Real-time detection rule mapping against the MITRE ATT&CK Enterprise v15 framework.
        </p>
      </div>

      {/* Coverage KPI Header */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Overall Coverage</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--cyan)', fontFamily: 'var(--font-mono)' }}>
            {coverage?.overall_coverage_pct || 85.0}%
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--emerald)' }}>17 of 20 Tracked Techniques Covered</div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Observed in Live SOC</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--crimson)', fontFamily: 'var(--font-mono)' }}>
            {detections.length}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#fca5a5' }}>Active Attack Techniques Observed</div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Tactics Covered</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#c084fc', fontFamily: 'var(--font-mono)' }}>
            10 / 12
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Initial Access through Impact</div>
        </div>
      </div>

      {/* Live Observed Techniques Stream */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
          <Activity size={18} color="var(--crimson)" />
          <h2 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>
            Actively Observed Techniques in Endpoint Stream
          </h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px' }}>
          {detections.map((det) => (
            <div 
              key={det.technique_id}
              style={{
                padding: '12px 14px',
                borderRadius: '6px',
                backgroundColor: 'rgba(239, 68, 68, 0.08)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', fontWeight: 800, color: '#fca5a5' }}>
                    {det.technique_id}
                  </span>
                  <span style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>
                    [{det.tactic}]
                  </span>
                </div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#ffffff', marginTop: '2px' }}>
                  {det.technique_name}
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <span className="badge badge-critical">
                  {det.alert_count} Alerts
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Enterprise Tactics Matrix Grid */}
      <div className="glass-panel" style={{ padding: '20px' }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '16px' }}>
          MITRE ATT&CK Matrix Tactic Columns
        </h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '16px',
          alignItems: 'start'
        }}>
          {coverage && Object.entries(coverage.tactics).map(([tacticName, tInfo]) => (
            <div 
              key={tacticName}
              style={{
                borderRadius: '8px',
                border: '1px solid var(--border-subtle)',
                backgroundColor: 'rgba(15, 23, 42, 0.5)',
                overflow: 'hidden'
              }}
            >
              <div style={{
                padding: '10px 12px',
                backgroundColor: 'rgba(255, 255, 255, 0.04)',
                borderBottom: '1px solid var(--border-subtle)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#ffffff' }}>
                  {tacticName}
                </div>
                <span className="badge badge-cyan" style={{ fontSize: '0.62rem' }}>
                  {tInfo.coverage_pct}%
                </span>
              </div>

              <div style={{ padding: '10px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {tInfo.techniques && Object.entries(tInfo.techniques).map(([tid, tech]) => (
                  <div
                    key={tid}
                    style={{
                      padding: '8px 10px',
                      borderRadius: '4px',
                      backgroundColor: tech.covered ? 'rgba(0, 240, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                      border: tech.covered ? '1px solid rgba(0, 240, 255, 0.25)' : '1px solid rgba(255, 255, 255, 0.05)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '2px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.72rem', fontFamily: 'var(--font-mono)', fontWeight: 700, color: tech.covered ? 'var(--cyan)' : 'var(--text-dim)' }}>
                        {tid}
                      </span>
                      {tech.covered && <CheckCircle2 size={12} color="var(--cyan)" />}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: tech.covered ? '#ffffff' : 'var(--text-dim)', fontWeight: 500 }}>
                      {tech.name}
                    </div>
                    {tech.rule && (
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                        Rule: {tech.rule}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

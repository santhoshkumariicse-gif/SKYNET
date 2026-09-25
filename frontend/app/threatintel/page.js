'use client';

import { useState, useEffect } from 'react';
import { 
  Search, 
  ShieldAlert, 
  ExternalLink, 
  CheckCircle, 
  AlertTriangle, 
  Database, 
  Globe, 
  Tag,
  Crosshair
} from 'lucide-react';
import { api } from '../lib/api';

export default function ThreatIntelPage() {
  const [iocType, setIocType] = useState('IP');
  const [iocValue, setIocValue] = useState('185.220.101.5');
  const [lookupResult, setLookupResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [iocsList, setIocsList] = useState([]);

  useEffect(() => {
    loadIOCs();
  }, []);

  async function loadIOCs() {
    try {
      const data = await api.listIOCs();
      setIocsList(data);
    } catch (err) {
      console.error(err);
    }
  }

  const handleLookup = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const res = await api.lookupIOC(iocType, iocValue.trim());
      setLookupResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const setPreset = (type, val) => {
    setIocType(type);
    setIocValue(val);
    setTimeout(() => {
      api.lookupIOC(type, val).then(setLookupResult);
    }, 50);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Title */}
      <div>
        <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ffffff', letterSpacing: '0.04em', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Search size={22} color="var(--cyan)" /> Threat Intelligence Platform (TIP)
        </h1>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '4px' }}>
          Global threat correlation across VirusTotal, AbuseIPDB, and URLhaus with automated Redis IOC caching.
        </p>
      </div>

      {/* Global Threat Feeds Status */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        <div className="glass-panel" style={{ padding: '16px', display: 'flex', alignItems: 'center', gap: '14px' }}>
          <Globe size={24} color="var(--cyan)" />
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffffff' }}>VirusTotal v3 API</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--emerald)' }}>Connected // SHA256 & URL Engine</div>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '16px', display: 'flex', alignItems: 'center', gap: '14px' }}>
          <ShieldAlert size={24} color="var(--amber)" />
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffffff' }}>AbuseIPDB v2 API</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--emerald)' }}>Connected // IPv4 Reputation Scoring</div>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '16px', display: 'flex', alignItems: 'center', gap: '14px' }}>
          <Database size={24} color="var(--purple)" />
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#ffffff' }}>URLhaus Feed</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--emerald)' }}>Synchronized // Active Malware URLs</div>
          </div>
        </div>
      </div>

      {/* Live Lookup Bar & Results */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '8px' }}>
          Live Indicator of Compromise (IOC) Lookup
        </div>

        {/* Quick Presets */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>PRESETS:</span>
          <button 
            type="button" 
            className="btn btn-ghost" 
            style={{ fontSize: '0.7rem', padding: '3px 8px' }}
            onClick={() => setPreset('IP', '185.220.101.5')}
          >
            Cobalt Strike IP
          </button>
          <button 
            type="button" 
            className="btn btn-ghost" 
            style={{ fontSize: '0.7rem', padding: '3px 8px' }}
            onClick={() => setPreset('SHA256', '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f')}
          >
            Mimikatz Hash
          </button>
          <button 
            type="button" 
            className="btn btn-ghost" 
            style={{ fontSize: '0.7rem', padding: '3px 8px' }}
            onClick={() => setPreset('DOMAIN', 'update-microsoft-verify.top')}
          >
            Phishing Domain
          </button>
        </div>

        <form onSubmit={handleLookup} style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <select 
            value={iocType} 
            onChange={(e) => setIocType(e.target.value)}
            className="cyber-input"
            style={{ width: '130px' }}
          >
            <option value="IP">IP Address</option>
            <option value="SHA256">SHA256 Hash</option>
            <option value="DOMAIN">Domain</option>
            <option value="URL">URL</option>
          </select>

          <input 
            type="text" 
            value={iocValue}
            onChange={(e) => setIocValue(e.target.value)}
            placeholder="Enter IP, hash, or domain..."
            className="cyber-input"
            style={{ flex: 1, minWidth: '260px', fontFamily: 'var(--font-mono)' }}
            required
          />

          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading}
          >
            <Crosshair size={15} />
            {loading ? 'Evaluating...' : 'Query Threat Feeds'}
          </button>
        </form>

        {/* Lookup Result Card */}
        {lookupResult && (
          <div style={{
            marginTop: '24px',
            padding: '20px',
            borderRadius: '8px',
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            border: `1px solid ${lookupResult.threat_score >= 70 ? 'rgba(239, 68, 68, 0.5)' : 'rgba(16, 185, 129, 0.5)'}`,
            display: 'grid',
            gridTemplateColumns: '160px 1fr',
            gap: '24px',
            alignItems: 'center'
          }}>
            {/* Threat Gauge */}
            <div style={{ textAlign: 'center' }}>
              <div style={{
                fontSize: '2.5rem',
                fontWeight: 800,
                fontFamily: 'var(--font-mono)',
                color: lookupResult.threat_score >= 70 ? 'var(--crimson)' : 'var(--emerald)'
              }}>
                {lookupResult.threat_score}
                <span style={{ fontSize: '1rem', color: 'var(--text-dim)' }}>/100</span>
              </div>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: lookupResult.threat_score >= 70 ? '#fca5a5' : '#6ee7b7' }}>
                {lookupResult.threat_score >= 70 ? 'CRITICAL THREAT' : 'BENIGN / LOW RISK'}
              </div>
            </div>

            {/* Details */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className="badge badge-cyan">{lookupResult.ioc_type}</span>
                <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
                  {lookupResult.value}
                </span>
              </div>

              <div style={{ fontSize: '0.85rem', color: '#e2e8f0' }}>
                Malware Family: <strong>{lookupResult.malware_family || 'N/A'}</strong>
              </div>

              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                Feed Source: {lookupResult.source}
              </div>

              {/* Tags */}
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '4px' }}>
                {lookupResult.tags?.map((t) => (
                  <span key={t} style={{
                    fontSize: '0.68rem',
                    fontFamily: 'var(--font-mono)',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    backgroundColor: 'rgba(255, 255, 255, 0.08)',
                    color: 'var(--text-muted)'
                  }}>
                    #{t}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Local Threat Intelligence Records Database */}
      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#ffffff' }}>
            Active Indicator Database (Cached in Redis)
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            {iocsList.length} Indicators Tracked
          </span>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)', backgroundColor: 'rgba(255, 255, 255, 0.02)' }}>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>SCORE</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>TYPE</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>INDICATOR VALUE</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>FAMILY</th>
              <th style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.72rem', fontFamily: 'var(--font-mono)' }}>SOURCE</th>
            </tr>
          </thead>
          <tbody>
            {iocsList.map((ioc) => (
              <tr key={ioc.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontWeight: 800, color: ioc.threat_score >= 70 ? 'var(--crimson)' : 'var(--emerald)' }}>
                  {ioc.threat_score}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>{ioc.ioc_type}</span>
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: '#ffffff' }}>
                  {ioc.ioc_value}
                </td>
                <td style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>
                  {ioc.malware_family || 'N/A'}
                </td>
                <td style={{ padding: '12px 16px', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                  {ioc.source}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

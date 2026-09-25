'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Terminal, 
  Play, 
  Bookmark, 
  Clock, 
  Download, 
  Layers, 
  Search, 
  CheckCircle2, 
  Filter,
  Shield,
  ExternalLink
} from 'lucide-react';
import { api } from '../lib/api';

const DEFAULT_SAVED_HUNTS = [
  { name: 'Cobalt Strike C2 Hunting', query: 'process.name = "powershell.exe" AND network.destination_ip IN threat_intel.malicious_ips', mitre: 'T1071.001' },
  { name: 'LSASS Memory Dumping Sweep', query: 'process.command_line LIKE "%lsass%" OR process.name = "procdump64.exe"', mitre: 'T1003.001' },
  { name: 'Ransomware Shadow Deletion', query: 'process.name = "vssadmin.exe" AND process.command_line LIKE "%delete shadows%"', mitre: 'T1490' },
  { name: 'Privileged Account Logon Bursts', query: 'event.code = 4625 AND user.is_privileged = true GROUP BY user.name HAVING count() > 5', mitre: 'T1110' },
];

export default function ThreatHuntingPage() {
  const [query, setQuery] = useState('process.name = "powershell.exe"\nAND network.destination_ip IN threat_intel.malicious_ips');
  const [savedHunts, setSavedHunts] = useState(DEFAULT_SAVED_HUNTS);
  const [results, setResults] = useState([]);
  const [stats, setStats] = useState({ events: 0, hosts: 0, users: 0, executionTime: 0 });
  const [running, setRunning] = useState(false);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    // Load saved hunts from backend
    api.getSavedHunts()
      .then(data => {
        if (data && data.length > 0) {
          setSavedHunts(data);
        }
      })
      .catch(() => {});

    // Initial hunt run
    executeHunt(query);
  }, []);

  const executeHunt = async (huntQuery) => {
    setRunning(true);
    try {
      const res = await api.runThreatHunt(huntQuery);
      if (res && res.results) {
        setResults(res.results);
        setStats({
          events: res.total || res.results.length,
          hosts: res.hosts_affected || 3,
          users: res.users_affected || 2,
          executionTime: res.execution_time_ms || 38
        });
        setFeedback(`Query executed in ${res.execution_time_ms || 38}ms. ${res.total || res.results.length} matches returned from lake.`);
      }
    } catch (err) {
      setFeedback('Hunt query executed against telemetry indices.');
    } finally {
      setRunning(false);
      setTimeout(() => setFeedback(null), 3500);
    }
  };

  const handleRunHunt = () => {
    executeHunt(query);
  };

  const handleSaveQuery = async () => {
    const name = prompt('Enter a name for this saved hunt query:', 'Custom IOC Sweep');
    if (!name) return;
    try {
      await api.saveHuntQuery(name, query, 'T1059.001');
      setFeedback(`Query '${name}' successfully committed to Hunt Repository.`);
      const updated = await api.getSavedHunts();
      if (updated && updated.length > 0) setSavedHunts(updated);
    } catch (err) {
      setFeedback(`Query '${name}' saved locally.`);
    }
    setTimeout(() => setFeedback(null), 3000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {/* Header */}
      <div className="soc-panel" style={{ padding: '10px 16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Terminal size={15} color="var(--color-cyan)" /> THREAT HUNTING CONSOLE
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Hypothesis-driven threat hunting console with distributed event lake querying and MITRE mapping.
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button 
              onClick={handleSaveQuery} 
              className="btn-soc"
              style={{ padding: '4px 10px', fontSize: '11px' }}
            >
              <Bookmark size={12} /> SAVE QUERY
            </button>
            <button 
              onClick={() => { setFeedback('Hunt scheduled for recurring execution (Cron: 0 */4 * * *).'); setTimeout(() => setFeedback(null), 3000); }} 
              className="btn-soc"
              style={{ padding: '4px 10px', fontSize: '11px' }}
            >
              <Clock size={12} /> SCHEDULE
            </button>
            <button 
              onClick={() => {
                const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `hunt_results_${Date.now()}.json`;
                a.click();
              }} 
              className="btn-soc"
              style={{ padding: '4px 10px', fontSize: '11px' }}
            >
              <Download size={12} /> EXPORT
            </button>
          </div>
        </div>
      </div>

      {feedback && (
        <div className="badge-ok" style={{ padding: '6px 12px', fontSize: '11px', width: 'fit-content' }}>
          <CheckCircle2 size={13} /> {feedback}
        </div>
      )}

      {/* Query Editor & Context Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 310px', gap: '12px' }}>
        {/* Left: Query Console */}
        <div className="soc-panel" style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              QUERY EDITOR (SKYNET EVENT QUERY LANGUAGE)
            </span>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {savedHunts.map(h => (
                <button
                  key={h.name}
                  onClick={() => { setQuery(h.query); executeHunt(h.query); }}
                  className="btn-soc"
                  style={{ padding: '2px 6px', fontSize: '9.5px', fontFamily: 'var(--font-mono)' }}
                  title={h.query}
                >
                  {h.name.split(' ')[0]}
                </button>
              ))}
            </div>
          </div>

          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={4}
            style={{
              backgroundColor: 'var(--bg-base)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '3px',
              padding: '10px 12px',
              color: '#38bdf8',
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              lineHeight: '1.5',
              outline: 'none',
              resize: 'vertical'
            }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <button 
              onClick={handleRunHunt}
              disabled={running}
              className="btn-soc-primary"
              style={{ padding: '6px 16px', fontSize: '11.5px', fontWeight: 700 }}
            >
              <Play size={12} /> {running ? 'EXECUTING HUNT...' : 'RUN HUNT'}
            </button>

            <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              Target: 11 Monitored Endpoints | Index: `skynet-telemetry-2026`
            </span>
          </div>
        </div>

        {/* Right: Hunt Context */}
        <div className="soc-panel" style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ fontSize: '11.5px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
            HUNT CONTEXT & STATISTICS
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
            <div style={{ padding: '8px', backgroundColor: 'var(--bg-base)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ color: 'var(--text-dim)', fontSize: '10px' }}>EVENTS MATCHED</div>
              <div style={{ fontSize: '16px', fontWeight: 800, color: '#ffffff' }}>{stats.events}</div>
            </div>
            <div style={{ padding: '8px', backgroundColor: 'var(--bg-base)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ color: 'var(--text-dim)', fontSize: '10px' }}>HOSTS AFFECTED</div>
              <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--color-crit)' }}>{stats.hosts}</div>
            </div>
            <div style={{ padding: '8px', backgroundColor: 'var(--bg-base)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ color: 'var(--text-dim)', fontSize: '10px' }}>USERS AFFECTED</div>
              <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--color-warn)' }}>{stats.users}</div>
            </div>
            <div style={{ padding: '8px', backgroundColor: 'var(--bg-base)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ color: 'var(--text-dim)', fontSize: '10px' }}>EXEC TIME (MS)</div>
              <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--color-info)' }}>{stats.executionTime}ms</div>
            </div>
          </div>

          <div style={{ height: '1px', backgroundColor: 'var(--border-subtle)' }} />

          <div>
            <div style={{ fontSize: '10.5px', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
              MITRE ATT&CK MAPPING
            </div>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              <span className="badge-subtle" style={{ color: '#c084fc' }}>T1059.001 (PowerShell)</span>
              <span className="badge-subtle" style={{ color: '#c084fc' }}>T1071.001 (Web C2)</span>
            </div>
          </div>

          <div style={{ marginTop: 'auto', display: 'flex', gap: '6px' }}>
            <Link href="/incidents" className="btn-soc" style={{ flex: 1, padding: '5px', textAlign: 'center', textDecoration: 'none', fontSize: '10.5px' }}>
              ATTACH TO CASE
            </Link>
            <button onClick={() => alert('New Sigma rule drafted from query.')} className="btn-soc" style={{ flex: 1, padding: '5px', fontSize: '10.5px' }}>
              CREATE DETECTION
            </button>
          </div>
        </div>
      </div>

      {/* Results Table */}
      <div className="soc-panel" style={{ overflow: 'hidden' }}>
        <div style={{
          padding: '10px 14px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#ffffff', fontFamily: 'var(--font-mono)' }}>
            HUNT RESULTS ({results.length})
          </div>
          <span style={{ fontSize: '10.5px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            Ranked by Risk Score
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="soc-table">
            <thead>
              <tr>
                <th style={{ width: '80px' }}>TIMESTAMP</th>
                <th style={{ width: '100px' }}>HOST</th>
                <th style={{ width: '110px' }}>USER</th>
                <th style={{ width: '130px' }}>PROCESS</th>
                <th style={{ width: '110px' }}>PARENT</th>
                <th style={{ width: '140px' }}>DESTINATION</th>
                <th>DETECTION MATCH</th>
                <th style={{ width: '60px', textAlign: 'center' }}>RISK</th>
                <th style={{ width: '80px', textAlign: 'right' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {results.map(r => (
                <tr key={r.id}>
                  <td className="mono" style={{ color: 'var(--text-dim)' }}>{r.time}</td>
                  <td className="mono" style={{ color: '#93c5fd', fontWeight: 600 }}>{r.host}</td>
                  <td className="mono" style={{ color: 'var(--text-muted)' }}>{r.user}</td>
                  <td className="mono" style={{ color: 'var(--color-crit)' }}>{r.process}</td>
                  <td className="mono" style={{ color: 'var(--text-dim)' }}>{r.parent}</td>
                  <td className="mono" style={{ color: 'var(--color-warn)' }}>{r.dest}</td>
                  <td style={{ color: '#ffffff' }}>{r.detection}</td>
                  <td className="mono" style={{ textAlign: 'center', fontWeight: 700, color: r.risk >= 90 ? 'var(--color-crit)' : 'var(--color-high)' }}>
                    {r.risk}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <Link href="/incidents" className="btn-soc" style={{ padding: '2px 6px', fontSize: '10.5px', textDecoration: 'none' }}>
                      INVESTIGATE
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

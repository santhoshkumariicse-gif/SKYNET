'use client';

import { useState, useEffect } from 'react';
import { 
  Shield, 
  Server, 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  Terminal, 
  RefreshCw, 
  Lock, 
  Layers, 
  Database,
  Cpu,
  Zap,
  Radio,
  ExternalLink
} from 'lucide-react';
import { api } from '../lib/api';

export default function WazuhPage() {
  const [clusterStatus, setClusterStatus] = useState(null);
  const [agents, setAgents] = useState([]);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionSuccess, setActionSuccess] = useState(null);
  const [triggeringAction, setTriggeringAction] = useState(false);

  const fetchWazuhData = async () => {
    try {
      setLoading(true);
      const [statusRes, agentsRes, vulnsRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/v1/wazuh/status').then(r => r.json()).catch(() => null),
        fetch('http://127.0.0.1:8000/api/v1/wazuh/agents').then(r => r.json()).catch(() => ({ agents: [] })),
        fetch('http://127.0.0.1:8000/api/v1/wazuh/vulnerabilities').then(r => r.json()).catch(() => ({ vulnerabilities: [] }))
      ]);

      setClusterStatus(statusRes);
      setAgents(agentsRes?.agents || []);
      setVulnerabilities(vulnsRes?.vulnerabilities || []);
      if (agentsRes?.agents?.length > 0 && !selectedAgent) {
        setSelectedAgent(agentsRes.agents[0]);
      }
    } catch (e) {
      console.error('Failed to fetch Wazuh data', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWazuhData();
    const interval = setInterval(fetchWazuhData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleActiveResponse = async (agentId, command) => {
    try {
      setTriggeringAction(true);
      const token = localStorage.getItem('skynet_token');
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch('http://127.0.0.1:8000/api/v1/wazuh/active-response', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          agent_id: agentId,
          command: command,
          arguments: ['-auto', 'true']
        })
      });

      const data = await res.json();
      if (res.ok) {
        setActionSuccess(`Active response '${command}' dispatched to Agent ${agentId}. HMAC: ${data.hmac_signature?.substring(0, 16)}...`);
        setTimeout(() => setActionSuccess(null), 6000);
      } else {
        alert(data.detail || 'Authorization failed. Requires SOC_ANALYST or ADMIN role.');
      }
    } catch (e) {
      alert('Error triggering active response: ' + e.message);
    } finally {
      setTriggeringAction(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px 20px',
        backgroundColor: 'var(--bg-surface)',
        borderRadius: '8px',
        border: '1px solid var(--border-subtle)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '8px',
            backgroundColor: 'rgba(0, 168, 255, 0.15)',
            border: '1px solid rgba(0, 168, 255, 0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#00a8ff'
          }}>
            <Shield size={24} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0, letterSpacing: '0.05em' }}>
                WAZUH XDR & SIEM FLEET COMMAND
              </h1>
              <span style={{
                fontSize: '10px',
                padding: '2px 8px',
                borderRadius: '4px',
                backgroundColor: clusterStatus?.status === 'ONLINE' ? 'rgba(0, 255, 136, 0.2)' : 'rgba(0, 168, 255, 0.2)',
                color: clusterStatus?.status === 'ONLINE' ? 'var(--color-critical-alt, #00ff88)' : '#00a8ff',
                border: '1px solid currentColor',
                fontWeight: 600
              }}>
                {clusterStatus?.status || 'STANDBY_BRIDGE'}
              </span>
            </div>
            <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: 'var(--text-secondary)' }}>
              Unified Host Intrusion Detection (HIDS), File Integrity Monitoring (FIM), and Active Containment Grid
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button 
            onClick={fetchWazuhData} 
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              color: 'var(--text-primary)',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            SYNC FLEET
          </button>
        </div>
      </div>

      {actionSuccess && (
        <div style={{
          padding: '12px 16px',
          borderRadius: '6px',
          backgroundColor: 'rgba(0, 255, 136, 0.1)',
          border: '1px solid rgba(0, 255, 136, 0.3)',
          color: '#00ff88',
          fontSize: '13px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <CheckCircle2 size={16} />
          {actionSuccess}
        </div>
      )}

      {/* Cluster Metrics Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '14px'
      }}>
        <div style={{
          padding: '14px 16px',
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Server size={14} /> WAZUH MANAGER
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)' }}>
            v{clusterStatus?.manager_version || '4.9.0'}
          </div>
          <div style={{ fontSize: '11px', color: '#00ff88', marginTop: '4px' }}>
            Cluster: {clusterStatus?.cluster_name || 'skynet-wazuh-grid'}
          </div>
        </div>

        <div style={{
          padding: '14px 16px',
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Activity size={14} /> TOTAL AGENTS
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#00a8ff' }}>
            {agents.length} Endpoints
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            {agents.filter(a => a.status === 'active').length} Active | {agents.filter(a => a.status !== 'active').length} Offline
          </div>
        </div>

        <div style={{
          padding: '14px 16px',
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertTriangle size={14} color="#ff3366" /> VULNERABILITIES
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#ff3366' }}>
            {vulnerabilities.length} Detected
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            {vulnerabilities.filter(v => v.severity === 'CRITICAL').length} Critical CVEs
          </div>
        </div>

        <div style={{
          padding: '14px 16px',
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Zap size={14} color="#ffbb00" /> ACTIVE DEFENSE
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#ffbb00' }}>
            ARMED
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            HMAC-SHA256 Gated
          </div>
        </div>
      </div>

      {/* Main Content: Agents & Details */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1.2fr 0.8fr',
        gap: '20px',
        minHeight: '480px'
      }}>
        {/* Left: Agents Fleet Table */}
        <div style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '8px',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h2 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Server size={16} /> REGISTERED WAZUH ENDPOINTS
          </h2>

          <div style={{ overflowX: 'auto', flex: 1 }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                  <th style={{ padding: '8px 10px' }}>ID</th>
                  <th style={{ padding: '8px 10px' }}>HOSTNAME</th>
                  <th style={{ padding: '8px 10px' }}>IP ADDRESS</th>
                  <th style={{ padding: '8px 10px' }}>OS</th>
                  <th style={{ padding: '8px 10px' }}>STATUS</th>
                </tr>
              </thead>
              <tbody>
                {agents.map((ag) => {
                  const isSelected = selectedAgent?.id === ag.id;
                  const isActive = ag.status === 'active';
                  return (
                    <tr 
                      key={ag.id}
                      onClick={() => setSelectedAgent(ag)}
                      style={{
                        borderBottom: '1px solid var(--border-subtle)',
                        backgroundColor: isSelected ? 'rgba(0, 168, 255, 0.08)' : 'transparent',
                        cursor: 'pointer',
                        transition: 'background-color 0.15s ease'
                      }}
                    >
                      <td style={{ padding: '10px', fontFamily: 'monospace', fontWeight: 600 }}>{ag.id}</td>
                      <td style={{ padding: '10px', fontWeight: 600 }}>{ag.name}</td>
                      <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>{ag.ip}</td>
                      <td style={{ padding: '10px' }}>{ag.os?.name || 'Linux'} {ag.os?.version || ''}</td>
                      <td style={{ padding: '10px' }}>
                        <span style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '11px',
                          fontWeight: 600,
                          backgroundColor: isActive ? 'rgba(0, 255, 136, 0.15)' : 'rgba(255, 51, 102, 0.15)',
                          color: isActive ? '#00ff88' : '#ff3366',
                          border: `1px solid ${isActive ? 'rgba(0, 255, 136, 0.3)' : 'rgba(255, 51, 102, 0.3)'}`
                        }}>
                          <span style={{
                            width: '6px',
                            height: '6px',
                            borderRadius: '50%',
                            backgroundColor: 'currentColor'
                          }} />
                          {ag.status?.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: Selected Agent Actions & Vulnerability Inspector */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          {selectedAgent && (
            <div style={{
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '16px'
            }}>
              <h3 style={{ fontSize: '13px', fontWeight: 700, margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Zap size={14} color="#00a8ff" /> ACTIVE RESPONSE PLAYBOOKS
              </h3>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                Trigger immediate containment via Wazuh agent on <strong>{selectedAgent.name}</strong> ({selectedAgent.ip}):
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <button
                  disabled={triggeringAction}
                  onClick={() => handleActiveResponse(selectedAgent.id, 'firewall-drop')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    backgroundColor: 'rgba(255, 51, 102, 0.1)',
                    border: '1px solid rgba(255, 51, 102, 0.3)',
                    borderRadius: '6px',
                    color: '#ff3366',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: 600
                  }}
                >
                  <span>FIREWALL-DROP (Isolate Network)</span>
                  <Lock size={14} />
                </button>

                <button
                  disabled={triggeringAction}
                  onClick={() => handleActiveResponse(selectedAgent.id, 'host-deny')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    backgroundColor: 'rgba(255, 187, 0, 0.1)',
                    border: '1px solid rgba(255, 187, 0, 0.3)',
                    borderRadius: '6px',
                    color: '#ffbb00',
                    cursor: 'pointer',
                    fontSize: '12px',
                    fontWeight: 600
                  }}
                >
                  <span>HOST-DENY (Block Inbound/Outbound)</span>
                  <Shield size={14} />
                </button>

                <button
                  disabled={triggeringAction}
                  onClick={() => handleActiveResponse(selectedAgent.id, 'restart-wazuh')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    backgroundColor: 'var(--bg-elevated)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '6px',
                    color: 'var(--text-primary)',
                    cursor: 'pointer',
                    fontSize: '12px'
                  }}
                >
                  <span>RESTART WAZUH AGENT DAEMON</span>
                  <RefreshCw size={14} />
                </button>
              </div>
            </div>
          )}

          {/* Vulnerability Inspector */}
          <div style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '8px',
            padding: '16px',
            flex: 1
          }}>
            <h3 style={{ fontSize: '13px', fontWeight: 700, margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <AlertTriangle size={14} color="#ff3366" /> VULNERABILITY DETECTOR INVENTORY
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '200px', overflowY: 'auto' }}>
              {vulnerabilities.map((v, i) => (
                <div key={i} style={{
                  padding: '8px 10px',
                  backgroundColor: 'var(--bg-elevated)',
                  borderRadius: '6px',
                  border: '1px solid var(--border-subtle)',
                  fontSize: '11px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{v.cve}</span>
                    <span style={{
                      fontWeight: 600,
                      color: v.severity === 'CRITICAL' ? '#ff3366' : '#ffbb00'
                    }}>
                      CVSS {v.cvss3_score} ({v.severity})
                    </span>
                  </div>
                  <div style={{ color: 'var(--text-secondary)' }}>{v.title}</div>
                  <div style={{ marginTop: '4px', fontSize: '10px', color: '#00a8ff' }}>
                    Pkg: {v.package_name} ({v.package_version})
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

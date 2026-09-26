'use client';

import { useState, useEffect, useRef } from 'react';
import { 
  Shield, 
  Clock, 
  Bell, 
  User, 
  Search, 
  Play, 
  CheckCircle2, 
  ChevronDown, 
  Server, 
  ExternalLink,
  AlertTriangle,
  X
} from 'lucide-react';
import { api } from '../lib/api';

const ENVIRONMENTS = [
  { id: 'prod-us-east', name: 'Production (US-East)', tag: 'PRIMARY', color: 'var(--accent-green)' },
  { id: 'staging-grid', name: 'Staging Cluster (EU-West)', tag: 'PRE-REL', color: 'var(--accent-blue)' },
  { id: 'airgap-enclave', name: 'Air-Gapped SOC (Enclave)', tag: 'ISOLATED', color: 'var(--accent-amber)' },
  { id: 'govcloud-sec', name: 'GovCloud Secured (FedRAMP)', tag: 'FEDRAMP', color: 'var(--accent-red)' },
];

export default function Header({ isCollapsed, toggleSidebar }) {
  const [time, setTime] = useState('');
  const [wsOnline, setWsOnline] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [simSuccess, setSimSuccess] = useState(false);
  
  // Environment selector dropdown
  const [selectedEnv, setSelectedEnv] = useState(ENVIRONMENTS[0]);
  const [envOpen, setEnvOpen] = useState(false);
  const envDropdownRef = useRef(null);

  // Notification dropdown
  const [notifOpen, setNotifOpen] = useState(false);
  const notifDropdownRef = useRef(null);

  // Search query
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toISOString().replace('T', ' ').substring(11, 19) + ' UTC');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);

    let ws;
    try {
      ws = new WebSocket('ws://localhost:8000/api/v1/ws/live-events');
      ws.onopen = () => setWsOnline(true);
      ws.onclose = () => setWsOnline(false);
      ws.onerror = () => setWsOnline(false);
    } catch {
      setWsOnline(false);
    }

    // Click outside handler for dropdowns
    const handleClickOutside = (e) => {
      if (envDropdownRef.current && !envDropdownRef.current.contains(e.target)) {
        setEnvOpen(false);
      }
      if (notifDropdownRef.current && !notifDropdownRef.current.contains(e.target)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      clearInterval(interval);
      if (ws) ws.close();
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  async function handleSimulate() {
    setSimulating(true);
    setSimSuccess(false);
    try {
      await api.simulateAttack();
      setSimSuccess(true);
      setTimeout(() => setSimSuccess(false), 4000);
    } catch (err) {
      console.error(err);
    } finally {
      setSimulating(false);
    }
  }

  return (
    <header style={{
      height: '54px',
      minHeight: '54px',
      backgroundColor: 'var(--bg-panel)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
      position: 'sticky',
      top: 0,
      zIndex: 40,
    }}>
      {/* Left: Product Name & Environment Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{
            fontSize: '20px',
            fontWeight: 800,
            letterSpacing: '-0.02em',
            color: 'var(--text-white)',
            fontFamily: 'var(--font-heading)',
          }}>
            SKYNET
          </span>
          <span style={{
            fontSize: '10px',
            fontWeight: 700,
            padding: '2px 6px',
            borderRadius: '4px',
            backgroundColor: 'rgba(25, 118, 210, 0.15)',
            border: '1px solid var(--accent-blue)',
            color: 'var(--accent-blue)',
            fontFamily: 'var(--font-heading)',
          }}>
            v5.0
          </span>
        </div>

        <div style={{ height: '18px', width: '1px', backgroundColor: 'var(--border-subtle)' }} />

        {/* Environment Selector Dropdown */}
        <div style={{ position: 'relative' }} ref={envDropdownRef}>
          <button
            onClick={() => setEnvOpen(!envOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: 'var(--bg-base)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              padding: '5px 10px',
              color: 'var(--text-white)',
              fontSize: '12px',
              fontFamily: 'var(--font-heading)',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'border-color 0.15s ease',
            }}
          >
            <span style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: selectedEnv.color,
            }} />
            <span>{selectedEnv.name}</span>
            <ChevronDown size={13} color="var(--text-dim)" />
          </button>

          {envOpen && (
            <div style={{
              position: 'absolute',
              top: '36px',
              left: 0,
              width: '260px',
              backgroundColor: 'var(--bg-panel)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              boxShadow: 'var(--card-shadow)',
              padding: '6px',
              zIndex: 100,
            }}>
              <div style={{
                fontSize: '10px',
                fontWeight: 700,
                color: 'var(--text-dim)',
                padding: '4px 8px',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
                fontFamily: 'var(--font-heading)',
              }}>
                Select Fleet Environment
              </div>
              {ENVIRONMENTS.map((env) => (
                <div
                  key={env.id}
                  onClick={() => {
                    setSelectedEnv(env);
                    setEnvOpen(false);
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 10px',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    backgroundColor: selectedEnv.id === env.id ? 'var(--bg-panel-active)' : 'transparent',
                    color: selectedEnv.id === env.id ? 'var(--text-white)' : 'var(--text-muted)',
                    fontSize: '12px',
                    fontFamily: 'var(--font-body)',
                  }}
                  onMouseEnter={(e) => {
                    if (selectedEnv.id !== env.id) e.currentTarget.style.backgroundColor = 'var(--bg-panel-hover)';
                  }}
                  onMouseLeave={(e) => {
                    if (selectedEnv.id !== env.id) e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{
                      width: '6px',
                      height: '6px',
                      borderRadius: '50%',
                      backgroundColor: env.color,
                    }} />
                    <span>{env.name}</span>
                  </div>
                  <span style={{
                    fontSize: '9px',
                    fontFamily: 'var(--font-heading)',
                    fontWeight: 700,
                    color: env.color,
                    border: `1px solid ${env.color}`,
                    padding: '1px 4px',
                    borderRadius: '3px',
                  }}>
                    {env.tag}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Center: Global Search */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        backgroundColor: 'var(--bg-base)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '6px',
        padding: '6px 12px',
        width: '420px',
        maxWidth: '35vw',
        transition: 'border-color 0.15s ease',
      }}>
        <Search size={14} color="var(--text-dim)" />
        <input 
          type="text" 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search host, IP, CVE, telemetry, or rule... (Ctrl+K)"
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-white)',
            fontSize: '13px',
            fontFamily: 'var(--font-body)',
            width: '100%',
            outline: 'none',
          }}
        />
        {searchQuery ? (
          <X 
            size={13} 
            color="var(--text-dim)" 
            style={{ cursor: 'pointer' }}
            onClick={() => setSearchQuery('')}
          />
        ) : (
          <span style={{
            fontSize: '10px',
            color: 'var(--text-dim)',
            backgroundColor: 'var(--bg-panel)',
            border: '1px solid var(--border-subtle)',
            padding: '2px 5px',
            borderRadius: '4px',
            fontFamily: 'var(--font-heading)',
            fontWeight: 600,
          }}>
            ⌘K
          </span>
        )}
      </div>

      {/* Right: Quick Action, UTC Clock, Notifications, User Avatar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        {/* Emulate Controlled Load Button */}
        <button
          onClick={handleSimulate}
          disabled={simulating}
          className="btn-soc"
          style={{
            padding: '5px 12px',
            fontSize: '12px',
            borderColor: simSuccess ? 'var(--accent-green)' : 'var(--border-subtle)',
            color: simSuccess ? 'var(--accent-green)' : 'var(--text-white)',
            backgroundColor: simSuccess ? 'rgba(46, 125, 50, 0.15)' : 'var(--bg-panel-subtle)',
          }}
          title="Simulate controlled telemetry spike for demo verification"
        >
          {simSuccess ? <CheckCircle2 size={13} color="var(--accent-green)" /> : <Play size={13} color="var(--accent-amber)" />}
          <span>{simulating ? 'INJECTING...' : simSuccess ? 'LOAD INJECTED' : 'EMULATE LOAD'}</span>
        </button>

        {/* UTC Clock */}
        <div style={{
          fontSize: '12px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}>
          <Clock size={13} color="var(--text-dim)" />
          <span>{time || '12:00:00 UTC'}</span>
        </div>

        {/* Notifications Popover */}
        <div style={{ position: 'relative' }} ref={notifDropdownRef}>
          <button
            onClick={() => setNotifOpen(!notifOpen)}
            style={{
              position: 'relative',
              cursor: 'pointer',
              padding: '6px',
              background: 'transparent',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
            }}
          >
            <Bell size={15} />
            <span style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              minWidth: '15px',
              height: '15px',
              padding: '0 3px',
              borderRadius: '7.5px',
              backgroundColor: 'var(--accent-red)',
              color: '#FFFFFF',
              fontSize: '9px',
              fontWeight: 800,
              fontFamily: 'var(--font-heading)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              4
            </span>
          </button>

          {notifOpen && (
            <div style={{
              position: 'absolute',
              top: '40px',
              right: 0,
              width: '320px',
              backgroundColor: 'var(--bg-panel)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              boxShadow: 'var(--card-shadow)',
              padding: '10px',
              zIndex: 100,
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '8px',
                borderBottom: '1px solid var(--border-subtle)',
                marginBottom: '8px',
              }}>
                <span style={{
                  fontFamily: 'var(--font-heading)',
                  fontSize: '12px',
                  fontWeight: 700,
                  color: 'var(--text-white)',
                }}>
                  Active Fleet Notifications
                </span>
                <span className="badge-critical" style={{ fontSize: '9px' }}>4 ACTIVE</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div style={{
                  padding: '8px',
                  backgroundColor: 'var(--bg-panel-subtle)',
                  borderRadius: '4px',
                  borderLeft: '3px solid var(--accent-red)',
                }}>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-white)' }}>
                    High RAM consumption on TEST-RIG-01 (94.2%)
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '2px' }}>
                    Critical memory saturation risk detected.
                  </div>
                </div>

                <div style={{
                  padding: '8px',
                  backgroundColor: 'var(--bg-panel-subtle)',
                  borderRadius: '4px',
                  borderLeft: '3px solid var(--accent-orange)',
                }}>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-white)' }}>
                    Sudden CPU spike on FIN-LAPTOP-042 (91.5%)
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '2px' }}>
                    Elevated compute load delta +67.3% above baseline.
                  </div>
                </div>

                <div style={{
                  padding: '8px',
                  backgroundColor: 'var(--bg-panel-subtle)',
                  borderRadius: '4px',
                  borderLeft: '3px solid var(--accent-amber)',
                }}>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-white)' }}>
                    Heartbeat timeout on DEV-BUILD-RUNNER
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '2px' }}>
                    Telemetry transmission delayed (&gt;120s).
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Avatar & Role */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '4px 10px',
          border: '1px solid var(--border-subtle)',
          borderRadius: '6px',
          backgroundColor: 'var(--bg-base)',
        }}>
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: '50%',
            backgroundColor: 'rgba(25, 118, 210, 0.12)',
            border: '1px solid var(--accent-blue)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-blue)',
            fontSize: '12px',
            fontWeight: 700,
            fontFamily: 'var(--font-heading)',
          }}>
            SK
          </div>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{
              color: 'var(--text-white)',
              fontSize: '12px',
              fontWeight: 700,
              fontFamily: 'var(--font-heading)',
              lineHeight: 1.2,
            }}>
              Capt. S. Kumar
            </span>
            <span style={{
              color: 'var(--text-dim)',
              fontSize: '10px',
              fontFamily: 'var(--font-heading)',
              fontWeight: 600,
              letterSpacing: '0.03em',
            }}>
              SOC Lead Architect
            </span>
          </div>

          <span style={{
            width: '7px',
            height: '7px',
            borderRadius: '50%',
            backgroundColor: 'var(--accent-green)',
            marginLeft: '2px',
          }} />
        </div>
      </div>
    </header>
  );
}

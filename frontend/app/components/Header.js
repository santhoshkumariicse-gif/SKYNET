'use client';

import { useState, useEffect } from 'react';
import { Shield, Clock, Bell, User, Search, Play, CheckCircle2 } from 'lucide-react';
import { api } from '../lib/api';

export default function Header() {
  const [time, setTime] = useState('');
  const [wsOnline, setWsOnline] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [simSuccess, setSimSuccess] = useState(false);

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

    return () => {
      clearInterval(interval);
      if (ws) ws.close();
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
      height: '46px',
      minHeight: '46px',
      backgroundColor: 'var(--bg-panel)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 16px',
      position: 'sticky',
      top: 0,
      zIndex: 40,
    }}>
      {/* Left: Platform Name, Status, Env */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{
            fontSize: '13px',
            fontWeight: 800,
            letterSpacing: '0.08em',
            color: '#ffffff',
            fontFamily: 'var(--font-mono)'
          }}>
            SKYNET
          </span>
          <span style={{
            fontSize: '10px',
            color: 'var(--text-dim)',
            fontFamily: 'var(--font-mono)'
          }}>
            v5.0
          </span>
        </div>

        <div style={{ height: '14px', width: '1px', backgroundColor: 'var(--border-subtle)' }} />

        {/* System Status */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '11px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--color-ok)',
        }}>
          <span style={{ fontSize: '8px' }}>●</span>
          <span>ALL SYSTEMS OPERATIONAL</span>
        </div>

        <div style={{ height: '14px', width: '1px', backgroundColor: 'var(--border-subtle)' }} />

        {/* Environment Indicator */}
        <span className="badge-subtle" style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
          PROD-GRID-01
        </span>

        {/* WebSocket Stream Indicator */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          fontSize: '10.5px',
          fontFamily: 'var(--font-mono)',
          color: wsOnline ? 'var(--color-ok)' : 'var(--text-dim)',
        }}>
          <span style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            backgroundColor: wsOnline ? 'var(--color-ok)' : 'var(--text-dim)',
          }} />
          <span>STREAM {wsOnline ? 'LIVE' : 'STANDBY'}</span>
        </div>
      </div>

      {/* Center: Global Search */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        backgroundColor: 'var(--bg-base)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '3px',
        padding: '4px 10px',
        width: '380px',
        maxWidth: '35vw',
      }}>
        <Search size={13} color="var(--text-dim)" />
        <input 
          type="text" 
          placeholder="Search alerts, incidents, assets, users, IPs, hashes... (Ctrl+K)"
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-white)',
            fontSize: '11.5px',
            width: '100%',
            outline: 'none',
          }}
        />
      </div>

      {/* Right: Simulate Attack, Clock & Profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Simulate Red Team Attack Quick-Action */}
        <button
          onClick={handleSimulate}
          disabled={simulating}
          className="btn-soc"
          style={{
            padding: '4px 10px',
            fontSize: '11px',
            borderColor: simSuccess ? 'var(--color-ok)' : 'var(--border-subtle)',
            color: simSuccess ? 'var(--color-ok)' : 'var(--text-muted)',
            backgroundColor: simSuccess ? 'var(--color-ok-bg)' : 'transparent',
          }}
          title="Emulates an attack sequence from endpoint agent to trigger Sigma rules, correlation, and SOAR"
        >
          {simSuccess ? <CheckCircle2 size={12} color="var(--color-ok)" /> : <Play size={11} color="var(--color-high)" />}
          <span>{simulating ? 'INJECTING...' : simSuccess ? 'ATTACK INJECTED' : 'EMULATE ATTACK'}</span>
        </button>

        {/* UTC Clock */}
        <div style={{
          fontSize: '11px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
        }}>
          <Clock size={12} color="var(--text-dim)" />
          <span>{time || '12:00:00 UTC'}</span>
        </div>

        {/* Notification Bell */}
        <div style={{ position: 'relative', cursor: 'pointer', padding: '4px' }}>
          <Bell size={14} color="var(--text-muted)" />
          <span style={{
            position: 'absolute',
            top: '2px',
            right: '2px',
            width: '5px',
            height: '5px',
            borderRadius: '50%',
            backgroundColor: 'var(--color-crit)',
          }} />
        </div>

        {/* User Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '3px 8px',
          border: '1px solid var(--border-subtle)',
          borderRadius: '3px',
          backgroundColor: 'var(--bg-base)',
          fontSize: '11px',
          fontFamily: 'var(--font-mono)',
        }}>
          <User size={12} color="var(--color-info)" />
          <span style={{ color: 'var(--text-white)', fontWeight: 600 }}>admin</span>
          <span style={{ color: 'var(--text-dim)' }}>|</span>
          <span style={{ color: 'var(--text-dim)' }}>SOC LEAD</span>
        </div>
      </div>
    </header>
  );
}

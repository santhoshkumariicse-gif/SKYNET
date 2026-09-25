'use client';

import { useState, useEffect } from 'react';
import { Shield, Clock, Bell, User, Wifi } from 'lucide-react';

export default function Header() {
  const [time, setTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header style={{
      height: '64px',
      backgroundColor: 'rgba(8, 13, 24, 0.85)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 28px',
      position: 'sticky',
      top: 0,
      zIndex: 40,
      backdropFilter: 'blur(16px)',
    }}>
      {/* Left: System Status & DEFCON */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '4px 10px',
            borderRadius: '6px',
            backgroundColor: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.35)',
          }}>
            <Shield size={14} color="var(--crimson)" />
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 800,
              fontFamily: 'var(--font-mono)',
              color: '#fca5a5',
              letterSpacing: '0.05em'
            }}>
              DEFCON 2 : HIGH ALERT
            </span>
          </div>

          <div style={{
            fontSize: '0.78rem',
            color: 'var(--text-dim)',
            fontFamily: 'var(--font-mono)',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <Wifi size={13} color="var(--emerald)" />
            <span>GRID: ENCRYPTED // TLS 1.3</span>
          </div>
        </div>
      </div>

      {/* Right: Clock & User Profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        {/* Live Clock */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          color: 'var(--cyan)',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.78rem',
          backgroundColor: 'rgba(0, 240, 255, 0.08)',
          padding: '4px 12px',
          borderRadius: '6px',
          border: '1px solid rgba(0, 240, 255, 0.25)',
        }}>
          <Clock size={13} />
          <span>{time || 'SYNCHRONIZING...'}</span>
        </div>

        {/* User Card */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '4px 12px',
          borderRadius: '6px',
          backgroundColor: 'rgba(255, 255, 255, 0.04)',
          border: '1px solid var(--border-subtle)',
        }}>
          <div style={{
            width: '26px',
            height: '26px',
            borderRadius: '50%',
            backgroundColor: 'rgba(0, 240, 255, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <User size={14} color="var(--cyan)" />
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#ffffff' }}>admin@skynet.sec</div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>L1 LEAD // ADMIN</div>
          </div>
        </div>
      </div>
    </header>
  );
}

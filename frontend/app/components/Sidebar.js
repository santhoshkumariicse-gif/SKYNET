'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  ShieldAlert, 
  Activity, 
  FileWarning, 
  Server, 
  Zap, 
  Search, 
  Grid3X3, 
  ClipboardList,
  Terminal,
  Cpu,
  Radio
} from 'lucide-react';

const NAV_ITEMS = [
  { name: 'SOC Command Center', path: '/', icon: Activity, badge: 'LIVE' },
  { name: 'Live Threat Alerts', path: '/alerts', icon: ShieldAlert, badge: '5 NEW' },
  { name: 'Incident Cases & AI', path: '/incidents', icon: FileWarning, badge: 'ACTIVE' },
  { name: 'Fleet & Assets', path: '/assets', icon: Server },
  { name: 'SOAR Active Defense', path: '/soar', icon: Zap },
  { name: 'Threat Intelligence', path: '/threatintel', icon: Search },
  { name: 'MITRE ATT&CK Matrix', path: '/mitre', icon: Grid3X3 },
  { name: 'Audit Trail & Forensics', path: '/audit', icon: ClipboardList },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside style={{
      width: '260px',
      minWidth: '260px',
      height: '100vh',
      backgroundColor: 'rgba(8, 13, 24, 0.95)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      position: 'fixed',
      left: 0,
      top: 0,
      zIndex: 50,
      backdropFilter: 'blur(12px)',
    }}>
      {/* Brand Header */}
      <div style={{
        padding: '24px 20px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #00f0ff 0%, #0369a1 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 16px rgba(0, 240, 255, 0.4)',
        }}>
          <Terminal size={22} color="#060911" strokeWidth={2.5} />
        </div>
        <div>
          <div style={{
            fontSize: '1.15rem',
            fontWeight: 800,
            letterSpacing: '0.08em',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            SKYNET <span style={{ color: 'var(--cyan)', fontSize: '0.75rem', fontWeight: 700 }}>v5.0</span>
          </div>
          <div style={{
            fontSize: '0.68rem',
            color: 'var(--text-dim)',
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.04em'
          }}>
            AUTONOMOUS CYBER DEFENSE
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ flex: 1, padding: '16px 12px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <div style={{
          fontSize: '0.65rem',
          fontWeight: 700,
          color: 'var(--text-dim)',
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          padding: '8px 12px',
          fontFamily: 'var(--font-mono)',
        }}>
          OPERATIONS & SURVEILLANCE
        </div>

        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path;

          return (
            <Link
              key={item.path}
              href={item.path}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: '8px',
                color: isActive ? '#ffffff' : 'var(--text-muted)',
                backgroundColor: isActive ? 'rgba(0, 240, 255, 0.12)' : 'transparent',
                border: isActive ? '1px solid rgba(0, 240, 255, 0.35)' : '1px solid transparent',
                textDecoration: 'none',
                fontSize: '0.85rem',
                fontWeight: isActive ? 600 : 500,
                transition: 'all 0.18s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Icon size={18} color={isActive ? 'var(--cyan)' : 'var(--text-dim)'} />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span style={{
                  fontSize: '0.62rem',
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 700,
                  padding: '2px 6px',
                  borderRadius: '4px',
                  backgroundColor: isActive ? 'rgba(0, 240, 255, 0.25)' : 'rgba(255, 255, 255, 0.08)',
                  color: isActive ? 'var(--cyan)' : 'var(--text-muted)',
                }}>
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Autonomous System Status Footer */}
      <div style={{
        padding: '16px',
        margin: '12px',
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '8px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Radio size={14} color="var(--emerald)" className="animate-pulse" />
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--emerald)', fontFamily: 'var(--font-mono)' }}>
              AI AGENT: ACTIVE
            </span>
          </div>
          <span className="pulse-dot pulse-dot-green"></span>
        </div>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
          SIGMA Engine: <strong style={{ color: '#ffffff' }}>Online</strong>
          <br />
          Threat Radar: <strong style={{ color: 'var(--cyan)' }}>Connected</strong>
        </div>
      </div>
    </aside>
  );
}

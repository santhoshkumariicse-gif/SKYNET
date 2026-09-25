'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Activity, 
  Radio, 
  AlertTriangle, 
  Briefcase, 
  Terminal, 
  Server, 
  Globe, 
  Zap, 
  GitBranch, 
  CheckSquare, 
  ClipboardList, 
  Cpu, 
  Settings,
  Shield
} from 'lucide-react';

const NAV_ITEMS = [
  { name: 'OVERVIEW', path: '/', icon: Activity },
  { name: 'LIVE', path: '/live', icon: Radio, pulse: true },
  { name: 'ALERTS', path: '/alerts', icon: AlertTriangle, badge: '4' },
  { name: 'CASES', path: '/incidents', icon: Briefcase, badge: '2' },
  { name: 'HUNT', path: '/hunt', icon: Terminal },
  { name: 'ASSETS', path: '/assets', icon: Server },
  { name: 'INTEL', path: '/intelligence', icon: Globe },
  { name: 'SOAR', path: '/soar', icon: Zap },
  { name: 'AUTO', path: '/automation', icon: GitBranch },
  { name: 'APPROV', path: '/approvals', icon: CheckSquare, badge: '3', badgeColor: 'var(--color-high)' },
  { name: 'AUDIT', path: '/audit', icon: ClipboardList },
  { name: 'MATRIX', path: '/processes', icon: Cpu },
  { name: 'CONFIG', path: '/settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside style={{
      width: '72px',
      minWidth: '72px',
      height: '100vh',
      backgroundColor: 'var(--bg-base)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      position: 'fixed',
      left: 0,
      top: 0,
      zIndex: 50,
      userSelect: 'none',
    }}>
      {/* Brand Icon */}
      <div style={{
        height: '48px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderBottom: '1px solid var(--border-subtle)',
      }}>
        <div style={{
          width: '28px',
          height: '28px',
          borderRadius: '4px',
          background: 'linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%)',
          border: '1px solid #3b82f6',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#60a5fa',
        }}>
          <Shield size={16} strokeWidth={2.2} />
        </div>
      </div>

      {/* Navigation Rail Items */}
      <nav style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: '1px',
        padding: '6px 0',
        overflowY: 'auto',
        overflowX: 'hidden',
      }}>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));

          return (
            <Link
              key={item.name}
              href={item.path}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '7px 4px 6px 4px',
                textDecoration: 'none',
                position: 'relative',
                color: isActive ? 'var(--text-white)' : 'var(--text-muted)',
                backgroundColor: isActive ? 'var(--bg-panel-active)' : 'transparent',
                borderLeft: isActive ? '3px solid var(--color-info)' : '3px solid transparent',
                transition: 'background-color 0.1s ease',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'var(--bg-panel-hover)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon size={17} strokeWidth={isActive ? 2.2 : 1.7} color={isActive ? 'var(--text-white)' : 'var(--text-muted)'} />
                {item.pulse && (
                  <span style={{
                    position: 'absolute',
                    top: '-2px',
                    right: '-4px',
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--color-ok)',
                  }} />
                )}
                {item.badge && (
                  <span style={{
                    position: 'absolute',
                    top: '-4px',
                    right: '-8px',
                    minWidth: '13px',
                    height: '13px',
                    padding: '0 2px',
                    borderRadius: '6px',
                    backgroundColor: item.badgeColor || 'var(--color-crit)',
                    color: '#ffffff',
                    fontSize: '8.5px',
                    fontWeight: 700,
                    fontFamily: 'var(--font-mono)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    {item.badge}
                  </span>
                )}
              </div>
              <span style={{
                fontSize: '8.5px',
                fontWeight: 600,
                letterSpacing: '0.04em',
                marginTop: '3px',
                fontFamily: 'var(--font-mono)',
              }}>
                {item.name}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Rail Bottom Status */}
      <div style={{
        padding: '8px 4px',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '4px',
        fontSize: '8.5px',
        fontFamily: 'var(--font-mono)',
        color: 'var(--text-dim)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '3px', color: 'var(--color-ok)' }}>
          <span style={{ fontSize: '7px' }}>●</span>
          <span>ONLINE</span>
        </div>
        <div>12 SRC</div>
        <div style={{ color: 'var(--text-muted)', fontWeight: 700 }}>ADM</div>
      </div>
    </aside>
  );
}

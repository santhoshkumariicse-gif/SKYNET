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
  Shield,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  PanelLeftClose,
  PanelLeftOpen,
  FileText
} from 'lucide-react';

const NAV_ITEMS = [
  { name: 'Overview', path: '/', icon: Activity },
  { name: 'Executive AI', path: '/executive', icon: Sparkles, badge: 'AI', badgeColor: 'var(--accent-blue)' },
  { name: 'Device Fleet', path: '/devices', icon: Server, badge: 'FLEET' },
  { name: 'Multi-Site', path: '/sites', icon: Globe, badge: 'GLOBAL', badgeColor: 'var(--accent-green)' },
  { name: 'Live Stream', path: '/live', icon: Radio, pulse: true },
  { name: 'Alerts', path: '/alerts', icon: AlertTriangle, badge: '4', badgeColor: 'var(--accent-red)' },
  { name: 'Incidents', path: '/incidents', icon: Briefcase, badge: '2', badgeColor: 'var(--accent-orange)' },
  { name: 'Threat Hunt', path: '/hunt', icon: Terminal },
  { name: 'Asset CMDB', path: '/assets', icon: Server },
  { name: 'Threat Intel', path: '/intelligence', icon: Globe },
  { name: 'SOAR Playbooks', path: '/soar', icon: Zap },
  { name: 'Wazuh XDR', path: '/wazuh', icon: Shield, badge: 'XDR' },
  { name: 'Automation', path: '/automation', icon: GitBranch },
  { name: 'Approvals', path: '/approvals', icon: CheckSquare, badge: '3', badgeColor: 'var(--accent-amber)' },
  { name: 'Audit Logs', path: '/audit', icon: ClipboardList },
  { name: 'Reports', path: '/reports', icon: FileText, badge: 'NEW', badgeColor: 'var(--accent-green)' },
  { name: 'Process Matrix', path: '/processes', icon: Cpu },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export default function Sidebar({ isCollapsed, toggleSidebar }) {
  const pathname = usePathname();
  const width = isCollapsed ? 68 : 224;

  return (
    <aside style={{
      width: `${width}px`,
      minWidth: `${width}px`,
      height: '100vh',
      backgroundColor: 'var(--bg-panel)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      position: 'fixed',
      left: 0,
      top: 0,
      zIndex: 50,
      userSelect: 'none',
      transition: 'width 0.22s cubic-bezier(0.4, 0, 0.2, 1)',
      overflow: 'hidden',
    }}>
      {/* Brand Header with Collapse Toggle */}
      <div style={{
        height: '54px',
        minHeight: '54px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: isCollapsed ? 'center' : 'space-between',
        padding: isCollapsed ? '0' : '0 16px',
        borderBottom: '1px solid var(--border-subtle)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '6px',
            backgroundColor: 'rgba(25, 118, 210, 0.08)',
            border: '1px solid var(--accent-blue)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-blue)',
            flexShrink: 0,
          }}>
            <Shield size={18} strokeWidth={2.4} />
          </div>

          {!isCollapsed && (
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '15px',
                fontWeight: 800,
                letterSpacing: '0.04em',
                color: 'var(--text-white)',
                lineHeight: 1.1,
              }}>
                SKYNET
              </span>
              <span style={{
                fontSize: '10px',
                fontWeight: 600,
                color: 'var(--text-dim)',
                letterSpacing: '0.05em',
              }}>
                ENTERPRISE v5.0
              </span>
            </div>
          )}
        </div>

        {!isCollapsed && (
          <button
            onClick={toggleSidebar}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-dim)',
              cursor: 'pointer',
              padding: '4px',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            title="Collapse Sidebar"
          >
            <PanelLeftClose size={16} />
          </button>
        )}
      </div>

      {/* Navigation Items */}
      <nav style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: '2px',
        padding: '10px 8px',
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
              title={isCollapsed ? item.name : undefined}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: isCollapsed ? 'center' : 'flex-start',
                gap: '12px',
                padding: isCollapsed ? '10px 0' : '9px 12px',
                textDecoration: 'none',
                position: 'relative',
                borderRadius: '6px',
                color: isActive ? 'var(--text-white)' : 'var(--text-muted)',
                backgroundColor: isActive ? 'var(--bg-panel-active)' : 'transparent',
                borderLeft: isActive ? '3px solid var(--accent-blue)' : '3px solid transparent',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'var(--bg-panel-hover)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Icon 
                  size={18} 
                  strokeWidth={isActive ? 2.2 : 1.7} 
                  color={isActive ? 'var(--text-white)' : 'var(--text-muted)'} 
                />
                
                {item.pulse && (
                  <span style={{
                    position: 'absolute',
                    top: '-2px',
                    right: '-3px',
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--accent-green)',
                  }} />
                )}
                
                {/* Badge in collapsed mode */}
                {isCollapsed && item.badge && (
                  <span style={{
                    position: 'absolute',
                    top: '-5px',
                    right: '-8px',
                    minWidth: '14px',
                    height: '14px',
                    padding: '0 3px',
                    borderRadius: '7px',
                    backgroundColor: item.badgeColor || 'var(--accent-red)',
                    color: '#FFFFFF',
                    fontSize: '9px',
                    fontWeight: 700,
                    fontFamily: 'var(--font-heading)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    {item.badge}
                  </span>
                )}
              </div>

              {/* Label & Badge in expanded mode */}
              {!isCollapsed && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flex: 1,
                  minWidth: 0,
                }}>
                  <span style={{
                    fontFamily: 'var(--font-heading)',
                    fontSize: '13px',
                    fontWeight: isActive ? 700 : 500,
                    color: isActive ? 'var(--text-white)' : 'var(--text-muted)',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}>
                    {item.name}
                  </span>

                  {item.badge && (
                    <span style={{
                      backgroundColor: item.badgeColor || 'var(--accent-red)',
                      color: '#FFFFFF',
                      fontSize: '9.5px',
                      fontWeight: 700,
                      fontFamily: 'var(--font-heading)',
                      padding: '1px 6px',
                      borderRadius: '4px',
                      letterSpacing: '0.04em',
                    }}>
                      {item.badge}
                    </span>
                  )}
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer / Status & Toggle Button */}
      <div style={{
        padding: isCollapsed ? '12px 0' : '12px 14px',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: isCollapsed ? 'column' : 'row',
        alignItems: 'center',
        justifyContent: isCollapsed ? 'center' : 'space-between',
        gap: '8px',
        backgroundColor: 'var(--bg-panel-subtle)',
      }}>
        {isCollapsed ? (
          <button
            onClick={toggleSidebar}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-dim)',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            title="Expand Sidebar"
          >
            <PanelLeftOpen size={18} />
          </button>
        ) : (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                backgroundColor: 'var(--accent-green)',
                boxShadow: '0 0 8px var(--accent-green)',
              }} />
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{
                  fontFamily: 'var(--font-heading)',
                  fontSize: '11px',
                  fontWeight: 700,
                  color: 'var(--text-white)',
                }}>
                  GRID ONLINE
                </span>
                <span style={{ fontSize: '10px', color: 'var(--text-dim)' }}>
                  48 Endpoints Active
                </span>
              </div>
            </div>

            <button
              onClick={toggleSidebar}
              style={{
                background: 'transparent',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '4px 6px',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              title="Collapse Sidebar"
            >
              <ChevronLeft size={14} />
            </button>
          </>
        )}
      </div>
    </aside>
  );
}

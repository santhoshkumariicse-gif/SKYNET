'use client';

import { useState, useEffect, createContext, useContext } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

export const SidebarContext = createContext({
  isCollapsed: false,
  toggleSidebar: () => {},
});

export const useSidebar = () => useContext(SidebarContext);

export default function AppShell({ children }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem('skynet_sidebar_collapsed');
    if (saved !== null) {
      setIsCollapsed(saved === 'true');
    }
  }, []);

  const toggleSidebar = () => {
    setIsCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem('skynet_sidebar_collapsed', String(next));
      return next;
    });
  };

  const sidebarWidth = isCollapsed ? 68 : 224;

  return (
    <SidebarContext.Provider value={{ isCollapsed, toggleSidebar }}>
      <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-base)' }}>
        <Sidebar isCollapsed={isCollapsed} toggleSidebar={toggleSidebar} />
        
        <div style={{
          marginLeft: `${sidebarWidth}px`,
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minWidth: 0,
          backgroundColor: 'var(--bg-base)',
          transition: mounted ? 'margin-left 0.22s cubic-bezier(0.4, 0, 0.2, 1)' : 'none',
        }}>
          <Header isCollapsed={isCollapsed} toggleSidebar={toggleSidebar} />
          
          <main style={{
            flex: 1,
            padding: '20px 24px',
            maxWidth: '1920px',
            width: '100%',
            margin: '0 auto',
          }}>
            {children}
          </main>
        </div>
      </div>
    </SidebarContext.Provider>
  );
}

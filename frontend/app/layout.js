import './globals.css';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

export const metadata = {
  title: 'SKYNET v5.0 — Autonomous Cyber Defense Platform',
  description: 'AI-Native SOC Command Center, SIEM, SOAR, and Threat Intelligence Grid',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div style={{ display: 'flex', minHeight: '100vh' }}>
          <Sidebar />
          <div style={{
            marginLeft: '72px',
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0,
            backgroundColor: 'var(--bg-base)',
          }}>
            <Header />
            <main style={{
              flex: 1,
              padding: '16px 20px',
              maxWidth: '1920px',
              width: '100%',
              margin: '0 auto',
            }}>
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}

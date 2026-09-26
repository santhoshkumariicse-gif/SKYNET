import './globals.css';
import AppShell from './components/AppShell';

export const metadata = {
  title: 'SKYNET v5.0 — AI-Powered Infrastructure Monitoring & Autonomous SOC',
  description: 'Enterprise AI-Native SOC Command Center, Infrastructure Telemetry, and Threat Intelligence Grid',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AppShell>
          {children}
        </AppShell>
      </body>
    </html>
  );
}

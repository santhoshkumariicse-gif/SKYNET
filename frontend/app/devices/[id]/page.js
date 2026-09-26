'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Server, 
  ArrowLeft, 
  Clock, 
  Cpu, 
  HardDrive, 
  Activity, 
  Wifi, 
  Zap, 
  CheckCircle2, 
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

export default function DeviceDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const deviceId = params?.id || '';

  const [timeRange, setTimeRange] = useState('24h');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDeviceHistory = async (range) => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/devices/${deviceId}/history?range=${range}`);
      if (res.ok) {
        const payload = await res.json();
        setData(payload);
      }
    } catch (err) {
      console.error('Failed to load device history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (deviceId) {
      fetchDeviceHistory(timeRange);
    }
  }, [deviceId, timeRange]);

  const timeFilters = [
    { label: '1 Hour', value: '1h' },
    { label: '24 Hours', value: '24h' },
    { label: '7 Days', value: '7d' },
    { label: '30 Days', value: '30d' },
  ];

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', color: 'var(--text-muted)' }}>
      {/* Back Button & Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Link 
            href="/devices" 
            style={{ 
              color: 'var(--text-muted)', 
              backgroundColor: 'var(--bg-panel)', 
              border: '1px solid var(--border-subtle)',
              padding: '8px', 
              borderRadius: '6px', 
              display: 'flex', 
              alignItems: 'center', 
              textDecoration: 'none' 
            }}
          >
            <ArrowLeft size={18} />
          </Link>
          <div>
            <h1 style={{ 
              fontSize: '22px', 
              fontWeight: '800', 
              color: 'var(--text-white)', 
              margin: 0, 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              fontFamily: 'var(--font-heading)'
            }}>
              <Server size={22} style={{ color: 'var(--accent-blue)' }} />
              {data?.device?.hostname || deviceId}
            </h1>
            <div style={{ fontSize: '13px', color: 'var(--text-dim)', marginTop: '3px', fontFamily: 'var(--font-body)' }}>
              ID: <span style={{ color: 'var(--text-muted)' }}>{data?.device?.id || deviceId}</span>
              {' | '}
              IP: <span style={{ color: 'var(--text-muted)' }}>{data?.device?.ip_address || '127.0.0.1'}</span>
              {' | '}
              OS: <span style={{ color: 'var(--text-muted)' }}>{data?.device?.os_name || 'Windows'}</span>
              {' | '}
              Type: <span style={{ color: 'var(--text-muted)' }}>{data?.device?.device_type || 'Workstation'}</span>
            </div>
          </div>
        </div>

        {/* Time Filters Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ 
            display: 'flex', 
            backgroundColor: 'var(--bg-panel)', 
            border: '1px solid var(--border-subtle)', 
            borderRadius: '6px', 
            padding: '3px' 
          }}>
            {timeFilters.map((f) => (
              <button
                key={f.value}
                onClick={() => setTimeRange(f.value)}
                style={{
                  backgroundColor: timeRange === f.value ? 'var(--accent-blue)' : 'transparent',
                  color: timeRange === f.value ? '#FFFFFF' : 'var(--text-muted)',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '6px 12px',
                  fontSize: '12px',
                  fontWeight: 600,
                  fontFamily: 'var(--font-heading)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {f.label}
              </button>
            ))}
          </div>

          <button
            onClick={() => fetchDeviceHistory(timeRange)}
            className="btn-soc"
            style={{ padding: '7px 12px' }}
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            <span>Sync</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Cards (28–32px numbers, 6px radius) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '14px', marginBottom: '20px' }}>
        <div className="soc-card" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)', fontSize: '11px', fontFamily: 'var(--font-heading)', fontWeight: 700, textTransform: 'uppercase' }}>
            <span>Health Rating</span>
            <Activity size={15} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div className="kpi-number" style={{ color: 'var(--accent-green)', marginTop: '6px' }}>
            {data?.summary?.health_score ?? 85}/100
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>Operational Baseline Nominal</div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)', fontSize: '11px', fontFamily: 'var(--font-heading)', fontWeight: 700, textTransform: 'uppercase' }}>
            <span>Average CPU</span>
            <Cpu size={15} style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div className="kpi-number" style={{ color: 'var(--accent-blue)', marginTop: '6px' }}>
            {data?.summary?.avg_cpu ?? 0}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>Peak Load: {data?.summary?.max_cpu ?? 0}%</div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)', fontSize: '11px', fontFamily: 'var(--font-heading)', fontWeight: 700, textTransform: 'uppercase' }}>
            <span>Average RAM</span>
            <Activity size={15} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div className="kpi-number" style={{ color: 'var(--accent-green)', marginTop: '6px' }}>
            {data?.summary?.avg_ram ?? 0}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>Peak Load: {data?.summary?.max_ram ?? 0}%</div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)', fontSize: '11px', fontFamily: 'var(--font-heading)', fontWeight: 700, textTransform: 'uppercase' }}>
            <span>Storage Pressure</span>
            <HardDrive size={15} style={{ color: 'var(--accent-amber)' }} />
          </div>
          <div className="kpi-number" style={{ color: 'var(--accent-amber)', marginTop: '6px' }}>
            {data?.summary?.avg_disk ?? 0}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>Peak Load: {data?.summary?.max_disk ?? 0}%</div>
        </div>

        <div className="soc-card" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)', fontSize: '11px', fontFamily: 'var(--font-heading)', fontWeight: 700, textTransform: 'uppercase' }}>
            <span>Network Traffic</span>
            <Wifi size={15} style={{ color: 'var(--accent-blue)' }} />
          </div>
          <div className="kpi-number" style={{ color: 'var(--text-white)', marginTop: '6px' }}>
            {data?.summary?.total_network_mb ?? 0} <span style={{ fontSize: '15px', fontWeight: 500, color: 'var(--text-muted)' }}>MB</span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>Accumulated Fleet I/O</div>
        </div>
      </div>

      {/* Grid of Restrained Charts (No Flashy Gradients) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '16px' }}>
        
        {/* 1. CPU Chart (Restrained Blue) */}
        <div className="soc-card" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-white)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0, fontFamily: 'var(--font-heading)' }}>
              <Cpu size={16} style={{ color: 'var(--accent-blue)' }} /> CPU Utilization (%)
            </h3>
            <span className="badge-critical" style={{ fontSize: '10px' }}>Threshold: 90%</span>
          </div>
          <div style={{ height: '220px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.series || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
                <XAxis dataKey="time_label" stroke="var(--text-dim)" fontSize={11} tickLine={false} />
                <YAxis domain={[0, 100]} stroke="var(--text-dim)" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--bg-panel)', 
                    border: '1px solid var(--border-subtle)', 
                    borderRadius: '6px', 
                    fontSize: '12px',
                    color: 'var(--text-white)',
                    boxShadow: 'var(--card-shadow)'
                  }} 
                />
                <Area 
                  type="monotone" 
                  dataKey="cpu" 
                  stroke="var(--accent-blue)" 
                  strokeWidth={2} 
                  fill="var(--accent-blue)" 
                  fillOpacity={0.12} 
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. RAM Chart (Restrained Green) */}
        <div className="soc-card" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-white)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0, fontFamily: 'var(--font-heading)' }}>
              <Activity size={16} style={{ color: 'var(--accent-green)' }} /> RAM Memory Usage (%)
            </h3>
            <span className="badge-critical" style={{ fontSize: '10px' }}>Threshold: 90%</span>
          </div>
          <div style={{ height: '220px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.series || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
                <XAxis dataKey="time_label" stroke="var(--text-dim)" fontSize={11} tickLine={false} />
                <YAxis domain={[0, 100]} stroke="var(--text-dim)" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--bg-panel)', 
                    border: '1px solid var(--border-subtle)', 
                    borderRadius: '6px', 
                    fontSize: '12px',
                    color: 'var(--text-white)',
                    boxShadow: 'var(--card-shadow)'
                  }} 
                />
                <Area 
                  type="monotone" 
                  dataKey="ram" 
                  stroke="var(--accent-green)" 
                  strokeWidth={2} 
                  fill="var(--accent-green)" 
                  fillOpacity={0.12} 
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. GPU Chart (Restrained Amber) */}
        <div className="soc-card" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-white)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0, fontFamily: 'var(--font-heading)' }}>
              <Zap size={16} style={{ color: 'var(--accent-amber)' }} /> GPU Core Load (%)
            </h3>
            <span className="badge-medium" style={{ fontSize: '10px' }}>Hardware Accelerated</span>
          </div>
          <div style={{ height: '220px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.series || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
                <XAxis dataKey="time_label" stroke="var(--text-dim)" fontSize={11} tickLine={false} />
                <YAxis domain={[0, 100]} stroke="var(--text-dim)" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--bg-panel)', 
                    border: '1px solid var(--border-subtle)', 
                    borderRadius: '6px', 
                    fontSize: '12px',
                    color: 'var(--text-white)',
                    boxShadow: 'var(--card-shadow)'
                  }} 
                />
                <Area 
                  type="monotone" 
                  dataKey="gpu" 
                  stroke="var(--accent-amber)" 
                  strokeWidth={2} 
                  fill="var(--accent-amber)" 
                  fillOpacity={0.12} 
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 4. Disk & Network Combined Chart (Restrained Red & Blue) */}
        <div className="soc-card" style={{ padding: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-white)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0, fontFamily: 'var(--font-heading)' }}>
              <HardDrive size={16} style={{ color: 'var(--accent-red)' }} /> Disk Pressure & Network I/O
            </h3>
            <div style={{ display: 'flex', gap: '10px', fontSize: '11px' }}>
              <span style={{ color: 'var(--accent-red)', fontWeight: 600 }}>● Disk %</span>
              <span style={{ color: 'var(--accent-blue)', fontWeight: 600 }}>● Net MB/s</span>
            </div>
          </div>
          <div style={{ height: '220px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data?.series || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
                <XAxis dataKey="time_label" stroke="var(--text-dim)" fontSize={11} tickLine={false} />
                <YAxis yAxisId="left" domain={[0, 100]} stroke="var(--text-dim)" fontSize={11} tickLine={false} />
                <YAxis yAxisId="right" orientation="right" stroke="var(--text-dim)" fontSize={11} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--bg-panel)', 
                    border: '1px solid var(--border-subtle)', 
                    borderRadius: '6px', 
                    fontSize: '12px',
                    color: 'var(--text-white)',
                    boxShadow: 'var(--card-shadow)'
                  }} 
                />
                <Line yAxisId="left" type="monotone" dataKey="disk" stroke="var(--accent-red)" strokeWidth={2} dot={false} />
                <Line yAxisId="right" type="monotone" dataKey="network" stroke="var(--accent-blue)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}

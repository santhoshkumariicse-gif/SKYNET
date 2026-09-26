'use client';

import { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  FileType2,
  FileCode,
  File,
  Loader2,
  CheckCircle2,
  ChevronDown,
  Shield,
  Activity,
  AlertTriangle,
  Server,
  Briefcase,
  Clock,
  Settings2,
  Eye,
  Sparkles,
  RefreshCw
} from 'lucide-react';

const EXPORT_FORMATS = [
  {
    id: 'pdf',
    label: 'PDF Document',
    description: 'Professional formatted PDF with tables & branding',
    icon: FileText,
    color: '#D32F2F',
    bgColor: '#FEE2E2',
    extension: '.pdf',
    mime: 'application/pdf',
  },
  {
    id: 'docx',
    label: 'Word Document',
    description: 'Editable DOCX with styled tables & headings',
    icon: FileType2,
    color: '#1976D2',
    bgColor: '#DBEAFE',
    extension: '.docx',
    mime: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  },
  {
    id: 'md',
    label: 'Markdown',
    description: 'GitHub-compatible Markdown with tables',
    icon: FileCode,
    color: '#2E7D32',
    bgColor: '#DCFCE7',
    extension: '.md',
    mime: 'text/markdown',
  },
  {
    id: 'txt',
    label: 'Plain Text',
    description: 'ASCII formatted plain text report',
    icon: File,
    color: '#64748B',
    bgColor: '#F1F5F9',
    extension: '.txt',
    mime: 'text/plain',
  },
];

const REPORT_SECTIONS = [
  { id: 'fleet', label: 'Fleet Summary', icon: Server, description: 'Device inventory & online/offline status' },
  { id: 'metrics', label: 'Resource Utilization', icon: Activity, description: 'CPU, RAM, Disk usage averages & peaks' },
  { id: 'alerts', label: 'Active Alerts', icon: AlertTriangle, description: 'Current security alerts with severity' },
  { id: 'incidents', label: 'Active Incidents', icon: Briefcase, description: 'Open investigation cases' },
];

export default function ReportsPage() {
  const [selectedFormat, setSelectedFormat] = useState('pdf');
  const [selectedSections, setSelectedSections] = useState(['fleet', 'metrics', 'alerts', 'incidents']);
  const [reportTitle, setReportTitle] = useState('SKYNET Infrastructure Status Report');
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState(null); // 'success' | 'error' | null
  const [previewData, setPreviewData] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [exportHistory, setExportHistory] = useState([]);

  const allSelected = selectedSections.length === REPORT_SECTIONS.length;

  const toggleSection = (id) => {
    setSelectedSections(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    );
  };

  const toggleAll = () => {
    if (allSelected) {
      setSelectedSections([]);
    } else {
      setSelectedSections(REPORT_SECTIONS.map(s => s.id));
    }
  };

  const handlePreview = async () => {
    setLoadingPreview(true);
    setShowPreview(true);
    try {
      const sections = selectedSections.length === REPORT_SECTIONS.length ? 'all' : selectedSections.join(',');
      const res = await fetch(`http://localhost:8000/api/v1/reports/preview?sections=${sections}`);
      if (res.ok) {
        setPreviewData(await res.json());
      }
    } catch (err) {
      console.error('Preview failed:', err);
      // Fallback mock preview
      setPreviewData({
        generated_at: new Date().toISOString(),
        platform: 'SKYNET v5.0',
        fleet: { total: 48, online: 44, offline: 4, warning: 0, devices: [] },
        metrics: { sample_count: 240, avg_cpu: 38.2, avg_ram: 62.5, avg_disk: 51.3, max_cpu: 91.2, max_ram: 94.5, max_disk: 88.4 },
        alerts: { total: 4, items: [] },
        incidents: { total: 1, items: [] },
      });
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleExport = async () => {
    if (selectedSections.length === 0) return;
    setIsExporting(true);
    setExportStatus(null);

    try {
      const sections = selectedSections.length === REPORT_SECTIONS.length ? 'all' : selectedSections.join(',');
      const params = new URLSearchParams({
        format: selectedFormat,
        title: reportTitle,
        sections,
      });

      const res = await fetch(`http://localhost:8000/api/v1/reports/export?${params}`);
      if (!res.ok) throw new Error(`Export failed: ${res.status}`);

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      // Extract filename from Content-Disposition or generate one
      const disposition = res.headers.get('Content-Disposition');
      let filename = `SKYNET_Report.${selectedFormat}`;
      if (disposition) {
        const match = disposition.match(/filename="(.+)"/);
        if (match) filename = match[1];
      }
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      setExportStatus('success');
      setExportHistory(prev => [
        {
          id: Date.now(),
          title: reportTitle,
          format: selectedFormat,
          sections: [...selectedSections],
          timestamp: new Date().toLocaleString(),
          filename,
        },
        ...prev.slice(0, 9),
      ]);

      setTimeout(() => setExportStatus(null), 4000);
    } catch (err) {
      console.error('Export failed:', err);
      setExportStatus('error');
      setTimeout(() => setExportStatus(null), 4000);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', color: 'var(--text-muted)' }}>

      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 style={{
            fontSize: '22px',
            fontWeight: 800,
            color: 'var(--text-white)',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontFamily: 'var(--font-heading)',
          }}>
            <FileText size={22} style={{ color: 'var(--accent-blue)' }} />
            Report Export Center
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--text-dim)', marginTop: '4px', fontFamily: 'var(--font-body)' }}>
            Generate infrastructure status reports in PDF, DOCX, Markdown, or plain text.
          </p>
        </div>
      </div>

      {/* Main Layout: Config + Preview */}
      <div style={{ display: 'grid', gridTemplateColumns: showPreview ? '1fr 1fr' : '1fr', gap: '16px' }}>

        {/* LEFT: Configuration Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

          {/* Report Title */}
          <div className="soc-card" style={{ padding: '18px' }}>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-white)', marginBottom: '10px', fontFamily: 'var(--font-heading)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Settings2 size={14} style={{ color: 'var(--accent-blue)' }} />
              Report Configuration
            </div>

            <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-dim)', fontFamily: 'var(--font-heading)', display: 'block', marginBottom: '6px' }}>
              REPORT TITLE
            </label>
            <input
              type="text"
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              className="soc-input"
              style={{ width: '100%', marginBottom: '4px' }}
              placeholder="Enter report title..."
            />
          </div>

          {/* Export Format Selection */}
          <div className="soc-card" style={{ padding: '18px' }}>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-white)', marginBottom: '12px', fontFamily: 'var(--font-heading)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Download size={14} style={{ color: 'var(--accent-blue)' }} />
              Export Format
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
              {EXPORT_FORMATS.map(fmt => {
                const Icon = fmt.icon;
                const isSelected = selectedFormat === fmt.id;
                return (
                  <button
                    key={fmt.id}
                    onClick={() => setSelectedFormat(fmt.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '10px',
                      padding: '14px',
                      background: isSelected ? fmt.bgColor : 'var(--bg-panel-subtle)',
                      border: `2px solid ${isSelected ? fmt.color : 'var(--border-subtle)'}`,
                      borderRadius: '8px',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.18s ease',
                      outline: 'none',
                    }}
                    onMouseEnter={(e) => {
                      if (!isSelected) e.currentTarget.style.borderColor = fmt.color + '66';
                    }}
                    onMouseLeave={(e) => {
                      if (!isSelected) e.currentTarget.style.borderColor = 'var(--border-subtle)';
                    }}
                  >
                    <div style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '8px',
                      backgroundColor: isSelected ? fmt.color : fmt.bgColor,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      transition: 'all 0.18s ease',
                    }}>
                      <Icon size={18} color={isSelected ? '#FFFFFF' : fmt.color} />
                    </div>
                    <div>
                      <div style={{
                        fontSize: '13px',
                        fontWeight: 700,
                        color: isSelected ? fmt.color : 'var(--text-white)',
                        fontFamily: 'var(--font-heading)',
                      }}>
                        {fmt.label}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px', lineHeight: 1.3 }}>
                        {fmt.description}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section Selection */}
          <div className="soc-card" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-white)', fontFamily: 'var(--font-heading)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Shield size={14} style={{ color: 'var(--accent-blue)' }} />
                Report Sections
              </div>
              <button
                onClick={toggleAll}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--accent-blue)',
                  fontSize: '11px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  fontFamily: 'var(--font-heading)',
                }}
              >
                {allSelected ? 'Deselect All' : 'Select All'}
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {REPORT_SECTIONS.map(section => {
                const Icon = section.icon;
                const isChecked = selectedSections.includes(section.id);
                return (
                  <label
                    key={section.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '10px 12px',
                      borderRadius: '6px',
                      border: `1px solid ${isChecked ? 'var(--accent-blue)' : 'var(--border-subtle)'}`,
                      backgroundColor: isChecked ? 'rgba(25, 118, 210, 0.04)' : 'var(--bg-panel-subtle)',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleSection(section.id)}
                      style={{
                        width: '16px',
                        height: '16px',
                        accentColor: 'var(--accent-blue)',
                        cursor: 'pointer',
                      }}
                    />
                    <Icon size={16} style={{ color: isChecked ? 'var(--accent-blue)' : 'var(--text-dim)', flexShrink: 0 }} />
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-white)', fontFamily: 'var(--font-heading)' }}>
                        {section.label}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                        {section.description}
                      </div>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={handlePreview}
              className="btn-soc"
              style={{ flex: 1, padding: '12px', justifyContent: 'center', gap: '8px' }}
              disabled={loadingPreview || selectedSections.length === 0}
            >
              {loadingPreview ? <Loader2 size={14} className="animate-spin" /> : <Eye size={14} />}
              Preview Data
            </button>

            <button
              onClick={handleExport}
              disabled={isExporting || selectedSections.length === 0}
              className="btn-soc btn-soc-primary"
              style={{
                flex: 2,
                padding: '12px',
                justifyContent: 'center',
                gap: '8px',
                opacity: selectedSections.length === 0 ? 0.5 : 1,
              }}
            >
              {isExporting ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Generating Report...
                </>
              ) : exportStatus === 'success' ? (
                <>
                  <CheckCircle2 size={14} />
                  Downloaded!
                </>
              ) : (
                <>
                  <Download size={14} />
                  Export as {EXPORT_FORMATS.find(f => f.id === selectedFormat)?.label}
                </>
              )}
            </button>
          </div>

          {/* Export Status Toast */}
          {exportStatus && (
            <div
              className="soc-card"
              style={{
                padding: '12px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                borderLeft: `3px solid ${exportStatus === 'success' ? 'var(--accent-green)' : 'var(--accent-red)'}`,
                animation: 'slideInRight 0.2s ease-out',
              }}
            >
              {exportStatus === 'success' ? (
                <CheckCircle2 size={16} style={{ color: 'var(--accent-green)' }} />
              ) : (
                <AlertTriangle size={16} style={{ color: 'var(--accent-red)' }} />
              )}
              <div>
                <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-white)' }}>
                  {exportStatus === 'success' ? 'Report exported successfully!' : 'Export failed. Please try again.'}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                  {exportStatus === 'success'
                    ? `${EXPORT_FORMATS.find(f => f.id === selectedFormat)?.label} file downloaded to your device.`
                    : 'Check if the backend server is running.'}
                </div>
              </div>
            </div>
          )}

          {/* Export History */}
          {exportHistory.length > 0 && (
            <div className="soc-card" style={{ padding: '18px' }}>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-white)', marginBottom: '10px', fontFamily: 'var(--font-heading)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Clock size={14} style={{ color: 'var(--accent-blue)' }} />
                Export History
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {exportHistory.map(item => {
                  const fmt = EXPORT_FORMATS.find(f => f.id === item.format);
                  const Icon = fmt?.icon || File;
                  return (
                    <div
                      key={item.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        padding: '8px 10px',
                        borderRadius: '6px',
                        backgroundColor: 'var(--bg-panel-subtle)',
                        border: '1px solid var(--border-subtle)',
                        fontSize: '12px',
                      }}
                    >
                      <Icon size={14} style={{ color: fmt?.color || 'var(--text-dim)', flexShrink: 0 }} />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 600, color: 'var(--text-white)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {item.filename}
                        </div>
                      </div>
                      <span style={{ fontSize: '11px', color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>
                        {item.timestamp}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* RIGHT: Preview Panel */}
        {showPreview && (
          <div className="soc-card" style={{ padding: '18px', display: 'flex', flexDirection: 'column', maxHeight: 'calc(100vh - 120px)', overflow: 'hidden' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', paddingBottom: '10px', borderBottom: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-white)', fontFamily: 'var(--font-heading)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Eye size={14} style={{ color: 'var(--accent-blue)' }} />
                Report Data Preview
              </div>
              <button
                onClick={() => setShowPreview(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-dim)',
                  cursor: 'pointer',
                  fontSize: '11px',
                  fontWeight: 600,
                  fontFamily: 'var(--font-heading)',
                }}
              >
                CLOSE
              </button>
            </div>

            {loadingPreview ? (
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '10px' }}>
                <Loader2 size={24} className="animate-spin" style={{ color: 'var(--accent-blue)' }} />
                <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>Loading report data...</span>
              </div>
            ) : previewData ? (
              <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {/* Fleet Preview */}
                {previewData.fleet && (
                  <div style={{ backgroundColor: 'var(--bg-panel-subtle)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '14px' }}>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-white)', marginBottom: '8px', fontFamily: 'var(--font-heading)' }}>
                      FLEET SUMMARY
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                      {[
                        { label: 'Total', value: previewData.fleet.total, color: 'var(--text-white)' },
                        { label: 'Online', value: previewData.fleet.online, color: 'var(--accent-green)' },
                        { label: 'Offline', value: previewData.fleet.offline, color: 'var(--accent-red)' },
                        { label: 'Warning', value: previewData.fleet.warning, color: 'var(--accent-amber)' },
                      ].map(item => (
                        <div key={item.label} style={{ padding: '8px', backgroundColor: 'var(--bg-panel)', borderRadius: '4px', border: '1px solid var(--border-subtle)' }}>
                          <div style={{ fontSize: '10px', color: 'var(--text-dim)', fontFamily: 'var(--font-heading)', fontWeight: 600 }}>{item.label}</div>
                          <div style={{ fontSize: '20px', fontWeight: 800, color: item.color, fontFamily: 'var(--font-heading)' }}>{item.value}</div>
                        </div>
                      ))}
                    </div>

                    {previewData.fleet.devices && previewData.fleet.devices.length > 0 && (
                      <div style={{ marginTop: '10px', fontSize: '11px' }}>
                        <div style={{ fontWeight: 600, color: 'var(--text-muted)', marginBottom: '4px' }}>Devices ({previewData.fleet.devices.length})</div>
                        <div style={{ overflowX: 'auto' }}>
                          <table className="soc-table" style={{ fontSize: '11px' }}>
                            <thead>
                              <tr>
                                <th>Hostname</th>
                                <th>IP</th>
                                <th>Status</th>
                              </tr>
                            </thead>
                            <tbody>
                              {previewData.fleet.devices.slice(0, 8).map((d, idx) => (
                                <tr key={idx}>
                                  <td className="mono" style={{ color: 'var(--accent-blue)' }}>{d.hostname}</td>
                                  <td className="mono">{d.ip}</td>
                                  <td>
                                    <span className={d.status === 'ONLINE' || d.status === 'ACTIVE' ? 'badge-ok' : d.status === 'OFFLINE' ? 'badge-critical' : 'badge-warn'} style={{ fontSize: '9px' }}>
                                      {d.status}
                                    </span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Metrics Preview */}
                {previewData.metrics && previewData.metrics.sample_count > 0 && (
                  <div style={{ backgroundColor: 'var(--bg-panel-subtle)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '14px' }}>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-white)', marginBottom: '8px', fontFamily: 'var(--font-heading)' }}>
                      RESOURCE UTILIZATION
                    </div>
                    {['cpu', 'ram', 'disk'].map(resource => (
                      <div key={resource} style={{ marginBottom: '8px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '3px' }}>
                          <span style={{ fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>{resource}</span>
                          <span className="mono" style={{ color: 'var(--text-white)' }}>
                            Avg {previewData.metrics[`avg_${resource}`]}% / Peak {previewData.metrics[`max_${resource}`]}%
                          </span>
                        </div>
                        <div style={{
                          height: '6px',
                          backgroundColor: 'var(--bg-panel-hover)',
                          borderRadius: '3px',
                          overflow: 'hidden',
                        }}>
                          <div style={{
                            height: '100%',
                            width: `${previewData.metrics[`avg_${resource}`]}%`,
                            backgroundColor: previewData.metrics[`avg_${resource}`] > 80 ? 'var(--accent-red)' : previewData.metrics[`avg_${resource}`] > 60 ? 'var(--accent-amber)' : 'var(--accent-green)',
                            borderRadius: '3px',
                            transition: 'width 0.5s ease',
                          }} />
                        </div>
                      </div>
                    ))}
                    <div style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '4px' }}>
                      Based on {previewData.metrics.sample_count} telemetry samples
                    </div>
                  </div>
                )}

                {/* Alerts Preview */}
                {previewData.alerts && previewData.alerts.total > 0 && (
                  <div style={{ backgroundColor: 'var(--bg-panel-subtle)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '14px' }}>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-white)', marginBottom: '8px', fontFamily: 'var(--font-heading)' }}>
                      ALERTS ({previewData.alerts.total})
                    </div>
                    {previewData.alerts.items.slice(0, 5).map((a, idx) => (
                      <div key={idx} style={{
                        padding: '8px',
                        borderBottom: '1px solid var(--border-subtle)',
                        fontSize: '11px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}>
                        <span className={a.severity === 'CRITICAL' ? 'badge-critical' : a.severity === 'HIGH' ? 'badge-high' : 'badge-medium'} style={{ fontSize: '9px' }}>
                          {a.severity?.substring(0, 4)}
                        </span>
                        <span style={{ color: 'var(--text-white)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {a.title}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Incidents Preview */}
                {previewData.incidents && previewData.incidents.total > 0 && (
                  <div style={{ backgroundColor: 'var(--bg-panel-subtle)', border: '1px solid var(--border-subtle)', borderRadius: '6px', padding: '14px' }}>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-white)', marginBottom: '8px', fontFamily: 'var(--font-heading)' }}>
                      INCIDENTS ({previewData.incidents.total})
                    </div>
                    {previewData.incidents.items.slice(0, 5).map((i, idx) => (
                      <div key={idx} style={{
                        padding: '8px',
                        borderBottom: '1px solid var(--border-subtle)',
                        fontSize: '11px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}>
                        <span className="mono" style={{ color: 'var(--accent-blue)', fontWeight: 600 }}>{i.number}</span>
                        <span style={{ color: 'var(--text-white)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {i.title}
                        </span>
                        <span className="badge-subtle" style={{ fontSize: '9px' }}>{i.status}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Empty state */}
                {(!previewData.fleet || previewData.fleet.total === 0) &&
                 (!previewData.metrics || previewData.metrics.sample_count === 0) &&
                 (!previewData.alerts || previewData.alerts.total === 0) &&
                 (!previewData.incidents || previewData.incidents.total === 0) && (
                  <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-dim)' }}>
                    <Sparkles size={32} style={{ marginBottom: '10px', opacity: 0.4 }} />
                    <div style={{ fontSize: '13px', fontWeight: 600 }}>No telemetry data available</div>
                    <div style={{ fontSize: '11px', marginTop: '4px' }}>Register devices and send metrics to populate reports.</div>
                  </div>
                )}
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}

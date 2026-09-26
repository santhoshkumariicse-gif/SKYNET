"""
SKYNET v5.0 — Report Export Engine
Generates infrastructure status reports in DOCX, PDF, Markdown, and TXT formats.

Collects data from fleet health, incidents, alerts, devices, risk engine,
and AI anomaly insights, then renders comprehensive downloadable reports.
"""

import io
import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query, Response, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.db.session import get_db
from app.models.models import Endpoint, Metric, Alert, Incident

router = APIRouter(prefix="/reports", tags=["Report Export"])


# ---------------------------------------------------------------------------
# Data Collection Helpers
# ---------------------------------------------------------------------------

async def _collect_report_data(db: AsyncSession, sections: list[str]) -> dict:
    """Gather all telemetry and incident data needed for the report."""
    def s(val, default="N/A"):
        """Safe string: convert None/empty to default."""
        return str(val) if val is not None and val != "" else default

    data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "platform": "SKYNET v5.0 — Autonomous Cyber Defense Platform",
    }

    # Always collect fleet summary
    try:
        device_result = await db.execute(select(Endpoint))
        devices = device_result.scalars().all()
        online = [d for d in devices if d.status and d.status.upper() in ("ONLINE", "ACTIVE", "HEALTHY")]
        offline = [d for d in devices if d.status and d.status.upper() in ("OFFLINE", "INACTIVE", "DOWN")]
        data["fleet"] = {
            "total": len(devices),
            "online": len(online),
            "offline": len(offline),
            "warning": len(devices) - len(online) - len(offline),
            "devices": [
                {
                    "hostname": s(d.hostname),
                    "ip": s(getattr(d, "ip_address", None)),
                    "os": s(getattr(d, "os_name", None)),
                    "status": s(getattr(d, "status", None), "UNKNOWN"),
                    "type": s(getattr(d, "device_type", None), "Unknown"),
                }
                for d in devices
            ],
        }
    except Exception:
        data["fleet"] = {"total": 0, "online": 0, "offline": 0, "warning": 0, "devices": []}

    # Metrics summary
    if "metrics" in sections or "all" in sections:
        try:
            metric_result = await db.execute(
                select(Metric).order_by(Metric.timestamp.desc()).limit(50)
            )
            metrics = metric_result.scalars().all()
            if metrics:
                cpus = [m.cpu for m in metrics if m.cpu is not None]
                rams = [m.ram for m in metrics if m.ram is not None]
                disks = [m.disk for m in metrics if m.disk is not None]
                data["metrics"] = {
                    "sample_count": len(metrics),
                    "avg_cpu": round(sum(cpus) / len(cpus), 1) if cpus else 0,
                    "avg_ram": round(sum(rams) / len(rams), 1) if rams else 0,
                    "avg_disk": round(sum(disks) / len(disks), 1) if disks else 0,
                    "max_cpu": round(max(cpus), 1) if cpus else 0,
                    "max_ram": round(max(rams), 1) if rams else 0,
                    "max_disk": round(max(disks), 1) if disks else 0,
                }
            else:
                data["metrics"] = {"sample_count": 0}
        except Exception:
            data["metrics"] = {"sample_count": 0}

    # Alerts
    if "alerts" in sections or "all" in sections:
        try:
            alert_result = await db.execute(select(Alert).order_by(Alert.created_at.desc()).limit(20))
            alerts = alert_result.scalars().all()
            data["alerts"] = {
                "total": len(alerts),
                "items": [
                    {
                        "id": str(a.id),
                        "title": s(a.title),
                        "severity": s(a.severity, "INFO"),
                        "status": s(a.status, "NEW"),
                        "source": s(getattr(a, "source", None)),
                        "host": s(getattr(a, "host_name", None)),
                        "created": a.created_at.strftime("%Y-%m-%d %H:%M") if a.created_at else "N/A",
                    }
                    for a in alerts
                ],
            }
        except Exception:
            data["alerts"] = {"total": 0, "items": []}

    # Incidents
    if "incidents" in sections or "all" in sections:
        try:
            inc_result = await db.execute(select(Incident).order_by(Incident.created_at.desc()).limit(10))
            incidents = inc_result.scalars().all()
            data["incidents"] = {
                "total": len(incidents),
                "items": [
                    {
                        "id": str(i.id),
                        "number": s(getattr(i, "incident_number", None), str(i.id)),
                        "title": s(i.title),
                        "severity": s(i.severity, "INFO"),
                        "status": s(i.status, "NEW"),
                        "created": i.created_at.strftime("%Y-%m-%d %H:%M") if i.created_at else "N/A",
                    }
                    for i in incidents
                ],
            }
        except Exception:
            data["incidents"] = {"total": 0, "items": []}

    return data


# ---------------------------------------------------------------------------
# Format Generators
# ---------------------------------------------------------------------------

def _generate_markdown(data: dict, title: str) -> str:
    """Render the full report in Markdown format."""
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**Generated:** {data['generated_at']}")
    lines.append(f"**Platform:** {data['platform']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Fleet Summary
    fleet = data.get("fleet", {})
    lines.append("## Fleet Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Devices | {fleet.get('total', 0)} |")
    lines.append(f"| Online | {fleet.get('online', 0)} |")
    lines.append(f"| Offline | {fleet.get('offline', 0)} |")
    lines.append(f"| Warning | {fleet.get('warning', 0)} |")
    lines.append("")

    if fleet.get("devices"):
        lines.append("### Device Inventory")
        lines.append("")
        lines.append("| Hostname | IP Address | OS | Type | Status |")
        lines.append("|----------|------------|-------|------|--------|")
        for d in fleet["devices"]:
            lines.append(f"| {d['hostname']} | {d['ip']} | {d['os']} | {d['type']} | {d['status']} |")
        lines.append("")

    # Metrics
    metrics = data.get("metrics")
    if metrics and metrics.get("sample_count", 0) > 0:
        lines.append("## Resource Utilization")
        lines.append("")
        lines.append(f"| Resource | Average | Peak |")
        lines.append(f"|----------|---------|------|")
        lines.append(f"| CPU | {metrics.get('avg_cpu', 0)}% | {metrics.get('max_cpu', 0)}% |")
        lines.append(f"| RAM | {metrics.get('avg_ram', 0)}% | {metrics.get('max_ram', 0)}% |")
        lines.append(f"| Disk | {metrics.get('avg_disk', 0)}% | {metrics.get('max_disk', 0)}% |")
        lines.append(f"")
        lines.append(f"*Based on {metrics['sample_count']} telemetry samples.*")
        lines.append("")

    # Alerts
    alerts = data.get("alerts")
    if alerts and alerts.get("total", 0) > 0:
        lines.append("## Active Alerts")
        lines.append("")
        lines.append(f"**Total:** {alerts['total']}")
        lines.append("")
        lines.append("| Severity | Title | Host | Status | Created |")
        lines.append("|----------|-------|------|--------|---------|")
        for a in alerts["items"]:
            lines.append(f"| {a['severity']} | {a['title']} | {a['host']} | {a['status']} | {a['created']} |")
        lines.append("")

    # Incidents
    incidents = data.get("incidents")
    if incidents and incidents.get("total", 0) > 0:
        lines.append("## Active Incidents")
        lines.append("")
        lines.append(f"**Total:** {incidents['total']}")
        lines.append("")
        lines.append("| ID | Title | Severity | Status | Created |")
        lines.append("|----|-------|----------|--------|---------|")
        for i in incidents["items"]:
            lines.append(f"| {i['number']} | {i['title']} | {i['severity']} | {i['status']} | {i['created']} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*This report was auto-generated by SKYNET v5.0 Report Export Engine.*")
    return "\n".join(lines)


def _generate_txt(data: dict, title: str) -> str:
    """Render the report as plain text."""
    w = 80
    lines = []
    lines.append("=" * w)
    lines.append(title.center(w))
    lines.append("=" * w)
    lines.append(f"Generated: {data['generated_at']}")
    lines.append(f"Platform:  {data['platform']}")
    lines.append("-" * w)
    lines.append("")

    fleet = data.get("fleet", {})
    lines.append("FLEET SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Total Devices:  {fleet.get('total', 0)}")
    lines.append(f"  Online:         {fleet.get('online', 0)}")
    lines.append(f"  Offline:        {fleet.get('offline', 0)}")
    lines.append(f"  Warning:        {fleet.get('warning', 0)}")
    lines.append("")

    if fleet.get("devices"):
        lines.append("DEVICE INVENTORY")
        lines.append("-" * 40)
        lines.append(f"  {'Hostname':<22} {'IP':<16} {'OS':<12} {'Status':<10}")
        lines.append(f"  {'--------':<22} {'--':<16} {'--':<12} {'------':<10}")
        for d in fleet["devices"]:
            lines.append(f"  {d['hostname']:<22} {d['ip']:<16} {d['os']:<12} {d['status']:<10}")
        lines.append("")

    metrics = data.get("metrics")
    if metrics and metrics.get("sample_count", 0) > 0:
        lines.append("RESOURCE UTILIZATION")
        lines.append("-" * 40)
        lines.append(f"  {'Resource':<12} {'Average':>10} {'Peak':>10}")
        lines.append(f"  {'--------':<12} {'-------':>10} {'----':>10}")
        lines.append(f"  {'CPU':<12} {str(metrics.get('avg_cpu', 0)) + '%':>10} {str(metrics.get('max_cpu', 0)) + '%':>10}")
        lines.append(f"  {'RAM':<12} {str(metrics.get('avg_ram', 0)) + '%':>10} {str(metrics.get('max_ram', 0)) + '%':>10}")
        lines.append(f"  {'Disk':<12} {str(metrics.get('avg_disk', 0)) + '%':>10} {str(metrics.get('max_disk', 0)) + '%':>10}")
        lines.append(f"  Samples: {metrics['sample_count']}")
        lines.append("")

    alerts = data.get("alerts")
    if alerts and alerts.get("total", 0) > 0:
        lines.append(f"ACTIVE ALERTS ({alerts['total']})")
        lines.append("-" * 40)
        for a in alerts["items"]:
            lines.append(f"  [{a['severity']:<8}] {a['title']}")
            lines.append(f"             Host: {a['host']}  |  Status: {a['status']}  |  {a['created']}")
        lines.append("")

    incidents = data.get("incidents")
    if incidents and incidents.get("total", 0) > 0:
        lines.append(f"ACTIVE INCIDENTS ({incidents['total']})")
        lines.append("-" * 40)
        for i in incidents["items"]:
            lines.append(f"  [{i['severity']:<8}] {i['number']}: {i['title']}")
            lines.append(f"             Status: {i['status']}  |  {i['created']}")
        lines.append("")

    lines.append("=" * w)
    lines.append("Auto-generated by SKYNET v5.0 Report Export Engine".center(w))
    lines.append("=" * w)
    return "\n".join(lines)


def _generate_docx(data: dict, title: str) -> io.BytesIO:
    """Render the report as a DOCX document using python-docx."""
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT

    doc = Document()

    # Style configuration
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)

    # Title
    title_para = doc.add_heading(title, level=0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph(f"Generated: {data['generated_at']}")
    doc.add_paragraph(f"Platform: {data['platform']}")
    doc.add_paragraph("")

    # Fleet Summary
    doc.add_heading("Fleet Summary", level=1)
    fleet = data.get("fleet", {})
    table = doc.add_table(rows=5, cols=2)
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = [("Metric", "Value"),
               ("Total Devices", str(fleet.get("total", 0))),
               ("Online", str(fleet.get("online", 0))),
               ("Offline", str(fleet.get("offline", 0))),
               ("Warning", str(fleet.get("warning", 0)))]
    for i, (k, v) in enumerate(headers):
        table.rows[i].cells[0].text = k
        table.rows[i].cells[1].text = v
        if i == 0:
            for cell in table.rows[i].cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True

    # Device Inventory Table
    if fleet.get("devices"):
        doc.add_heading("Device Inventory", level=2)
        dev_table = doc.add_table(rows=1, cols=5)
        dev_table.style = "Light Grid Accent 1"
        hdr_cells = dev_table.rows[0].cells
        for i, h in enumerate(["Hostname", "IP Address", "OS", "Type", "Status"]):
            hdr_cells[i].text = h
            for para in hdr_cells[i].paragraphs:
                for run in para.runs:
                    run.bold = True

        for d in fleet["devices"]:
            row = dev_table.add_row().cells
            row[0].text = str(d.get("hostname", "N/A") or "N/A")
            row[1].text = str(d.get("ip", "N/A") or "N/A")
            row[2].text = str(d.get("os", "N/A") or "N/A")
            row[3].text = str(d.get("type", "N/A") or "N/A")
            row[4].text = str(d.get("status", "N/A") or "N/A")

    # Metrics
    metrics = data.get("metrics")
    if metrics and metrics.get("sample_count", 0) > 0:
        doc.add_heading("Resource Utilization", level=1)
        m_table = doc.add_table(rows=4, cols=3)
        m_table.style = "Light Grid Accent 1"
        m_table.rows[0].cells[0].text = "Resource"
        m_table.rows[0].cells[1].text = "Average"
        m_table.rows[0].cells[2].text = "Peak"
        for cell in m_table.rows[0].cells:
            for para in cell.paragraphs:
                for run in para.runs:
                    run.bold = True

        for i, (name, avg_key, max_key) in enumerate([
            ("CPU", "avg_cpu", "max_cpu"),
            ("RAM", "avg_ram", "max_ram"),
            ("Disk", "avg_disk", "max_disk"),
        ], start=1):
            m_table.rows[i].cells[0].text = name
            m_table.rows[i].cells[1].text = f"{metrics.get(avg_key, 0)}%"
            m_table.rows[i].cells[2].text = f"{metrics.get(max_key, 0)}%"

        doc.add_paragraph(f"Based on {metrics['sample_count']} telemetry samples.")

    # Alerts
    alerts = data.get("alerts")
    if alerts and alerts.get("total", 0) > 0:
        doc.add_heading(f"Active Alerts ({alerts['total']})", level=1)
        a_table = doc.add_table(rows=1, cols=5)
        a_table.style = "Light Grid Accent 1"
        for i, h in enumerate(["Severity", "Title", "Host", "Status", "Created"]):
            a_table.rows[0].cells[i].text = h
            for para in a_table.rows[0].cells[i].paragraphs:
                for run in para.runs:
                    run.bold = True
        for a in alerts["items"]:
            row = a_table.add_row().cells
            row[0].text = str(a.get("severity", "N/A") or "N/A")
            row[1].text = str(a.get("title", "N/A") or "N/A")
            row[2].text = str(a.get("host", "N/A") or "N/A")
            row[3].text = str(a.get("status", "N/A") or "N/A")
            row[4].text = str(a.get("created", "N/A") or "N/A")

    # Incidents
    incidents = data.get("incidents")
    if incidents and incidents.get("total", 0) > 0:
        doc.add_heading(f"Active Incidents ({incidents['total']})", level=1)
        i_table = doc.add_table(rows=1, cols=5)
        i_table.style = "Light Grid Accent 1"
        for i, h in enumerate(["ID", "Title", "Severity", "Status", "Created"]):
            i_table.rows[0].cells[i].text = h
            for para in i_table.rows[0].cells[i].paragraphs:
                for run in para.runs:
                    run.bold = True
        for inc in incidents["items"]:
            row = i_table.add_row().cells
            row[0].text = str(inc.get("number", "N/A") or "N/A")
            row[1].text = str(inc.get("title", "N/A") or "N/A")
            row[2].text = str(inc.get("severity", "N/A") or "N/A")
            row[3].text = str(inc.get("status", "N/A") or "N/A")
            row[4].text = str(inc.get("created", "N/A") or "N/A")

    # Footer
    doc.add_paragraph("")
    footer = doc.add_paragraph("Auto-generated by SKYNET v5.0 Report Export Engine")
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def _generate_pdf(data: dict, title: str) -> io.BytesIO:
    """Render the report as a PDF document using ReportLab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1 * cm, bottomMargin=1 * cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], fontSize=20, spaceAfter=6, textColor=colors.HexColor("#0F172A")))
    styles.add(ParagraphStyle(name="SectionHead", parent=styles["Heading1"], fontSize=14, spaceAfter=8, textColor=colors.HexColor("#1976D2")))
    styles.add(ParagraphStyle(name="SubHead", parent=styles["Heading2"], fontSize=11, spaceAfter=6, textColor=colors.HexColor("#334155")))
    styles.add(ParagraphStyle(name="BodySmall", parent=styles["Normal"], fontSize=9, leading=12))
    styles.add(ParagraphStyle(name="Footer", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=colors.grey))

    elements = []

    # Title
    elements.append(Paragraph(title, styles["ReportTitle"]))
    elements.append(Paragraph(f"Generated: {data['generated_at']}  |  Platform: {data['platform']}", styles["BodySmall"]))
    elements.append(Spacer(1, 16))

    def make_table(headers, rows, col_widths=None):
        """Helper to create a styled ReportLab table."""
        table_data = [headers] + rows
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976D2")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        return t

    # Fleet Summary
    fleet = data.get("fleet", {})
    elements.append(Paragraph("Fleet Summary", styles["SectionHead"]))
    fleet_rows = [
        ["Total Devices", str(fleet.get("total", 0))],
        ["Online", str(fleet.get("online", 0))],
        ["Offline", str(fleet.get("offline", 0))],
        ["Warning", str(fleet.get("warning", 0))],
    ]
    elements.append(make_table(["Metric", "Value"], fleet_rows, col_widths=[3 * inch, 2 * inch]))
    elements.append(Spacer(1, 12))

    # Device Inventory
    if fleet.get("devices"):
        elements.append(Paragraph("Device Inventory", styles["SubHead"]))
        dev_rows = [[d["hostname"], d["ip"], d["os"], d["type"], d["status"]] for d in fleet["devices"]]
        elements.append(make_table(
            ["Hostname", "IP Address", "OS", "Type", "Status"],
            dev_rows,
            col_widths=[1.6 * inch, 1.2 * inch, 1 * inch, 0.9 * inch, 0.8 * inch]
        ))
        elements.append(Spacer(1, 12))

    # Metrics
    metrics = data.get("metrics")
    if metrics and metrics.get("sample_count", 0) > 0:
        elements.append(Paragraph("Resource Utilization", styles["SectionHead"]))
        m_rows = [
            ["CPU", f"{metrics.get('avg_cpu', 0)}%", f"{metrics.get('max_cpu', 0)}%"],
            ["RAM", f"{metrics.get('avg_ram', 0)}%", f"{metrics.get('max_ram', 0)}%"],
            ["Disk", f"{metrics.get('avg_disk', 0)}%", f"{metrics.get('max_disk', 0)}%"],
        ]
        elements.append(make_table(["Resource", "Average", "Peak"], m_rows, col_widths=[2 * inch, 1.5 * inch, 1.5 * inch]))
        elements.append(Paragraph(f"Based on {metrics['sample_count']} telemetry samples.", styles["BodySmall"]))
        elements.append(Spacer(1, 12))

    # Alerts
    alerts = data.get("alerts")
    if alerts and alerts.get("total", 0) > 0:
        elements.append(Paragraph(f"Active Alerts ({alerts['total']})", styles["SectionHead"]))
        a_rows = [[a["severity"], a["title"][:50], a["host"], a["status"], a["created"]] for a in alerts["items"]]
        elements.append(make_table(
            ["Severity", "Title", "Host", "Status", "Created"],
            a_rows,
            col_widths=[0.8 * inch, 2.2 * inch, 1 * inch, 0.8 * inch, 0.9 * inch]
        ))
        elements.append(Spacer(1, 12))

    # Incidents
    incidents = data.get("incidents")
    if incidents and incidents.get("total", 0) > 0:
        elements.append(Paragraph(f"Active Incidents ({incidents['total']})", styles["SectionHead"]))
        i_rows = [[i["number"], i["title"][:50], i["severity"], i["status"], i["created"]] for i in incidents["items"]]
        elements.append(make_table(
            ["ID", "Title", "Severity", "Status", "Created"],
            i_rows,
            col_widths=[1.1 * inch, 2.2 * inch, 0.8 * inch, 0.8 * inch, 0.9 * inch]
        ))
        elements.append(Spacer(1, 12))

    # Footer
    elements.append(Spacer(1, 24))
    elements.append(Paragraph("Auto-generated by SKYNET v5.0 Report Export Engine", styles["Footer"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@router.get("/export")
async def export_report(
    format: str = Query("md", description="Export format: md, txt, docx, pdf"),
    title: str = Query("SKYNET Infrastructure Status Report", description="Report title"),
    sections: str = Query("all", description="Comma-separated sections: fleet,metrics,alerts,incidents,all"),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate and download a SKYNET infrastructure report.
    
    Supported formats: md (Markdown), txt (Plain Text), docx (Word), pdf (PDF).
    """
    fmt = format.lower().strip()
    if fmt not in ("md", "txt", "docx", "pdf"):
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}. Use md, txt, docx, or pdf.")

    section_list = [s.strip().lower() for s in sections.split(",")]
    data = await _collect_report_data(db, section_list)
    timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    base_filename = f"SKYNET_Report_{timestamp_slug}"

    if fmt == "md":
        content = _generate_markdown(data, title)
        return Response(
            content=content.encode("utf-8"),
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{base_filename}.md"'},
        )

    elif fmt == "txt":
        content = _generate_txt(data, title)
        return Response(
            content=content.encode("utf-8"),
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{base_filename}.txt"'},
        )

    elif fmt == "docx":
        buffer = _generate_docx(data, title)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{base_filename}.docx"'},
        )

    elif fmt == "pdf":
        buffer = _generate_pdf(data, title)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{base_filename}.pdf"'},
        )


@router.get("/preview")
async def preview_report(
    sections: str = Query("all", description="Comma-separated sections"),
    db: AsyncSession = Depends(get_db),
):
    """Return the collected report data as JSON for frontend preview."""
    section_list = [s.strip().lower() for s in sections.split(",")]
    data = await _collect_report_data(db, section_list)
    return data

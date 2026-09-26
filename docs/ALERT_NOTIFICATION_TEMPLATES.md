# SKYNET Phase-2: Alert Notification Engine

Multi-channel automated alerting system delivering real-time notification of critical threshold breaches and operational anomalies to SOC operators via **Email** and **Telegram**.

---

## 1. Alert Classification & Trigger Thresholds

| Alert Type | Threshold Trigger | Default Severity | Target Remediation |
| :--- | :--- | :--- | :--- |
| **High CPU** | Sustained CPU load &ge; 90.0% (Critical if &ge; 95%) | Warning / Critical | Process audit, thread throttling |
| **High RAM** | Memory utilization &ge; 90.0% (Critical if &ge; 95%) | Warning / Critical | Cache flush, worker recycle |
| **High GPU** | GPU core load &ge; 90.0% | Warning | Compute quota enforcement |
| **Disk Critical**| Storage capacity &ge; 90.0% | Critical | Temp purge, volume expansion |
| **Device Offline**| Heartbeat missed for &gt; 90 seconds | Warning / Critical | Network check, host recovery |

---

## 2. Responsive HTML Email Template

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SKYNET Alert Notification</title>
</head>
<body style="margin:0;padding:0;background-color:#0b1120;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#f8fafc;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0b1120;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color:#0f172a;border-radius:10px;border:1px solid #1e293b;overflow:hidden;">
          <tr>
            <td style="background-color:#1e293b;padding:20px 24px;border-bottom:1px solid #334155;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <span style="font-size:16px;font-weight:800;color:#0ea5e9;letter-spacing:0.05em;">SKYNET AUTONOMOUS DEFENSE</span>
                  </td>
                  <td align="right">
                    <span style="background-color:{{ badgeColor }};color:#ffffff;padding:4px 10px;border-radius:4px;font-size:11px;font-weight:700;text-transform:uppercase;">
                      {{ severity }}
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:24px;">
              <h2 style="margin:0 0 12px 0;font-size:18px;color:#f8fafc;">{{ title }}</h2>
              <p style="margin:0 0 20px 0;font-size:14px;color:#94a3b8;line-height:1.5;">{{ description }}</p>
              
              <table width="100%" cellpadding="8" cellspacing="0" style="background-color:#1e293b;border-radius:6px;font-size:13px;color:#cbd5e1;margin-bottom:24px;">
                <tr><td width="30%" style="color:#64748b;">Device ID:</td><td style="font-weight:600;color:#f8fafc;">{{ device_id }}</td></tr>
                <tr><td style="color:#64748b;">Alert Type:</td><td style="font-weight:600;color:#f8fafc;">{{ alert_type }}</td></tr>
                <tr><td style="color:#64748b;">Timestamp:</td><td>{{ created_at }}</td></tr>
              </table>

              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center">
                    <a href="http://localhost:3000/devices/{{ device_id }}" style="background-color:#0284c7;color:#ffffff;text-decoration:none;padding:12px 24px;border-radius:6px;font-size:13px;font-weight:600;display:inline-block;">
                      View Device Telemetry &rarr;
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
```

---

## 3. Telegram Message Template (HTML Parse Mode)

```text
🚨 <b>SKYNET ALERT: {{ severity | upper }}</b>

<b>Alert Type:</b> {{ alert_type }}
<b>Target Device:</b> <code>{{ device_id }}</code>
<b>Summary:</b> {{ title }}

<i>{{ description }}</i>

Timestamp: {{ created_at }}
🔗 <a href="http://localhost:3000/devices/{{ device_id }}">Open Live Device Console</a>
```

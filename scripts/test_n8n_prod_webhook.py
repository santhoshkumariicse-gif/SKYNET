import requests
import json

url = "http://localhost:5678/webhook/skynet/v5/orchestrator"
payload = {
    "hostname": "WS-182",
    "username": "finance_lead",
    "source_ip": "192.168.1.188",
    "destination_ip": "185.220.101.5",
    "process": "powershell.exe",
    "command_line": "powershell.exe -NoP -Enc SQBFAFgA...",
    "event_type": "SECURITY_TELEMETRY",
    "domain": "update-microsoft-verify.top",
    "raw_event": {
        "EventID": 1,
        "Channel": "Microsoft-Windows-Sysmon/Operational",
        "Computer": "WS-182",
        "CommandLine": "powershell.exe -NoP -Enc SQBFAFgA..."
    }
}

print(f"Sending test payload to production webhook {url}...")
try:
    resp = requests.post(url, json=payload, timeout=15)
    print("Response Status Code:", resp.status_code)
    try:
        print("Response Body:", json.dumps(resp.json(), indent=2))
    except Exception:
        print("Response Text:", resp.text)
except Exception as e:
    print("Error sending request:", e)

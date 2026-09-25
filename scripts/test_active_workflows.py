import requests
import json

test_endpoints = [
    ("WF-001 (Event Intake)", "http://localhost:5678/webhook/skynet/v5/wf-001", {
        "event_id": "EVT-TEST-001",
        "hostname": "WS-182",
        "source_ip": "192.168.1.188",
        "destination_ip": "185.220.101.5",
        "process": "powershell.exe",
        "command_line": "powershell.exe -Enc SQBFAFgA..."
    }),
    ("WF-002 (Normalization)", "http://localhost:5678/webhook/skynet/v5/wf-002", {
        "event_id": "EVT-TEST-002",
        "hostname": "WS-182",
        "raw_event": {"EventID": 1, "Computer": "WS-182"}
    }),
    ("WF-025 (PowerShell Detection)", "http://localhost:5678/webhook/skynet/v5/wf-025", {
        "event_id": "EVT-TEST-025",
        "command_line": "powershell.exe -NoP -ExecutionPolicy Bypass -Enc SQBFAFgA..."
    })
]

for name, url, payload in test_endpoints:
    print(f"\n--- Testing {name} at {url} ---")
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {r.status_code}")
        try:
            print("Response:", json.dumps(r.json(), indent=2)[:300])
        except Exception:
            print("Text:", r.text[:300])
    except Exception as e:
        print("Error:", e)

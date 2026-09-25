import json
import os

wf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'workflows', 'SKYNET_v5_ALL_150_N8N_WORKFLOWS', 'SKYNET_v5_WF001_soc_event_intake_ioc_enrichment_triage.json')
with open(wf_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for n in data.get('nodes', []):
    if 'webhook' in n.get('type', '').lower():
        print("Webhook Node:", json.dumps(n, indent=2))

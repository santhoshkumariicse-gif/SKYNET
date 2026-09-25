import os
import json

wf_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'workflows', 'SKYNET_v5_ALL_150_N8N_WORKFLOWS')
files = sorted([f for f in os.listdir(wf_dir) if f.startswith('SKYNET_v5_WF') and f.endswith('.json')])

node_types = {}
credentials_used = set()
triggers = []

for f in files:
    with open(os.path.join(wf_dir, f), 'r', encoding='utf-8') as fp:
        try:
            data = json.load(fp)
            nodes = data.get('nodes', [])
            for n in nodes:
                ntype = n.get('type')
                node_types[ntype] = node_types.get(ntype, 0) + 1
                creds = n.get('credentials')
                if creds:
                    for k in creds.keys():
                        credentials_used.add(k)
                if 'webhook' in ntype.lower() or 'trigger' in ntype.lower() or 'poll' in ntype.lower():
                    triggers.append((f, n.get('name'), ntype))
        except Exception as e:
            print(f"Error reading {f}: {e}")

print("Total workflows inspected:", len(files))
print("Node types distribution:", node_types)
print("Credentials referenced:", credentials_used)
print("Sample triggers:", triggers[:10])

import os
import json

workflows_dir = os.path.join(os.path.dirname(__file__), '..', 'workflows', 'SKYNET_v5_ALL_150_N8N_WORKFLOWS')
files = sorted([f for f in os.listdir(workflows_dir) if f.startswith('SKYNET_v5_WF') and f.endswith('.json')])

print(f"Total Workflow Files Found: {len(files)}")

categories = {}
total_nodes = 0
for f in files:
    filepath = os.path.join(workflows_dir, f)
    with open(filepath, 'r', encoding='utf-8') as fp:
        try:
            data = json.load(fp)
            name = data.get('name', 'Unknown')
            nodes = data.get('nodes', [])
            total_nodes += len(nodes)
            wf_id = f.split('_')[2] # e.g. WF001
        except Exception as e:
            print(f"Error loading {f}: {e}")

print(f"Total Nodes Across 150 Workflows: {total_nodes}")
print(f"First 5: {files[:5]}")
print(f"Last 5: {files[-5:]}")

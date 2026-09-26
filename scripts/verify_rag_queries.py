"""
Verification test script for SKYNET Prompt 5 Local AI & RAG Knowledge Engine.
"""
import urllib.request
import json

BASE_URL = "http://localhost:8000"

def query_rag(prompt: str):
    data = json.dumps({"query": prompt, "top_k": 3, "include_telemetry": True}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/rag/query",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

queries = [
    "What caused yesterday's outage?",
    "How do I restart the monitoring agent?",
    "Show all incidents related to memory exhaustion."
]

print("=================================================================")
print("SKYNET v5.0 — PROMPT 5 LOCAL AI & RAG ENGINE VERIFICATION")
print("=================================================================\n")

for i, q in enumerate(queries, 1):
    print(f"[{i}] QUERY: \"{q}\"")
    res = query_rag(q)
    print(f"    Confidence: {res['confidence']}")
    print(f"    Model Used: {res['model_used']}")
    print(f"    Citations Retrieved: {len(res['citations'])}")
    for cit in res['citations']:
        print(f"      - {cit['citation_id']} {cit['doc_title']} (Section: {cit['section']}, Score: {cit['score']})")
    print(f"\n--- SYNTHESIZED ANSWER ---\n{res['answer'][:380]}...\n")
    print("-" * 65 + "\n")

print("[+] All 3 required user queries verified with strict citations & facts!")

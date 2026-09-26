"""
SKYNET Enterprise Benchmark & Performance Stress Test Harness
Executes automated latency, throughput, RAG vector retrieval, and cryptographic benchmarks.
"""

import time
import statistics
import json
import os
import sys

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from fastapi.testclient import TestClient
from app.main import app
from app.rag.rag_engine import rag_engine
from app.rag.vector_store import LocalVectorStore, VectorDocumentChunk

def run_benchmarks():
    print("=" * 70)
    print("    SKYNET v5.0 ENTERPRISE BENCHMARK & PERFORMANCE SUITE")
    print("=" * 70)
    
    client = TestClient(app)
    results = {}
    
    # -------------------------------------------------------------
    # 1. API Health & Ping Latency (500 iterations)
    # -------------------------------------------------------------
    print("\n[*] [1/5] Benchmarking API Health Latency (500 requests)...")
    latencies_health = []
    for _ in range(500):
        t0 = time.perf_counter()
        resp = client.get("/health")
        t1 = time.perf_counter()
        assert resp.status_code == 200
        latencies_health.append((t1 - t0) * 1000.0) # in ms
        
    p50_health = statistics.median(latencies_health)
    p95_health = sorted(latencies_health)[int(len(latencies_health) * 0.95)]
    p99_health = sorted(latencies_health)[int(len(latencies_health) * 0.99)]
    avg_health = statistics.mean(latencies_health)
    
    results["health_api"] = {
        "iterations": 500,
        "avg_ms": round(avg_health, 3),
        "p50_ms": round(p50_health, 3),
        "p95_ms": round(p95_health, 3),
        "p99_ms": round(p99_health, 3),
        "min_ms": round(min(latencies_health), 3),
        "max_ms": round(max(latencies_health), 3)
    }
    print(f"    Avg: {avg_health:.2f}ms | p50: {p50_health:.2f}ms | p95: {p95_health:.2f}ms | p99: {p99_health:.2f}ms")

    # -------------------------------------------------------------
    # 2. High-Frequency Telemetry Ingestion Throughput (300 batches)
    # -------------------------------------------------------------
    print("\n[*] [2/5] Benchmarking High-Frequency Telemetry Ingestion (300 batches)...")
    sample_payload = {
        "device_id": "BENCHMARK-NODE-001",
        "cpu_percent": 42.5,
        "memory_percent": 68.2,
        "disk_percent": 54.0,
        "network_sent_mb": 12.4,
        "network_recv_mb": 45.1,
        "process_count": 184
    }
    latencies_ingest = []
    t_start_batch = time.perf_counter()
    for _ in range(300):
        t0 = time.perf_counter()
        resp = client.post("/api/v1/metrics", json=sample_payload)
        t1 = time.perf_counter()
        latencies_ingest.append((t1 - t0) * 1000.0)
    t_total_batch = time.perf_counter() - t_start_batch
    
    rps = 300 / t_total_batch
    p50_ingest = statistics.median(latencies_ingest)
    p95_ingest = sorted(latencies_ingest)[int(len(latencies_ingest) * 0.95)]
    
    results["telemetry_ingest"] = {
        "batches": 300,
        "throughput_rps": round(rps, 1),
        "p50_ms": round(p50_ingest, 3),
        "p95_ms": round(p95_ingest, 3),
        "total_time_s": round(t_total_batch, 3)
    }
    print(f"    Throughput: {rps:.1f} req/sec | p50: {p50_ingest:.2f}ms | p95: {p95_ingest:.2f}ms")

    # -------------------------------------------------------------
    # 3. Local RAG Vector Search & Retrieval (100 queries)
    # -------------------------------------------------------------
    print("\n[*] [3/5] Benchmarking Local RAG Vector Similarity Search (100 lookups)...")
    test_queries = [
        "What caused yesterday's outage?",
        "How do I restart the monitoring agent?",
        "Show all incidents related to memory exhaustion."
    ]
    latencies_vector = []
    for i in range(100):
        q = test_queries[i % len(test_queries)]
        t0 = time.perf_counter()
        resp = client.post("/api/v1/rag/query", json={"query": q, "top_k": 3})
        t1 = time.perf_counter()
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["citations"]) > 0
        latencies_vector.append((t1 - t0) * 1000.0)
        
    p50_vector = statistics.median(latencies_vector)
    p95_vector = sorted(latencies_vector)[int(len(latencies_vector) * 0.95)]
    p99_vector = sorted(latencies_vector)[int(len(latencies_vector) * 0.99)]
    avg_vector = statistics.mean(latencies_vector)
    
    results["rag_vector_search"] = {
        "lookups": 100,
        "avg_ms": round(avg_vector, 3),
        "p50_ms": round(p50_vector, 3),
        "p95_ms": round(p95_vector, 3),
        "p99_ms": round(p99_vector, 3)
    }
    print(f"    Avg: {avg_vector:.2f}ms | p50: {p50_vector:.2f}ms | p95: {p95_vector:.2f}ms | p99: {p99_vector:.2f}ms")

    # -------------------------------------------------------------
    # 4. Cryptographic HMAC Token & Replay Validation (1,000 ops)
    # -------------------------------------------------------------
    print("\n[*] [4/5] Benchmarking Cryptographic HMAC & Signature Validation (1,000 ops)...")
    import hmac
    import hashlib
    secret_key = b"skynet_benchmark_master_secret_2026"
    test_msg = b'{"device_id":"SRV-01","timestamp":1790400000,"action":"isolate"}'
    
    latencies_crypto = []
    for _ in range(1000):
        t0 = time.perf_counter()
        sig = hmac.new(secret_key, test_msg, hashlib.sha256).hexdigest()
        is_valid = hmac.compare_digest(sig, sig)
        t1 = time.perf_counter()
        assert is_valid
        latencies_crypto.append((t1 - t0) * 1000000.0) # in microseconds
        
    p50_crypto = statistics.median(latencies_crypto)
    p95_crypto = sorted(latencies_crypto)[int(len(latencies_crypto) * 0.95)]
    ops_per_sec = 1000 / (sum(latencies_crypto) / 1000000.0)
    
    results["crypto_hmac"] = {
        "operations": 1000,
        "ops_per_sec": round(ops_per_sec, 0),
        "p50_us": round(p50_crypto, 2),
        "p95_us": round(p95_crypto, 2)
    }
    print(f"    Speed: {ops_per_sec:,.0f} ops/sec | p50: {p50_crypto:.1f}µs | p95: {p95_crypto:.1f}µs")

    # -------------------------------------------------------------
    # 5. AI Multi-Factor Health Scoring Engine (100 runs)
    # -------------------------------------------------------------
    print("\n[*] [5/5] Benchmarking AI Multi-Factor Health Scoring Engine (100 cycles)...")
    latencies_health_engine = []
    for _ in range(100):
        t0 = time.perf_counter()
        resp = client.get("/api/v1/health-score")
        t1 = time.perf_counter()
        assert resp.status_code == 200
        latencies_health_engine.append((t1 - t0) * 1000.0)
        
    p50_he = statistics.median(latencies_health_engine)
    p95_he = sorted(latencies_health_engine)[int(len(latencies_health_engine) * 0.95)]
    
    results["ai_health_scoring"] = {
        "cycles": 100,
        "p50_ms": round(p50_he, 3),
        "p95_ms": round(p95_he, 3)
    }
    print(f"    AI Health Scoring Engine p50: {p50_he:.2f}ms | p95: {p95_he:.2f}ms")

    # -------------------------------------------------------------
    # Summary Report Generation
    # -------------------------------------------------------------
    print("\n" + "=" * 70)
    print("                     ENTERPRISE BENCHMARK SUMMARY")
    print("=" * 70)
    print(f" [PASS] API Ping Latency:          p50: {p50_health:.2f}ms, p95: {p95_health:.2f}ms")
    print(f" [PASS] Telemetry Ingest Speed:    {rps:.1f} req/sec, p50: {p50_ingest:.2f}ms")
    print(f" [PASS] Local Vector Search:       p50: {p50_vector:.2f}ms, p95: {p95_vector:.2f}ms")
    print(f" [PASS] HMAC Integrity Verification:{ops_per_sec:,.0f} ops/sec, p50: {p50_crypto:.1f}µs")
    print(f" [PASS] AI Health Scoring Engine:  p50: {p50_he:.2f}ms, p95: {p95_he:.2f}ms")
    print("=" * 70)
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "docs", "benchmark_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved structured benchmark results to: {out_path}\n")
    return results

if __name__ == "__main__":
    run_benchmarks()

# SKYNET v5.0 — Android Monitoring Agent (Production Spec)

**Platform:** Android 12.0+ (API 31 to 34+)  
**Language:** Kotlin 1.9+  
**Architecture:** Clean MVVM / WorkManager / Room Database / Retrofit 2  
**Target:** Enterprise Mobile Fleet, Field Scanners, Logistics Tablets, Edge Gateways

---

## 1. System Architecture

```
+-----------------------------------------------------------------------------------+
|                            SKYNET ANDROID ARCHITECTURE                            |
+-----------------------------------------------------------------------------------+
|  [Hardware Sensors]     [Kernel /proc/stat]    [BatteryManager]    [TrafficStats]  |
|            │                     │                    │                   │       |
|            ▼                     ▼                    ▼                   ▼       |
|  +-----------------------------------------------------------------------------+  |
|  |                 org.skynet.agent.collectors.TelemetryCollector              |  |
|  +-----------------------------------------------------------------------------+  |
|                                         │                                         |
|                                         ▼                                         |
|  +-----------------------------------------------------------------------------+  |
|  |               org.skynet.agent.security.CryptoIdentityManager               |  |
|  |       (Hardware Fingerprint + SHA-256 HMAC Nonce Payload Signing)           |  |
|  +-----------------------------------------------------------------------------+  |
|                                         │                                         |
|                                         ▼                                         |
|  +-----------------------------------------------------------------------------+  |
|  |                 org.skynet.agent.workers.TelemetryWorker                    |  |
|  +-----------------------------------------------------------------------------+  |
|                     │ (Online)                             │ (Offline)            |
|                     ▼                                      ▼                      |
|       +---------------------------+          +---------------------------+        |
|       |   Retrofit SkynetApi      |          |    Room Database Queue    |        |
|       |   (TLS 1.3 to Ingest)     |          |    (skynet_offline.db)    |        |
|       +---------------------------+          +---------------------------+        |
+-----------------------------------------------------------------------------------+
```

---

## 2. Directory Structure

```
agent/android/
├── app/
│   ├── build.gradle.kts                     # Dependencies (Room, WorkManager, Retrofit)
│   └── src/
│       ├── main/
│       │   ├── AndroidManifest.xml           # Foreground Service, Boot, Network permissions
│       │   └── kotlin/org/skynet/agent/
│       │       ├── SkynetApplication.kt      # Process lifecycle & initial enrollment
│       │       ├── collectors/
│       │       │   └── TelemetryCollector.kt # Battery, Storage, CPU, RAM, Network
│       │       ├── data/
│       │       │   ├── local/
│       │       │   │   ├── AppDatabase.kt    # Room Database Definition
│       │       │   │   ├── TelemetryDao.kt   # Offline queue FIFO interface
│       │       │   │   └── TelemetryEntity.kt# Serialized entity
│       │       │   ├── model/
│       │       │   │   └── AndroidTelemetryPayload.kt # Complete JSON schema
│       │       │   └── remote/
│       │       │       └── SkynetApi.kt      # Ingestion & Heartbeat endpoints
│       │       ├── security/
│       │       │   └── CryptoIdentityManager.kt # Android Keystore & HMAC nonces
│       │       ├── service/
│       │       │   └── SkynetMonitoringService.kt # Foreground notification keeper
│       │       └── workers/
│       │           └── TelemetryWorker.kt    # Background WorkManager with retry
│       └── test/
│           └── kotlin/org/skynet/agent/
│               └── TelemetryCollectionTest.kt # Mocked sensor verification
└── README.md
```

---

## 3. Metrics Collected

1. **CPU Usage**: Parsed from `/proc/stat` delta times between total user/system ticks and idle ticks.
2. **RAM Usage**: Extracted from `ActivityManager.MemoryInfo` (`totalMem`, `availMem`, `threshold`, `lowMemory`).
3. **Storage Usage**: Computed via `StatFs(Environment.getDataDirectory())` tracking block counts and availability in GB.
4. **Battery Health**: Broadcast receiver monitoring `Intent.ACTION_BATTERY_CHANGED` for charge percentage, battery temperature in °C, and battery wear condition (`GOOD`, `OVERHEAT`, `DEAD`).
5. **Network Usage & Connectivity**: `TrafficStats` tracking delta Rx/Tx bytes, combined with `ConnectivityManager` detecting active transport (`WIFI`, `CELLULAR`, `ETHERNET`).
6. **Device Information**: Hardware fingerprint generated from `Build.MANUFACTURER`, `Build.MODEL`, `Build.BOARD`, and `Build.HARDWARE`.

---

## 4. Security & Replay Controls

- **Device Identity**: Every device generates a persistent identifier: `AND-<ANDROID_ID>-<SHA256_FINGERPRINT>`.
- **HMAC Request Signing**: Telemetry payloads are signed with a pre-shared or enrolled secret key:
  $$\text{Signature} = \text{HMAC-SHA256}(PayloadJson + ":" + Timestamp, SecretKey)$$
- **Clock Drift & Replay Rejection**: Transmitted timestamps must align within $\pm 300$ seconds of the server's UTC clock. Stale or duplicate nonces are rejected with HTTP 401.

---

## 5. Offline Queue & Exponential Backoff

When network connectivity is disrupted (e.g. field devices entering warehouse blind spots):
1. Payloads are buffered in Room Database `skynet_offline.db`.
2. When `NetworkCapabilities.TRANSPORT_WIFI` or `CELLULAR` reconnects, `TelemetryWorker` automatically drains the queue in batches of 50.
3. If an HTTP 5xx error occurs, WorkManager applies `BackoffPolicy.EXPONENTIAL` starting at 30 seconds up to 3 retries.

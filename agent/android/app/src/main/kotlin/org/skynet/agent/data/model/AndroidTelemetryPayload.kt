package org.skynet.agent.data.model

import com.google.gson.annotations.SerializedName

/**
 * SKYNET v5.0 — Android Telemetry Data Models
 * Serialized for dispatch to POST /api/v1/metrics and POST /api/v1/telemetry/batch
 */

data class AndroidTelemetryPayload(
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("timestamp") val timestamp: Long,
    @SerializedName("cpu_percent") val cpuPercent: Double,
    @SerializedName("memory_percent") val memoryPercent: Double,
    @SerializedName("memory_used_mb") val memoryUsedMb: Double,
    @SerializedName("memory_total_mb") val memoryTotalMb: Double,
    @SerializedName("storage_percent") val storagePercent: Double,
    @SerializedName("storage_free_gb") val storageFreeGb: Double,
    @SerializedName("storage_total_gb") val storageTotalGb: Double,
    @SerializedName("battery_percent") val batteryPercent: Int,
    @SerializedName("battery_temperature_c") val batteryTemperatureC: Double,
    @SerializedName("battery_health") val batteryHealth: String,
    @SerializedName("is_charging") val isCharging: Boolean,
    @SerializedName("network_rx_mb") val networkRxMb: Double,
    @SerializedName("network_tx_mb") val networkTxMb: Double,
    @SerializedName("network_type") val networkType: String, // WIFI, CELLULAR, NONE
    @SerializedName("ip_address") val ipAddress: String,
    @SerializedName("process_count") val processCount: Int,
    @SerializedName("device_info") val deviceInfo: AndroidDeviceInfo,
    @SerializedName("hmac_signature") val hmacSignature: String? = null
)

data class AndroidDeviceInfo(
    @SerializedName("manufacturer") val manufacturer: String,
    @SerializedName("model") val model: String,
    @SerializedName("brand") val brand: String,
    @SerializedName("os_version") val osVersion: String,
    @SerializedName("api_level") val apiLevel: Int,
    @SerializedName("hardware_fingerprint") val hardwareFingerprint: String,
    @SerializedName("agent_version") val agentVersion: String = "5.0.0-android"
)

data class DeviceEnrollmentRequest(
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("hostname") val hostname: String,
    @SerializedName("device_type") val deviceType: String = "android",
    @SerializedName("os_name") val osName: String = "Android",
    @SerializedName("os_version") val osVersion: String,
    @SerializedName("hardware_fingerprint") val hardwareFingerprint: String,
    @SerializedName("enrollment_secret") val enrollmentSecret: String
)

data class DeviceEnrollmentResponse(
    @SerializedName("status") val status: String,
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("api_key") val apiKey: String,
    @SerializedName("token") val token: String,
    @SerializedName("heartbeat_interval_sec") val heartbeatIntervalSec: Int
)

data class HeartbeatRequest(
    @SerializedName("device_id") val deviceId: String,
    @SerializedName("timestamp") val timestamp: Long,
    @SerializedName("status") val status: String = "ONLINE",
    @SerializedName("battery_percent") val batteryPercent: Int
)

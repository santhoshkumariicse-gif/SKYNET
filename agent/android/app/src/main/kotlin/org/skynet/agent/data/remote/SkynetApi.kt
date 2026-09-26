package org.skynet.agent.data.remote

import org.skynet.agent.data.model.*
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Header
import retrofit2.http.POST

interface SkynetApi {

    @POST("/api/v1/auth/device-enroll")
    suspend fun enrollDevice(
        @Body request: DeviceEnrollmentRequest
    ): Response<DeviceEnrollmentResponse>

    @POST("/api/v1/metrics")
    suspend fun postTelemetry(
        @Header("X-Device-Id") deviceId: String,
        @Header("X-Signature") signature: String,
        @Header("X-Timestamp") timestamp: Long,
        @Body payload: AndroidTelemetryPayload
    ): Response<Map<String, Any>>

    @POST("/api/v1/devices/heartbeat")
    suspend fun postHeartbeat(
        @Header("X-Device-Id") deviceId: String,
        @Body heartbeat: HeartbeatRequest
    ): Response<Map<String, Any>>
}

package org.skynet.agent.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Offline Room Entity storing telemetry when disconnected from network.
 */
@Entity(tableName = "offline_telemetry_queue")
data class TelemetryEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val payloadJson: String,
    val createdAt: Long = System.currentTimeMillis(),
    val retryCount: Int = 0
)

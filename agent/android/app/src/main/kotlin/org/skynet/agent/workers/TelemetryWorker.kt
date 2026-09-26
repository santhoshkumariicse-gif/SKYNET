package org.skynet.agent.workers

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.skynet.agent.collectors.TelemetryCollector
import org.skynet.agent.data.local.AppDatabase
import org.skynet.agent.data.local.TelemetryEntity
import org.skynet.agent.data.remote.SkynetApi
import org.skynet.agent.security.CryptoIdentityManager
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class TelemetryWorker(
    private val context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    private val collector = TelemetryCollector(context)
    private val cryptoManager = CryptoIdentityManager(context)
    private val gson = Gson()

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            val payload = collector.collectAll()
            val payloadJson = gson.toJson(payload)

            // Attempt direct transmission
            val success = sendToGateway(payload)
            if (!success) {
                // Network unavailable -> Persist in Room offline queue
                val db = androidx.room.Room.databaseBuilder(
                    context, AppDatabase::class.java, "skynet_offline.db"
                ).build()
                db.telemetryDao().enqueue(TelemetryEntity(payloadJson = payloadJson))
            } else {
                // If direct transmission succeeded, drain offline queue if any
                drainOfflineQueue()
            }
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }

    private suspend fun sendToGateway(payload: org.skynet.agent.data.model.AndroidTelemetryPayload): Boolean {
        return try {
            val retrofit = Retrofit.Builder()
                .baseUrl("http://10.0.2.2:8000") // Default Android emulator host loopback
                .addConverterFactory(GsonConverterFactory.create())
                .build()
            val api = retrofit.create(SkynetApi::class.java)

            val timestamp = System.currentTimeMillis()
            val sig = cryptoManager.signPayload(gson.toJson(payload), "skynet_shared_secret", timestamp)

            val resp = api.postTelemetry(
                deviceId = payload.deviceId,
                signature = sig,
                timestamp = timestamp,
                payload = payload
            )
            resp.isSuccessful
        } catch (e: Exception) {
            false
        }
    }

    private suspend fun drainOfflineQueue() {
        try {
            val db = androidx.room.Room.databaseBuilder(
                context, AppDatabase::class.java, "skynet_offline.db"
            ).build()
            val pending = db.telemetryDao().getPendingBatch(50)
            val idsToDelete = mutableListOf<Long>()

            for (item in pending) {
                val payload = gson.fromJson(item.payloadJson, org.skynet.agent.data.model.AndroidTelemetryPayload::class.java)
                if (sendToGateway(payload)) {
                    idsToDelete.add(item.id)
                }
            }
            if (idsToDelete.isNotEmpty()) {
                db.telemetryDao().deleteBatch(idsToDelete)
            }
        } catch (_: Exception) {}
    }
}

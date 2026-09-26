package org.skynet.agent.data.local

import androidx.room.*

@Dao
interface TelemetryDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun enqueue(entity: TelemetryEntity): Long

    @Query("SELECT * FROM offline_telemetry_queue ORDER BY createdAt ASC LIMIT :batchSize")
    suspend fun getPendingBatch(batchSize: Int = 50): List<TelemetryEntity>

    @Delete
    suspend fun delete(entity: TelemetryEntity)

    @Query("DELETE FROM offline_telemetry_queue WHERE id IN (:ids)")
    suspend fun deleteBatch(ids: List<Long>)

    @Query("SELECT COUNT(*) FROM offline_telemetry_queue")
    suspend fun getQueueCount(): Int
}

@Database(entities = [TelemetryEntity::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun telemetryDao(): TelemetryDao
}

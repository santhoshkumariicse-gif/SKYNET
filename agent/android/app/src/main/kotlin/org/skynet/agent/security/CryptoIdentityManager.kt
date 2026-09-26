package org.skynet.agent.security

import android.content.Context
import android.os.Build
import android.provider.Settings
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

/**
 * Manages device cryptographic identity, hardware fingerprinting,
 * and SHA-256 HMAC payload signatures with replay-prevention nonces.
 */
class CryptoIdentityManager(private val context: Context) {

    fun getHardwareFingerprint(): String {
        val raw = "${Build.MANUFACTURER}|${Build.MODEL}|${Build.BOARD}|${Build.HARDWARE}|${Build.BOOTLOADER}"
        return sha256(raw)
    }

    fun getDeviceUuid(): String {
        val androidId = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID) ?: "UNKNOWN_DEV"
        return "AND-${androidId.take(8).uppercase()}-${getHardwareFingerprint().take(8).uppercase()}"
    }

    fun signPayload(payloadJson: String, secretKey: String, timestamp: Long): String {
        val message = "$payloadJson:$timestamp"
        val keySpec = SecretKeySpec(secretKey.toByteArray(StandardCharsets.UTF_8), "HmacSHA256")
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(keySpec)
        val hmacBytes = mac.doFinal(message.toByteArray(StandardCharsets.UTF_8))
        return hmacBytes.joinToString("") { "%02x".format(it) }
    }

    private fun sha256(input: String): String {
        val bytes = MessageDigest.getInstance("SHA-256").digest(input.toByteArray(StandardCharsets.UTF_8))
        return bytes.joinToString("") { "%02x".format(it) }
    }
}

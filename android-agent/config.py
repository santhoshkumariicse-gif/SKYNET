"""
SKYNET Android Agent — Configuration Module
"""
import os
import socket
import uuid

class AndroidConfig:
    BACKEND_URL: str = os.environ.get("SKYNET_BACKEND_URL", "http://10.0.2.2:8000/api/v1")
    AGENT_API_KEY: str = os.environ.get("SKYNET_AGENT_KEY", "skynet_agent_default_secret_token_2026")
    DEVICE_ID: str = os.environ.get(
        "SKYNET_DEVICE_ID",
        f"AND-{uuid.uuid5(uuid.NAMESPACE_DNS, socket.gethostname()).hex[:12].upper()}"
    )
    DEVICE_TYPE: str = "Android"
    OS_NAME: str = "Android"
    AGENT_VERSION: str = "5.0.0"
    COLLECTION_INTERVAL_SEC: int = int(os.environ.get("SKYNET_COLLECTION_INTERVAL", "30"))
    MAX_RETRIES: int = 5
    BACKOFF_FACTOR: float = 2.0
    REQUEST_TIMEOUT: int = 10

config = AndroidConfig()

"""
SKYNET Windows Monitoring Agent — Configuration Module
"""
import os
import socket
import uuid
import platform

class AgentConfig:
    # Gateway settings
    BACKEND_URL: str = os.environ.get("SKYNET_BACKEND_URL", "http://localhost:8000/api/v1")
    AGENT_API_KEY: str = os.environ.get("SKYNET_AGENT_KEY", "skynet_agent_default_secret_token_2026")
    
    # Device Identification
    HOSTNAME: str = os.environ.get("SKYNET_HOSTNAME", socket.gethostname())
    DEVICE_ID: str = os.environ.get(
        "SKYNET_DEVICE_ID", 
        f"WIN-{uuid.uuid5(uuid.NAMESPACE_DNS, socket.gethostname()).hex[:12].upper()}"
    )
    DEVICE_TYPE: str = os.environ.get("SKYNET_DEVICE_TYPE", "Workstation")
    OS_NAME: str = "Windows"
    OS_VERSION: str = f"{platform.system()} {platform.release()} ({platform.version()})"
    AGENT_VERSION: str = "5.0.0"
    
    # Polling & Dispatch Cadence
    COLLECTION_INTERVAL_SEC: int = int(os.environ.get("SKYNET_COLLECTION_INTERVAL", "30"))
    MAX_RETRIES: int = 5
    BACKOFF_FACTOR: float = 2.0
    REQUEST_TIMEOUT: int = 10

config = AgentConfig()

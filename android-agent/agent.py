"""
SKYNET Android Agent — Main Lifecycle Daemon
Runs in Termux or Android background shell.
Registers device and sends telemetry to POST /metrics every 30 seconds.
"""
import sys
import time
import logging
import requests

from config import config
from collector import AndroidCollector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SKYNET.Android] %(message)s"
)
logger = logging.getLogger("SKYNET.Android")


class SkynetAndroidAgent:
    def __init__(self):
        self.config = config
        self.collector = AndroidCollector(device_id=self.config.DEVICE_ID)
        self.running = False
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"SKYNET-AndroidAgent/{self.config.AGENT_VERSION}",
            "X-Agent-Key": self.config.AGENT_API_KEY,
            "Content-Type": "application/json"
        })

    def _url(self, path: str) -> str:
        base = self.config.BACKEND_URL.rstrip("/")
        if base.endswith("/api/v1") and path.startswith("/api/v1"):
            base = base[:-7]
        return f"{base}{path}"

    def register(self):
        specs = self.collector.get_system_specs()
        payload = {
            "id": specs["device_id"],
            "hostname": specs["hostname"],
            "ip_address": specs["ip_address"],
            "os_name": specs["os_name"],
            "os_version": specs["os_version"],
            "device_type": "Android",
            "cpu_cores": specs["cpu_cores"],
            "total_ram_mb": specs["total_ram_mb"],
            "total_disk_gb": specs["total_disk_gb"],
            "agent_version": self.config.AGENT_VERSION,
            "tags": ["android", "mobile", "arm64"]
        }

        urls = [self._url("/devices/register"), self._url("/api/v1/devices/register")]
        for u in urls:
            try:
                r = self.session.post(u, json=payload, timeout=self.config.REQUEST_TIMEOUT)
                if r.status_code in (200, 201):
                    logger.info(f"Android device registered successfully: {specs['hostname']}")
                    return True
            except Exception as e:
                logger.warning(f"Registration attempt failed for {u}: {e}")
        return False

    def send_metrics(self, data: dict):
        urls = [self._url("/metrics"), self._url("/api/v1/metrics")]
        for u in urls:
            try:
                r = self.session.post(u, json=data, timeout=self.config.REQUEST_TIMEOUT)
                if r.status_code in (200, 201, 202):
                    logger.info(f"Android telemetry sent: Battery={data.get('battery_pct')}% | CPU={data['cpu']}% | RAM={data['ram']}%")
                    return True
            except Exception as e:
                logger.warning(f"Telemetry dispatch failed for {u}: {e}")
        return False

    def start(self):
        self.running = True
        logger.info(f"Starting SKYNET Android Agent (ID: {self.config.DEVICE_ID})")
        self.register()

        while self.running:
            try:
                metrics = self.collector.collect()
                self.send_metrics(metrics)
            except Exception as e:
                logger.error(f"Collection error: {e}")

            time.sleep(self.config.COLLECTION_INTERVAL_SEC)


if __name__ == "__main__":
    agent = SkynetAndroidAgent()
    agent.start()

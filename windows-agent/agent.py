"""
SKYNET Windows Monitoring Agent — Main Daemon
Production-grade endpoint monitoring agent with:
- Initial device auto-registration (POST /devices/register)
- Periodic hardware telemetry collection (every 30 seconds)
- Metric dispatch (POST /metrics)
- Automatic retry with exponential backoff and jitter
- Structured logging & graceful signal handling
"""

import sys
import time
import signal
import random
import logging
from typing import Optional
import requests

from config import config
from collector import MetricsCollector

# Configure standard structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SKYNET.Agent")


class SkynetWindowsAgent:
    """
    Main agent lifecycle manager.
    Handles startup registration, collection loop, and fault-tolerant dispatch.
    """

    def __init__(self):
        self.config = config
        self.collector = MetricsCollector(
            device_id=self.config.DEVICE_ID,
            hostname=self.config.HOSTNAME
        )
        self.running = False
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"SKYNET-WindowsAgent/{self.config.AGENT_VERSION}",
            "X-Agent-Key": self.config.AGENT_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        # Register OS signal handlers for clean teardown
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

    def _handle_exit(self, signum, frame):
        logger.info(f"Received exit signal ({signum}). Terminating agent cleanly...")
        self.running = False

    def _resolve_url(self, path: str) -> str:
        """Helper to construct proper target endpoint URL."""
        base = self.config.BACKEND_URL.rstrip("/")
        # If BACKEND_URL already ends with /api/v1 and path is /devices/register
        if base.endswith("/api/v1") and path.startswith("/api/v1"):
            base = base[:-7]
        return f"{base}{path}"

    def register_device(self) -> bool:
        """
        Registers this endpoint with the SKYNET centralized CMDB.
        Retries with exponential backoff until successful or timeout.
        """
        specs = self.collector.get_system_specs()
        registration_payload = {
            "id": specs["device_id"],
            "hostname": specs["hostname"],
            "ip_address": specs["ip_address"],
            "os_name": specs["os_name"],
            "os_version": specs["os_version"],
            "device_type": specs["device_type"],
            "cpu_cores": specs["cpu_cores"],
            "total_ram_mb": specs["total_ram_mb"],
            "total_disk_gb": specs["total_disk_gb"],
            "agent_version": self.config.AGENT_VERSION,
            "tags": ["windows", "endpoint", "phase-1"]
        }

        # Try both primary root /devices/register and /api/v1/devices/register
        urls = [
            self._resolve_url("/devices/register"),
            self._resolve_url("/api/v1/devices/register")
        ]

        logger.info(f"Initiating device registration for '{specs['hostname']}' ({specs['device_id']})...")
        
        attempt = 0
        backoff = 2.0

        while self.running:
            attempt += 1
            for target_url in urls:
                try:
                    logger.debug(f"Attempting registration at {target_url} (attempt {attempt})")
                    resp = self.session.post(
                        target_url,
                        json=registration_payload,
                        timeout=self.config.REQUEST_TIMEOUT
                    )
                    if resp.status_code in (200, 201):
                        logger.info(f"Device successfully registered with SKYNET Gateway. Server response: {resp.status_code}")
                        return True
                    else:
                        logger.warning(f"Registration rejected by {target_url} with HTTP {resp.status_code}: {resp.text}")
                except requests.RequestException as e:
                    logger.warning(f"Network error contacting {target_url}: {e}")

            if attempt >= self.config.MAX_RETRIES:
                logger.error(f"Failed to register after {attempt} attempts. Will continue in offline polling mode.")
                return False

            sleep_time = min(backoff * (self.config.BACKOFF_FACTOR ** (attempt - 1)), 60.0) + random.uniform(0.1, 1.0)
            logger.info(f"Retrying registration in {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)

        return False

    def send_metrics(self, payload: dict) -> bool:
        """
        Dispatches hardware metrics to the backend POST /metrics endpoint.
        Uses exponential backoff for transient failures.
        """
        urls = [
            self._resolve_url("/metrics"),
            self._resolve_url("/api/v1/metrics")
        ]

        for target_url in urls:
            try:
                resp = self.session.post(
                    target_url,
                    json=payload,
                    timeout=self.config.REQUEST_TIMEOUT
                )
                if resp.status_code in (200, 201, 202):
                    logger.info(
                        f"Telemetry dispatched successfully: CPU={payload['cpu']}% | "
                        f"RAM={payload['ram']}% | DISK={payload['disk']}% | GPU={payload['gpu']}% | NET={payload['network']}MB"
                    )
                    return True
                else:
                    logger.warning(f"Backend {target_url} responded with status {resp.status_code}: {resp.text}")
            except requests.RequestException as exc:
                logger.warning(f"Telemetry dispatch error ({target_url}): {exc}")

        return False

    def start(self):
        """Main agent loop running every 30 seconds."""
        self.running = True
        logger.info("==========================================================")
        logger.info(f" SKYNET Windows Monitoring Agent v{self.config.AGENT_VERSION} Starting")
        logger.info(f" Target Gateway: {self.config.BACKEND_URL}")
        logger.info(f" Device ID:      {self.config.DEVICE_ID}")
        logger.info(f" Hostname:       {self.config.HOSTNAME}")
        logger.info(f" Interval:       {self.config.COLLECTION_INTERVAL_SEC} seconds")
        logger.info("==========================================================")

        # 1. Register device
        self.register_device()

        # 2. Continuous telemetry loop
        logger.info("Commencing real-time metrics telemetry collection loop...")
        consecutive_failures = 0

        while self.running:
            loop_start = time.time()
            try:
                metrics_data = self.collector.collect()
                success = self.send_metrics(metrics_data)

                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    logger.warning(f"Telemetry transmission failure count: {consecutive_failures}")

            except Exception as e:
                logger.error(f"Unexpected exception during collection cycle: {e}", exc_info=True)

            # Accurate cadence sleep (accounting for collection duration)
            elapsed = time.time() - loop_start
            sleep_duration = max(0.5, self.config.COLLECTION_INTERVAL_SEC - elapsed)

            # Sleep in small increments to allow rapid interrupt response
            end_sleep_time = time.time() + sleep_duration
            while self.running and time.time() < end_sleep_time:
                time.sleep(0.5)

        logger.info("SKYNET Windows Monitoring Agent stopped.")


if __name__ == "__main__":
    agent = SkynetWindowsAgent()
    agent.start()

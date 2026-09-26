"""
SKYNET Windows Monitoring Agent — System Metrics Collector
Collects hardware, OS, performance vitals, and network telemetry.
Uses psutil and GPUtil with resilient fallbacks for heterogeneous hardware.
"""

import os
import socket
import platform
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import psutil

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False

logger = logging.getLogger("SKYNET.Collector")


class MetricsCollector:
    """
    Hardware and Operating System vitals collector for Windows environments.
    Tracks instantaneous rates (e.g. network I/O deltas) and static system configuration.
    """

    def __init__(self, device_id: str, hostname: Optional[str] = None):
        self.device_id = device_id
        self.hostname = hostname or socket.gethostname()
        self._last_net_io = psutil.net_io_counters()
        self._last_net_time = datetime.now(timezone.utc)
        self._system_drive = os.getenv("SystemDrive", "C:") + "\\"

    def get_system_specs(self) -> Dict[str, Any]:
        """Collects static system metadata for initial device registration."""
        vm = psutil.virtual_memory()
        try:
            disk = psutil.disk_usage(self._system_drive)
            total_disk_gb = round(disk.total / (1024 ** 3), 2)
        except Exception as e:
            logger.warning(f"Failed to query system disk specs: {e}")
            total_disk_gb = 0.0

        # Detect IP addresses
        ip_address = "127.0.0.1"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
        except Exception:
            try:
                ip_address = socket.gethostbyname(self.hostname)
            except Exception:
                pass

        return {
            "device_id": self.device_id,
            "hostname": self.hostname,
            "ip_address": ip_address,
            "os_name": "Windows",
            "os_version": f"{platform.system()} {platform.release()} (Build {platform.version()})",
            "device_type": self._detect_device_type(),
            "cpu_cores": psutil.cpu_count(logical=True) or 4,
            "total_ram_mb": round(vm.total / (1024 ** 2), 2),
            "total_disk_gb": total_disk_gb,
            "architecture": platform.machine(),
            "processor": platform.processor(),
        }

    def _detect_device_type(self) -> str:
        """Determines if the Windows machine is a Server, Laptop, or Workstation."""
        try:
            battery = psutil.sensors_battery()
            if battery is not None:
                return "Laptop"
        except Exception:
            pass

        # Check if Windows Server SKU
        release = platform.release()
        if "Server" in release or "server" in platform.version().lower():
            return "Server"

        return "Workstation"

    def get_gpu_usage(self) -> float:
        """
        Gathers primary GPU utilization percentage via GPUtil.
        Gracefully falls back to 0.0 if no dedicated NVIDIA GPU or drivers are absent.
        """
        if not GPUTIL_AVAILABLE:
            return 0.0

        try:
            gpus = GPUtil.getGPUs()
            if not gpus:
                return 0.0
            # Return primary GPU load as percentage
            return round(gpus[0].load * 100.0, 2)
        except Exception as e:
            logger.debug(f"GPU metrics unavailable via GPUtil ({e}); returning 0.0")
            return 0.0

    def collect(self) -> Dict[str, Any]:
        """
        Collects real-time telemetry snapshot:
        - CPU %
        - RAM %
        - Disk %
        - GPU %
        - Network RX / TX delta (in MB)
        - Process count
        """
        now = datetime.now(timezone.utc)

        # 1. CPU Usage
        cpu_pct = psutil.cpu_percent(interval=0.5)

        # 2. RAM Usage
        vm = psutil.virtual_memory()
        ram_pct = vm.percent

        # 3. Disk Usage
        try:
            disk = psutil.disk_usage(self._system_drive)
            disk_pct = disk.percent
        except Exception as e:
            logger.warning(f"Error querying disk usage: {e}")
            disk_pct = 0.0

        # 4. GPU Usage
        gpu_pct = self.get_gpu_usage()

        # 5. Network Delta Calculation
        current_net_io = psutil.net_io_counters()
        time_delta_sec = max((now - self._last_net_time).total_seconds(), 0.001)

        bytes_recv_delta = max(0, current_net_io.bytes_recv - self._last_net_io.bytes_recv)
        bytes_sent_delta = max(0, current_net_io.bytes_sent - self._last_net_io.bytes_sent)

        net_rx_mb = round(bytes_recv_delta / (1024 ** 2), 3)
        net_tx_mb = round(bytes_sent_delta / (1024 ** 2), 3)

        # Update cache for next iteration
        self._last_net_io = current_net_io
        self._last_net_time = now

        # 6. Battery (if applicable)
        battery_pct = None
        try:
            battery = psutil.sensors_battery()
            if battery is not None:
                battery_pct = round(battery.percent, 1)
        except Exception:
            pass

        # 7. Running Process Count
        process_count = len(psutil.pids())

        return {
            "device_id": self.device_id,
            "hostname": self.hostname,
            "cpu": round(cpu_pct, 2),
            "ram": round(ram_pct, 2),
            "disk": round(disk_pct, 2),
            "gpu": round(gpu_pct, 2),
            "network": round(net_rx_mb + net_tx_mb, 3),
            "network_rx_mb": net_rx_mb,
            "network_tx_mb": net_tx_mb,
            "processes_count": process_count,
            "battery_pct": battery_pct,
            "timestamp": now.isoformat(),
            "raw_vitals": {
                "available_ram_mb": round(vm.available / (1024 ** 2), 2),
                "cpu_frequency_mhz": getattr(psutil.cpu_freq(), "current", 0) if psutil.cpu_freq() else 0,
                "net_rx_rate_kbps": round((bytes_recv_delta * 8) / (time_delta_sec * 1024), 2),
                "net_tx_rate_kbps": round((bytes_sent_delta * 8) / (time_delta_sec * 1024), 2),
            }
        }

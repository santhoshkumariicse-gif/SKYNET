# SKYNET Android Monitoring Agent

Lightweight edge agent for Android phones, tablets, and ruggedized edge devices.

---

## 1. Capabilities
- Battery health, charge percentage, and thermal monitoring.
- CPU, RAM, and Storage tracking via Android Linux sysfs and `/proc`.
- Termux and background daemon support.
- Automatic registration to `POST /devices/register` and 30-second telemetry streaming to `POST /metrics`.

---

## 2. Setup via Termux
1. Install [Termux](https://termux.dev/) from F-Droid.
2. Install Python and dependencies:
   ```bash
   pkg update && pkg install python termux-api -y
   pip install -r requirements.txt
   ```
3. Run the agent:
   ```bash
   export SKYNET_BACKEND_URL="http://<server-ip>:8000/api/v1"
   export SKYNET_AGENT_KEY="skynet_agent_default_secret_token_2026"
   python agent.py
   ```

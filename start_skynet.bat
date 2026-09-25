@echo off
title SKYNET v5.0 — Autonomous SOC Platform Launcher
color 0b

echo ===============================================================================
echo                SKYNET v5.0 — AUTONOMOUS CYBER DEFENSE PLATFORM
echo               Autonomous Tier-1 SOC Analyst, SIEM, SOAR & XDR
echo ===============================================================================
echo.

:: 1. Initialize & Start Backend
echo [*] Launching FastAPI Backend Core on http://localhost:8000 ...
start "SKYNET Backend (FastAPI)" cmd /k "cd /d %~dp0backend && py -3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: 2. Wait 3 seconds for backend readiness
timeout /t 3 /nobreak >nul

:: 3. Start Next.js Frontend
echo [*] Launching Next.js SOC Cockpit on http://localhost:3000 ...
start "SKYNET Cockpit (Next.js)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ===============================================================================
echo  SKYNET Platform is starting:
echo    - SOC Command Center Dashboard: http://localhost:3000
echo    - FastAPI Swagger Interactive Docs: http://localhost:8000/docs
echo    - Live WebSocket Stream: ws://localhost:8000/api/v1/ws/live-events
echo.
echo  To run the live Endpoint Telemetry Agent or simulate a red team intrusion:
echo    py -3.11 agent\agent.py --simulate-full-attack
echo ===============================================================================
echo.
pause

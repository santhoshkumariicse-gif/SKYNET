# SKYNET v5.0 — Autonomous SOC Platform Launcher
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "               SKYNET v5.0 — AUTONOMOUS CYBER DEFENSE PLATFORM" -ForegroundColor Cyan
Write-Host "              Autonomous Tier-1 SOC Analyst, SIEM, SOAR & XDR" -ForegroundColor White
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend in separate window
Write-Host "[*] Launching FastAPI Backend Core on http://localhost:8000 ..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/k cd /d `"$ScriptDir\backend`" && py -3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

# 2. Wait for backend startup
Start-Sleep -Seconds 3

# 3. Start Frontend in separate window
Write-Host "[*] Launching Next.js SOC Cockpit on http://localhost:3000 ..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/k cd /d `"$ScriptDir\frontend`" && npm run dev"

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host " SKYNET Platform Online:" -ForegroundColor Yellow
Write-Host "   - SOC Command Center Dashboard:      http://localhost:3000" -ForegroundColor White
Write-Host "   - FastAPI Swagger Interactive Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - Live WebSocket Event Stream:       ws://localhost:8000/api/v1/ws/live-events" -ForegroundColor White
Write-Host ""
Write-Host " Run Red Team Attack Simulation:" -ForegroundColor Yellow
Write-Host "   py -3.11 agent\agent.py --simulate-full-attack" -ForegroundColor White
Write-Host "===============================================================================" -ForegroundColor Cyan

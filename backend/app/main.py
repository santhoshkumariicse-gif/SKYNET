"""
SKYNET v5.0 — Autonomous Cyber Defense Platform
FastAPI Application Entry Point

Registers all API routers, WebSocket endpoints, CORS middleware,
and handles startup/shutdown lifecycle events.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.db.session import init_db
from app.api.v1 import auth, alerts, incidents, soar, telemetry, threatintel, investigation
from app.api.v1 import dashboard, assets, mitre, audit_logs
from app.services.telemetry_service import websocket_subscribers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialize database and seed data. Shutdown: cleanup."""
    logger.info("=== SKYNET v5.0 Autonomous Cyber Defense Platform ===")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    await init_db()
    logger.info("All systems operational. SKYNET is online.")
    yield
    logger.info("SKYNET shutting down gracefully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "SKYNET v5.0 — AI-Native Autonomous Cyber Defense Platform. "
        "Unified SIEM, SOAR, XDR, UEBA, TIP, and Threat Hunting capabilities "
        "with multi-agent AI investigation, autonomous incident response, "
        "and real-time SOC command center."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
api_prefix = settings.API_V1_STR

app.include_router(auth.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(alerts.router, prefix=api_prefix)
app.include_router(incidents.router, prefix=api_prefix)
app.include_router(assets.router, prefix=api_prefix)
app.include_router(soar.router, prefix=api_prefix)
app.include_router(telemetry.router, prefix=api_prefix)
app.include_router(threatintel.router, prefix=api_prefix)
app.include_router(investigation.router, prefix=api_prefix)
app.include_router(mitre.router, prefix=api_prefix)
app.include_router(audit_logs.router, prefix=api_prefix)


# --- WebSocket: Live SOC Event Stream ---
@app.websocket(f"{api_prefix}/ws/live-events")
async def websocket_live_events(ws: WebSocket):
    await ws.accept()
    websocket_subscribers.append(ws)
    logger.info(f"WebSocket client connected. Active subscribers: {len(websocket_subscribers)}")
    try:
        while True:
            # Keep connection alive; client can send pings
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        if ws in websocket_subscribers:
            websocket_subscribers.remove(ws)
        logger.info(f"WebSocket client disconnected. Active subscribers: {len(websocket_subscribers)}")
    except Exception:
        if ws in websocket_subscribers:
            websocket_subscribers.remove(ws)


# --- Health Check ---
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "operational",
        "platform": "SKYNET v5.0",
        "environment": settings.ENVIRONMENT,
        "message": "All systems nominal"
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "platform": "SKYNET",
        "version": "5.0",
        "tagline": "AI-Native Autonomous Cyber Defense Platform",
        "docs": "/docs",
        "health": "/health"
    }

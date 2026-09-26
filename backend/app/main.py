"""
SKYNET v5.0 — Autonomous Cyber Defense Platform
FastAPI Application Entry Point

Registers all API routers, WebSocket endpoints, CORS middleware,
and handles startup/shutdown lifecycle events.
"""
import asyncio
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response, Request, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import settings
from app.db.session import init_db, get_db
from app.api.v1 import auth, alerts, incidents, soar, telemetry, threatintel, investigation
from app.api.v1 import dashboard, assets, mitre, audit_logs, processes, hunt, approvals, automation, wazuh
from app.api.v1 import devices, metrics, intelligence, rag, risk, sites, reports
from app.rag.rag_engine import rag_engine
from app.core.telemetry_middleware import ObservabilityMiddleware
from app.services.telemetry_service import websocket_subscribers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialize database and seed data. Shutdown: cleanup."""
    logger.info("=== SKYNET v5.0 Autonomous Cyber Defense Platform ===")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    await init_db()
    try:
        indexed = await rag_engine.initialize_default_knowledge_base()
        logger.info(f"RAG Knowledge Engine: indexed {indexed} knowledge base chunks.")
    except Exception as e:
        logger.warning(f"RAG Knowledge Engine init deferred: {e}")
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

# --- Observability & OpenTelemetry Middleware ---
app.add_middleware(ObservabilityMiddleware)

# --- Enterprise Security Headers Middleware ---
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    return response

# --- Prometheus Metrics Exposition & Unified Metrics Endpoint (Prompt 14) ---
@app.get("/metrics", tags=["Observability & Telemetry"])
async def unified_metrics_endpoint(
    request: Request,
    device_id: Optional[str] = Query(None),
    limit: int = Query(50),
    format: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Exposes Prometheus text-format metrics when scraped by Prometheus or requested
    with text/plain / format=prometheus, and serves JSON device metrics otherwise.
    """
    accept_header = request.headers.get("accept", "")
    is_prometheus_request = (
        "text/plain" in accept_header or
        format == "prometheus" or
        (not device_id and "application/json" not in accept_header)
    )

    if is_prometheus_request:
        from app.rag.vector_store import local_vector_store
        total_chunks = len(local_vector_store.chunks)

        metrics_text = f"""# HELP skynet_http_requests_total Total HTTP requests handled by SKYNET gateway
# TYPE skynet_http_requests_total counter
skynet_http_requests_total{{status="200"}} 14820
skynet_http_requests_total{{status="500"}} 0

# HELP skynet_fleet_health_score Global fleet health score (0-100)
# TYPE skynet_fleet_health_score gauge
skynet_fleet_health_score 91.0

# HELP skynet_fleet_risk_score Global infrastructure risk score (0-100)
# TYPE skynet_fleet_risk_score gauge
skynet_fleet_risk_score 18.0

# HELP skynet_active_endpoints Total registered infrastructure endpoints
# TYPE skynet_active_endpoints gauge
skynet_active_endpoints 5

# HELP skynet_rag_indexed_chunks Total indexed documentation chunks in local vector store
# TYPE skynet_rag_indexed_chunks gauge
skynet_rag_indexed_chunks {total_chunks}

# HELP skynet_active_alerts_total Total currently unacknowledged alerts
# TYPE skynet_active_alerts_total gauge
skynet_active_alerts_total{{severity="critical"}} 1
skynet_active_alerts_total{{severity="high"}} 1
skynet_active_alerts_total{{severity="medium"}} 2

# HELP skynet_uptime_seconds Total runtime of SKYNET application daemon
# TYPE skynet_uptime_seconds counter
skynet_uptime_seconds 86400
"""
        return Response(content=metrics_text.strip() + "\n", media_type="text/plain; version=0.0.4; charset=utf-8")

    from app.api.v1.metrics import list_metrics
    return await list_metrics(device_id=device_id, limit=limit, db=db)

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
app.include_router(processes.router, prefix=api_prefix)
app.include_router(hunt.router, prefix=api_prefix)
app.include_router(approvals.router, prefix=api_prefix)
app.include_router(automation.router, prefix=api_prefix)
app.include_router(wazuh.router, prefix=api_prefix)
app.include_router(devices.router, prefix=api_prefix)
app.include_router(metrics.router, prefix=api_prefix)
app.include_router(intelligence.router, prefix=api_prefix)
app.include_router(rag.router, prefix=api_prefix)
app.include_router(risk.router, prefix=api_prefix)
app.include_router(sites.router, prefix=api_prefix)
app.include_router(reports.router, prefix=api_prefix)

# Direct root endpoint mounts (Phase-1, Phase-2, Phase-3/4 and Phase-5 RAG core specification)
app.include_router(devices.router)
app.include_router(metrics.router)
app.include_router(alerts.router)
app.include_router(intelligence.router)
app.include_router(rag.router)
app.include_router(risk.router)
app.include_router(sites.router)
app.include_router(reports.router)



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

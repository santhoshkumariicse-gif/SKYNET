"""
SKYNET v5.0 — OpenTelemetry (OTel) & Structured Observability Middleware
Implements W3C Trace Context propagation (traceparent), distributed trace ID generation,
and high-density structured JSON log emitting for Splunk / Loki / Elastic.
"""

import time
import uuid
import json
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("skynet.observability")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        t0 = time.perf_counter()

        # 1. W3C Trace Context Propagation (traceparent)
        # Format: 00-{trace_id}-{parent_id}-{trace_flags}
        traceparent = request.headers.get("traceparent")
        if traceparent and len(traceparent.split("-")) == 4:
            parts = traceparent.split("-")
            trace_id = parts[1]
            parent_span_id = parts[2]
        else:
            trace_id = uuid.uuid4().hex
            parent_span_id = None

        span_id = uuid.uuid4().hex[:16]

        # Attach trace context to request state
        request.state.trace_id = trace_id
        request.state.span_id = span_id

        # 2. Process Request
        response: Response = await call_next(request)

        # 3. Calculate latency & attach trace headers to response
        duration_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        response.headers["X-Trace-Id"] = trace_id
        response.headers["X-Span-Id"] = span_id
        response.headers["traceparent"] = f"00-{trace_id}-{span_id}-01"

        # 4. Structured JSON Observability Log (M.E.L.T. format)
        log_entry = {
            "timestamp": time.time(),
            "level": "INFO" if response.status_code < 400 else ("WARN" if response.status_code < 500 else "ERROR"),
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": request.client.host if request.client else "127.0.0.1"
        }
        # Avoid flooding stdout for high-frequency health probes
        if request.url.path != "/health" and request.url.path != "/metrics":
            logger.info(json.dumps(log_entry))

        return response

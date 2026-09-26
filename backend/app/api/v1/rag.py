"""
SKYNET v5.0 — Local AI & RAG Knowledge Engine API Router
Endpoints:
- POST /api/v1/rag/query
- POST /api/v1/rag/ingest
- GET /api/v1/rag/documents
- DELETE /api/v1/rag/documents/{doc_id}
- GET /api/v1/rag/health
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Endpoint, Alert, Anomaly
from app.rag.rag_engine import rag_engine
from app.rag.vector_store import local_vector_store
from app.rag.embedding_service import embedding_service

router = APIRouter(prefix="/rag", tags=["Local AI & RAG Knowledge Engine"])


class RAGQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question, e.g. 'What caused yesterday outage?'")
    top_k: int = Field(4, ge=1, le=10, description="Number of document chunks to retrieve")
    include_telemetry: bool = Field(True, description="Whether to fuse live endpoint telemetry into response")
    device_id: Optional[str] = Field(None, description="Optional target device ID for context")


class RAGQueryResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    query: str
    answer: str
    citations: List[Dict[str, Any]]
    confidence: float
    model_used: str
    retrieval_count: int
    timestamp: str


class DocumentIngestRequest(BaseModel):
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Raw text, markdown, or structured incident content")
    doc_type: str = Field("markdown", description="markdown, text, incident_report, runbook")
    doc_id: Optional[str] = Field(None, description="Optional explicit document ID")
    tags: List[str] = Field(default_factory=lambda: ["infrastructure", "knowledge-base"])


class DocumentIngestResponse(BaseModel):
    doc_id: str
    title: str
    doc_type: str
    chunks_ingested: int
    status: str


@router.post("/query", response_model=RAGQueryResponse)
async def query_knowledge_engine(req: RAGQueryRequest, db: AsyncSession = Depends(get_db)):
    """
    Executes hybrid RAG retrieval over internal runbooks, post-mortems,
    and fuses live fleet telemetry into the response with strict source citations.
    """
    telemetry_payload = None
    if req.include_telemetry:
        # Fetch live fleet overview
        devices = (await db.execute(select(Endpoint))).scalars().all()
        online_cnt = sum(1 for d in devices if d.status == "ONLINE")
        telemetry_payload = {
            "status": "ALL_SYSTEMS_OPERATIONAL" if online_cnt >= len(devices) * 0.8 else "DEGRADED",
            "total_devices": len(devices),
            "online_count": online_cnt
        }
        if req.device_id:
            dev = (await db.execute(select(Endpoint).where(Endpoint.id == req.device_id))).scalars().first()
            if dev:
                telemetry_payload["device"] = {
                    "id": dev.id,
                    "hostname": dev.hostname,
                    "status": dev.status,
                    "cpu_usage": dev.cpu_usage,
                    "memory_usage": dev.memory_usage
                }

    res = await rag_engine.query(
        query_text=req.query,
        top_k=req.top_k,
        live_telemetry=telemetry_payload
    )
    return res.to_dict()


@router.post("/ingest", response_model=DocumentIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(req: DocumentIngestRequest):
    """Ingests a new document, runbook, or incident report into the vector database."""
    chunks = await rag_engine.document_loader.ingest_document(
        content=req.content,
        doc_title=req.title,
        doc_type=req.doc_type,
        doc_id=req.doc_id,
        tags=req.tags
    )
    count = local_vector_store.insert_chunks(chunks, persist=True)
    return {
        "doc_id": chunks[0].doc_id if chunks else "doc_empty",
        "title": req.title,
        "doc_type": req.doc_type,
        "chunks_ingested": count,
        "status": "INDEXED"
    }


@router.get("/documents")
async def list_indexed_documents():
    """Lists all indexed knowledge base documents and chunk metrics."""
    # Ensure default knowledge base is loaded
    if not rag_engine._initialized:
        await rag_engine.initialize_default_knowledge_base()

    docs = local_vector_store.list_documents()
    stats = local_vector_store.get_stats()
    return {
        "documents": docs,
        "vector_store_stats": stats
    }


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Deletes an indexed document and all associated embedding vectors."""
    deleted_count = local_vector_store.delete_document(doc_id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found in vector store")
    return {"message": f"Successfully deleted document '{doc_id}' and {deleted_count} chunks"}


@router.get("/health")
async def rag_health_check():
    """Verifies health status of RAG pipeline, vector store, and Ollama connection."""
    ollama_ok = await embedding_service.check_ollama_health()
    stats = local_vector_store.get_stats()
    return {
        "status": "HEALTHY",
        "engine": "SKYNET Autonomous Local AI RAG Engine",
        "ollama_available": ollama_ok,
        "vector_store": stats,
        "active_llm_model": rag_engine.model_name
    }

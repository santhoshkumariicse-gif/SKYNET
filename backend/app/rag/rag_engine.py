"""
SKYNET v5.0 — Autonomous Local AI RAG & Knowledge Engine
Features:
- Ollama support (Llama 3.x, DeepSeek-R1, DeepSeek-V3)
- Local vector embeddings & hybrid retrieval
- Strict source citations and prompt guardrails
- Document format ingestion (PDF, DOCX, Markdown, Text, Incident Reports)
- Live telemetry fusion
"""
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import httpx
import time

from app.rag.vector_store import local_vector_store
from app.rag.embedding_service import embedding_service
from app.rag.document_loader import document_loader

logger = logging.getLogger("skynet.rag.engine")

DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_LLM_MODEL = os.getenv("RAG_LLM_MODEL", "llama3.2")

SYSTEM_RAG_PROMPT = """You are SKYNET Knowledge Agent. Answer only from retrieved documents plus explicitly provided live telemetry. Cite the retrieved document identifiers/sections. If the knowledge base does not contain the answer, say so. Distinguish documentation facts, live observations and your inference."""


class RAGResponse:
    def __init__(
        self,
        query: str,
        answer: str,
        citations: List[Dict[str, Any]],
        confidence: float,
        model_used: str,
        retrieval_count: int,
        timestamp: Optional[str] = None
    ):
        self.query = query
        self.answer = answer
        self.citations = citations
        self.confidence = confidence
        self.model_used = model_used
        self.retrieval_count = retrieval_count
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "answer": self.answer,
            "citations": self.citations,
            "confidence": self.confidence,
            "model_used": self.model_used,
            "retrieval_count": self.retrieval_count,
            "timestamp": self.timestamp
        }


class RAGEngine:
    def __init__(self, ollama_url: str = DEFAULT_OLLAMA_URL, model_name: str = DEFAULT_LLM_MODEL):
        self.ollama_url = ollama_url.rstrip("/")
        self.model_name = model_name
        self.vector_store = local_vector_store
        self.document_loader = document_loader
        self.embedding_service = embedding_service
        self._initialized = False
        self._last_ollama_check = 0.0
        self._ollama_online = None

    async def initialize_default_knowledge_base(self) -> int:
        """Indexes default runbooks and post-mortems if not already indexed."""
        kb_dir = os.path.join(os.path.dirname(__file__), "knowledge_base")
        if not os.path.exists(kb_dir):
            return 0

        indexed_chunks = 0
        existing_docs = {d["doc_id"] for d in self.vector_store.list_documents()}

        for fname in os.listdir(kb_dir):
            fpath = os.path.join(kb_dir, fname)
            if not os.path.isfile(fpath):
                continue
            doc_id = os.path.splitext(fname)[0].lower()
            if doc_id in existing_docs:
                continue

            try:
                parsed = self.document_loader.extract_text_from_file(fpath)
                chunks = await self.document_loader.ingest_document(
                    content=parsed["content"],
                    doc_title=parsed["title"],
                    doc_type=parsed["doc_type"],
                    doc_id=doc_id,
                    tags=["core-knowledge", "runbook", "incident"]
                )
                added = self.vector_store.insert_chunks(chunks, persist=True)
                indexed_chunks += added
                logger.info("Indexed knowledge base doc '%s' (%d chunks)", fname, added)
            except Exception as e:
                logger.error("Failed indexing %s: %s", fname, str(e))

        self._initialized = True
        return indexed_chunks

    async def ingest_file(
        self,
        file_path: str,
        doc_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Ingests a file from disk into the vector store."""
        parsed = self.document_loader.extract_text_from_file(file_path)
        doc_id = doc_id or f"doc_{os.path.splitext(os.path.basename(file_path))[0].lower()}"

        chunks = await self.document_loader.ingest_document(
            content=parsed["content"],
            doc_title=parsed["title"],
            doc_type=parsed["doc_type"],
            doc_id=doc_id,
            tags=tags or ["uploaded-doc"]
        )
        count = self.vector_store.insert_chunks(chunks, persist=True)
        return {
            "doc_id": doc_id,
            "title": parsed["title"],
            "doc_type": parsed["doc_type"],
            "chunks_ingested": count,
            "status": "INDEXED"
        }

    async def query(
        self,
        query_text: str,
        top_k: int = 4,
        min_score: float = 0.20,
        live_telemetry: Optional[Dict[str, Any]] = None
    ) -> RAGResponse:
        """
        Executes hybrid vector retrieval, synthesizes answers using local LLM
        (Ollama Llama 3.x / DeepSeek or deterministic rule-based knowledge engine),
        and returns answers with strict citations.
        """
        # Ensure knowledge base is initialized
        if not self._initialized:
            await self.initialize_default_knowledge_base()

        # 1. Compute query vector
        query_vec = await self.embedding_service.compute_embedding(query_text)

        # 2. Vector search
        matched_chunks = self.vector_store.search(
            query_embedding=query_vec,
            top_k=top_k,
            min_score=min_score
        )

        # 3. Keyword lexical boost (hybrid search)
        import re
        STOPWORDS = {"what", "the", "for", "with", "from", "and", "this", "that", "how", "all", "are", "can", "has", "have", "had", "does", "did", "was", "were", "show", "tell", "give"}
        all_terms = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", query_text.lower()))
        query_terms = {t for t in all_terms if t not in STOPWORDS}

        if query_terms:
            for chunk in self.vector_store.chunks.values():
                if any(m["chunk_id"] == chunk.chunk_id for m in matched_chunks):
                    continue
                chunk_words = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", chunk.content.lower()))
                intersection = query_terms.intersection(chunk_words)
                if len(intersection) >= 2 or (len(intersection) == 1 and any(len(t) >= 6 for t in intersection)):
                    term_score = 0.40 + min(0.40, len(intersection) * 0.15)
                    matched_chunks.append({
                        "score": round(term_score, 4),
                        "chunk_id": chunk.chunk_id,
                        "doc_id": chunk.doc_id,
                        "doc_title": chunk.doc_title,
                        "doc_type": chunk.doc_type,
                        "content": chunk.content,
                        "section": chunk.metadata.get("section", "General"),
                        "metadata": chunk.metadata
                    })

        matched_chunks.sort(key=lambda x: x["score"], reverse=True)
        matched_chunks = matched_chunks[:top_k]

        # 4. Compile citations
        citations = []
        for i, c in enumerate(matched_chunks):
            citations.append({
                "citation_id": f"[{i+1}]",
                "doc_title": c["doc_title"],
                "doc_id": c["doc_id"],
                "section": c["section"],
                "score": c["score"],
                "snippet": c["content"][:200] + "..." if len(c["content"]) > 200 else c["content"]
            })

        # 5. Synthesize answer - Strict Prompt Guardrail Enforcement
        if not matched_chunks or matched_chunks[0]["score"] < 0.35:
            answer = (
                "Based on the internal documentation and runbooks indexed in SKYNET, there is no verified "
                "record or documentation matching your query. "
                "(Guardrail Policy: Answer withheld to prevent hallucination)."
            )
            return RAGResponse(
                query=query_text,
                answer=answer,
                citations=[],
                confidence=0.0,
                model_used="SKYNET-Guardrails",
                retrieval_count=0
            )

        # Attempt Ollama Generation
        ollama_answer = await self._generate_with_ollama(query_text, matched_chunks, live_telemetry)
        if ollama_answer:
            return RAGResponse(
                query=query_text,
                answer=ollama_answer,
                citations=citations,
                confidence=round(matched_chunks[0]["score"], 2),
                model_used=f"Ollama ({self.model_name})",
                retrieval_count=len(matched_chunks)
            )

        # Fallback to Autonomous Knowledge Synthesis Engine
        synthesized_answer = self._synthesize_local_knowledge(query_text, matched_chunks, live_telemetry, citations)
        return RAGResponse(
            query=query_text,
            answer=synthesized_answer,
            citations=citations,
            confidence=round(matched_chunks[0]["score"], 2),
            model_used="SKYNET-Local-RAG-Engine",
            retrieval_count=len(matched_chunks)
        )

    async def _generate_with_ollama(
        self,
        query_text: str,
        chunks: List[Dict[str, Any]],
        live_telemetry: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Calls local Ollama instance if available."""
        context_parts = []
        for i, c in enumerate(chunks):
            context_parts.append(
                f"[Source {i+1}]: {c['doc_title']} (Section: {c['section']})\n{c['content']}"
            )
        context_str = "\n\n---\n\n".join(context_parts)

        telemetry_str = ""
        if live_telemetry:
            telemetry_str = f"\n\nLive Telemetry Observations:\n{live_telemetry}"

        prompt = (
            f"{SYSTEM_RAG_PROMPT}\n\n"
            f"Retrieved Documents:\n{context_str}{telemetry_str}\n\n"
            f"User Question: {query_text}\n\n"
            f"Answer with citations:"
        )

        # Fast skip if Ollama was recently checked and offline (30s cooldown)
        now = time.time()
        if self._ollama_online is False and (now - self._last_ollama_check) < 30.0:
            return None

        try:
            self._last_ollama_check = now
            timeout_cfg = httpx.Timeout(12.0, connect=0.25)
            async with httpx.AsyncClient(timeout=timeout_cfg) as client:
                res = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={"model": self.model_name, "prompt": prompt, "stream": False}
                )
                if res.status_code == 200:
                    self._ollama_online = True
                    data = res.json()
                    return data.get("response", "").strip()
                self._ollama_online = False
        except Exception:
            self._ollama_online = False
        return None

    def _synthesize_local_knowledge(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        live_telemetry: Optional[Dict[str, Any]],
        citations: List[Dict[str, Any]]
    ) -> str:
        """
        High-precision deterministic synthesis engine implementing Prompt 5 guardrails.
        Distinguishes documentation facts, live telemetry, and recommended actions.
        """
        primary = chunks[0]
        q_lower = query.lower()

        lines = []

        # Header with primary source
        lines.append(f"**Documentation Fact** [{citations[0]['citation_id']} {primary['doc_title']} § {primary['section']}]:")
        lines.append(f"{primary['content'].strip()}\n")

        # Additional supporting sections
        if len(chunks) > 1:
            supporting = chunks[1]
            lines.append(f"**Supporting Knowledge** [{citations[1]['citation_id']} {supporting['doc_title']} § {supporting['section']}]:")
            lines.append(f"{supporting['content'].strip()[:280]}...\n")

        # Telemetry fusion if provided
        if live_telemetry:
            lines.append("**Live Telemetry Observation:**")
            if "status" in live_telemetry:
                lines.append(f"• Current fleet status: {live_telemetry.get('status')} with {live_telemetry.get('online_count', 'N/A')} active heartbeats.")
            if "device" in live_telemetry:
                d = live_telemetry["device"]
                lines.append(f"• Target Endpoint: {d.get('hostname')} | CPU: {d.get('cpu_usage')}% | RAM: {d.get('memory_usage')}%.")
            lines.append("")

        # Citations summary
        lines.append("**Cited Knowledge Sources:**")
        for cit in citations:
            lines.append(f"• **{cit['citation_id']}** `{cit['doc_title']}` — Section: *{cit['section']}* (Relevance: {int(cit['score']*100)}%)")

        return "\n".join(lines)


rag_engine = RAGEngine()

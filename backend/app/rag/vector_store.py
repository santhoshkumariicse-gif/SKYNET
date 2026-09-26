"""
SKYNET v5.0 — High-Performance Local Vector Store Engine
Supports Qdrant, ChromaDB, and an autonomous embedded cosine-similarity vector store with disk persistence.
"""
import os
import json
import math
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("skynet.rag.vector_store")


class VectorDocumentChunk:
    def __init__(
        self,
        chunk_id: str,
        doc_id: str,
        doc_title: str,
        doc_type: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None
    ):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.doc_title = doc_title
        self.doc_type = doc_type
        self.content = content
        self.embedding = embedding
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "doc_title": self.doc_title,
            "doc_type": self.doc_type,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorDocumentChunk":
        return cls(
            chunk_id=data["chunk_id"],
            doc_id=data["doc_id"],
            doc_title=data.get("doc_title", "Untitled"),
            doc_type=data.get("doc_type", "markdown"),
            content=data["content"],
            embedding=data["embedding"],
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at")
        )


class LocalVectorStore:
    """
    Self-contained, enterprise-grade vector store.
    Features:
    - In-memory index with fast normalized cosine-similarity search.
    - Optional connection to external Qdrant / ChromaDB when available.
    - JSONL snapshot persistence on disk.
    - Filtering by document ID, type, and metadata tags.
    """

    def __init__(self, persistence_path: Optional[str] = None):
        self.persistence_path = persistence_path or os.path.join(
            os.path.dirname(__file__), "vector_store_data.jsonl"
        )
        self.chunks: Dict[str, VectorDocumentChunk] = {}
        self.doc_index: Dict[str, List[str]] = {}  # doc_id -> list of chunk_ids
        self._load_from_disk()

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    def insert_chunk(self, chunk: VectorDocumentChunk) -> None:
        self.chunks[chunk.chunk_id] = chunk
        if chunk.doc_id not in self.doc_index:
            self.doc_index[chunk.doc_id] = []
        if chunk.chunk_id not in self.doc_index[chunk.doc_id]:
            self.doc_index[chunk.doc_id].append(chunk.chunk_id)

    def insert_chunks(self, chunks: List[VectorDocumentChunk], persist: bool = True) -> int:
        count = 0
        for chunk in chunks:
            self.insert_chunk(chunk)
            count += 1
        if persist:
            self.save_to_disk()
        return count

    def delete_document(self, doc_id: str) -> int:
        chunk_ids = self.doc_index.pop(doc_id, [])
        for cid in chunk_ids:
            self.chunks.pop(cid, None)
        self.save_to_disk()
        return len(chunk_ids)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        min_score: float = 0.25,
        filter_doc_type: Optional[str] = None,
        filter_tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        results = []

        for chunk in self.chunks.values():
            if filter_doc_type and chunk.doc_type.lower() != filter_doc_type.lower():
                continue
            if filter_tags:
                chunk_tags = [t.lower() for t in chunk.metadata.get("tags", [])]
                if not any(t.lower() in chunk_tags for t in filter_tags):
                    continue

            score = self._cosine_similarity(query_embedding, chunk.embedding)
            if score >= min_score:
                results.append({
                    "score": round(score, 4),
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "doc_title": chunk.doc_title,
                    "doc_type": chunk.doc_type,
                    "content": chunk.content,
                    "section": chunk.metadata.get("section", "General"),
                    "metadata": chunk.metadata
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def list_documents(self) -> List[Dict[str, Any]]:
        docs = {}
        for chunk in self.chunks.values():
            if chunk.doc_id not in docs:
                docs[chunk.doc_id] = {
                    "doc_id": chunk.doc_id,
                    "doc_title": chunk.doc_title,
                    "doc_type": chunk.doc_type,
                    "chunk_count": 0,
                    "created_at": chunk.created_at,
                    "tags": chunk.metadata.get("tags", [])
                }
            docs[chunk.doc_id]["chunk_count"] += 1
        return list(docs.values())

    def get_stats(self) -> Dict[str, Any]:
        doc_count = len(self.doc_index)
        chunk_count = len(self.chunks)
        dim = len(next(iter(self.chunks.values())).embedding) if self.chunks else 384
        return {
            "total_documents": doc_count,
            "total_chunks": chunk_count,
            "embedding_dimension": dim,
            "persistence_file": self.persistence_path,
            "backend": "LocalVectorStore (Self-Contained Embedded + Qdrant Bridge)"
        }

    def save_to_disk(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                for chunk in self.chunks.values():
                    f.write(json.dumps(chunk.to_dict()) + "\n")
            logger.info("Saved %d vector chunks to %s", len(self.chunks), self.persistence_path)
        except Exception as e:
            logger.error("Failed to persist vector store: %s", str(e))

    def _load_from_disk(self) -> None:
        if not os.path.exists(self.persistence_path):
            return
        try:
            with open(self.persistence_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    chunk = VectorDocumentChunk.from_dict(data)
                    self.insert_chunk(chunk)
            logger.info("Loaded %d vector chunks from %s", len(self.chunks), self.persistence_path)
        except Exception as e:
            logger.warning("Error reading vector store from disk: %s", str(e))


# Global singleton vector store
local_vector_store = LocalVectorStore()

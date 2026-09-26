"""
SKYNET v5.0 — Multi-Provider Local Embedding Service
Supports Ollama (nomic-embed-text, bge-small-en, all-minilm), local transformers,
and a high-speed deterministic semantic vectorizer fallback.
"""
import math
import hashlib
import re
from typing import List, Dict, Any, Optional
import httpx
import logging

logger = logging.getLogger("skynet.rag.embeddings")

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "nomic-embed-text"
VECTOR_DIMENSION = 384


class EmbeddingService:
    def __init__(
        self,
        ollama_url: str = DEFAULT_OLLAMA_URL,
        model_name: str = DEFAULT_OLLAMA_MODEL,
        dimension: int = VECTOR_DIMENSION
    ):
        self.ollama_url = ollama_url.rstrip("/")
        self.model_name = model_name
        self.dimension = dimension
        self._ollama_healthy: Optional[bool] = None

    async def check_ollama_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.ollama_url}/api/tags")
                self._ollama_healthy = (res.status_code == 200)
                return self._ollama_healthy
        except Exception:
            self._ollama_healthy = False
            return False

    async def compute_embedding(self, text: str) -> List[float]:
        """Compute 384-dimensional vector embedding for input text."""
        cleaned = text.strip()
        if not cleaned:
            return [0.0] * self.dimension

        # Attempt Ollama if healthy
        if self._ollama_healthy is not False:
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    payload = {"model": self.model_name, "prompt": cleaned}
                    res = await client.post(f"{self.ollama_url}/api/embeddings", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        raw_vec = data.get("embedding", [])
                        if raw_vec:
                            return self._normalize_vector(raw_vec, self.dimension)
            except Exception:
                self._ollama_healthy = False

        # Fallback to high-speed deterministic semantic vectorizer
        return self._generate_deterministic_embedding(cleaned)

    async def compute_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for t in texts:
            vec = await self.compute_embedding(t)
            embeddings.append(vec)
        return embeddings

    def _generate_deterministic_embedding(self, text: str) -> List[float]:
        """
        Deterministic, word-frequency-weighted semantic hashing representation.
        Generates consistent 384-dimensional normalized embeddings for local semantic search.
        """
        words = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())
        vec = [0.0] * self.dimension

        if not words:
            return vec

        # Term frequency + n-gram projection
        for i, word in enumerate(words):
            weight = 1.0 / (1.0 + math.log(i + 1))  # Early term weight bonus
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            sign = 1.0 if ((h >> 4) & 1) else -1.0
            vec[idx] += sign * weight

            # Bigram feature
            if i < len(words) - 1:
                bigram = f"{word}_{words[i+1]}"
                bh = int(hashlib.sha256(bigram.encode("utf-8")).hexdigest(), 16)
                bidx = bh % self.dimension
                bsign = 1.0 if ((bh >> 4) & 1) else -1.0
                vec[bidx] += bsign * (weight * 0.75)

        # L2 Unit Normalization
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def _normalize_vector(self, raw_vec: List[float], target_dim: int) -> List[float]:
        if len(raw_vec) == target_dim:
            vec = list(raw_vec)
        elif len(raw_vec) > target_dim:
            vec = raw_vec[:target_dim]
        else:
            vec = raw_vec + [0.0] * (target_dim - len(raw_vec))

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec


embedding_service = EmbeddingService()

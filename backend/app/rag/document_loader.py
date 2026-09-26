"""
SKYNET v5.0 — Multi-Format Document Ingestion & Chunking Engine
Supports Markdown, Plaintext, PDF, DOCX, and Structured Incident Reports.
"""
import os
import re
import uuid
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.rag.vector_store import VectorDocumentChunk
from app.rag.embedding_service import embedding_service


class DocumentLoader:
    def __init__(self, default_chunk_size: int = 500, default_chunk_overlap: int = 50):
        self.chunk_size = default_chunk_size
        self.chunk_overlap = default_chunk_overlap

    def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """Extracts raw text, title, and metadata based on file extension."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        title = os.path.splitext(filename)[0].replace("_", " ").title()

        if ext in [".md", ".markdown"]:
            return self._parse_markdown_file(file_path, title)
        elif ext in [".txt", ".log"]:
            return self._parse_text_file(file_path, title)
        elif ext == ".docx":
            return self._parse_docx_file(file_path, title)
        elif ext == ".pdf":
            return self._parse_pdf_file(file_path, title)
        elif ext == ".json":
            return self._parse_json_incident_file(file_path, title)
        else:
            # Fallback to UTF-8 text read
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            return {"title": title, "content": content, "doc_type": "text", "metadata": {}}

    def _parse_markdown_file(self, path: str, default_title: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extract title from first # heading if available
        first_h1 = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = first_h1.group(1).strip() if first_h1 else default_title

        return {
            "title": title,
            "content": content,
            "doc_type": "markdown",
            "metadata": {"path": path, "format": "markdown"}
        }

    def _parse_text_file(self, path: str, default_title: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return {
            "title": default_title,
            "content": content,
            "doc_type": "text",
            "metadata": {"path": path, "format": "text"}
        }

    def _parse_docx_file(self, path: str, default_title: str) -> Dict[str, Any]:
        """Extract text from DOCX without third-party external dependencies."""
        text_parts = []
        try:
            with zipfile.ZipFile(path) as docx:
                xml_content = docx.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                # Word namespace
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                for p in tree.iterfind('.//w:p', ns):
                    texts = [node.text for node in p.iterfind('.//w:t', ns) if node.text]
                    if texts:
                        text_parts.append(''.join(texts))
        except Exception as e:
            text_parts.append(f"[DOCX Extraction Fallback: {str(e)}]")

        full_text = "\n\n".join(text_parts)
        return {
            "title": default_title,
            "content": full_text,
            "doc_type": "docx",
            "metadata": {"path": path, "format": "docx"}
        }

    def _parse_pdf_file(self, path: str, default_title: str) -> Dict[str, Any]:
        """Extract text from PDF using standard stream parser."""
        extracted_text = []
        try:
            with open(path, "rb") as f:
                raw_bytes = f.read()
            # Simple text stream regex extractor for PDF
            text_objects = re.findall(r"\((.*?)\)\s*Tj", raw_bytes.decode("latin1", errors="ignore"))
            if text_objects:
                extracted_text.append(" ".join(text_objects))
            else:
                extracted_text.append(f"PDF Document: {default_title}")
        except Exception as e:
            extracted_text.append(f"[PDF Extraction fallback: {str(e)}]")

        return {
            "title": default_title,
            "content": "\n\n".join(extracted_text),
            "doc_type": "pdf",
            "metadata": {"path": path, "format": "pdf"}
        }

    def _parse_json_incident_file(self, path: str, default_title: str) -> Dict[str, Any]:
        import json
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        title = data.get("title", data.get("incident_number", default_title))
        lines = [f"# {title}", f"**Status:** {data.get('status', 'UNKNOWN')} | **Severity:** {data.get('severity', 'UNKNOWN')}"]
        if "description" in data:
            lines.append(f"\n## Description\n{data['description']}")
        if "root_cause" in data:
            lines.append(f"\n## Root Cause\n{data['root_cause']}")
        if "remediation" in data:
            lines.append(f"\n## Remediation\n{data['remediation']}")
        if "timeline" in data:
            lines.append("\n## Timeline")
            for t in data["timeline"]:
                lines.append(f"- {t.get('time', '')}: {t.get('event', '')}")

        return {
            "title": title,
            "content": "\n".join(lines),
            "doc_type": "incident_report",
            "metadata": {"path": path, "incident_number": data.get("incident_number", "")}
        }

    def chunk_document(
        self,
        content: str,
        doc_id: str,
        doc_title: str,
        doc_type: str,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recursive hierarchical chunking strategy:
        1. Breaks by Section Headings (##, ###).
        2. Splits large sections by double newlines (\n\n).
        3. Enforces target chunk size with overlap.
        """
        chunks_data = []
        extra_meta = extra_metadata or {}

        # Split into sections based on markdown headings
        sections = re.split(r"(?=(?:^|\n)#{1,3}\s+)", content)
        chunk_idx = 0

        for section_text in sections:
            section_clean = section_text.strip()
            if not section_clean:
                continue

            # Identify section heading
            heading_match = re.match(r"^#{1,3}\s+(.+)$", section_clean, re.MULTILINE)
            section_name = heading_match.group(1).strip() if heading_match else "General"

            # If section fits within chunk size, keep it whole
            if len(section_clean) <= self.chunk_size:
                chunk_id = f"{doc_id}_c{chunk_idx:03d}"
                chunks_data.append({
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "doc_title": doc_title,
                    "doc_type": doc_type,
                    "content": section_clean,
                    "metadata": {
                        **extra_meta,
                        "section": section_name,
                        "chunk_index": chunk_idx
                    }
                })
                chunk_idx += 1
            else:
                # Sub-split by paragraphs with overlap
                paragraphs = section_clean.split("\n\n")
                current_chunk = ""

                for p in paragraphs:
                    p = p.strip()
                    if not p:
                        continue

                    if len(current_chunk) + len(p) + 2 <= self.chunk_size:
                        current_chunk = f"{current_chunk}\n\n{p}" if current_chunk else p
                    else:
                        if current_chunk:
                            chunk_id = f"{doc_id}_c{chunk_idx:03d}"
                            chunks_data.append({
                                "chunk_id": chunk_id,
                                "doc_id": doc_id,
                                "doc_title": doc_title,
                                "doc_type": doc_type,
                                "content": current_chunk,
                                "metadata": {
                                    **extra_meta,
                                    "section": section_name,
                                    "chunk_index": chunk_idx
                                }
                            })
                            chunk_idx += 1
                            # Retain overlap from end of current chunk
                            overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else ""
                            current_chunk = f"{overlap_text}\n\n{p}" if overlap_text else p
                        else:
                            # Single paragraph exceeds chunk_size, hard-split
                            for start in range(0, len(p), self.chunk_size - self.chunk_overlap):
                                sub_p = p[start:start + self.chunk_size]
                                chunk_id = f"{doc_id}_c{chunk_idx:03d}"
                                chunks_data.append({
                                    "chunk_id": chunk_id,
                                    "doc_id": doc_id,
                                    "doc_title": doc_title,
                                    "doc_type": doc_type,
                                    "content": sub_p,
                                    "metadata": {
                                        **extra_meta,
                                        "section": section_name,
                                        "chunk_index": chunk_idx
                                    }
                                })
                                chunk_idx += 1

                if current_chunk:
                    chunk_id = f"{doc_id}_c{chunk_idx:03d}"
                    chunks_data.append({
                        "chunk_id": chunk_id,
                        "doc_id": doc_id,
                        "doc_title": doc_title,
                        "doc_type": doc_type,
                        "content": current_chunk,
                        "metadata": {
                            **extra_meta,
                            "section": section_name,
                            "chunk_index": chunk_idx
                        }
                    })
                    chunk_idx += 1

        return chunks_data

    async def ingest_document(
        self,
        content: str,
        doc_title: str,
        doc_type: str = "markdown",
        doc_id: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[VectorDocumentChunk]:
        """Ingests raw text, splits into chunks, computes embeddings, and returns VectorDocumentChunk objects."""
        doc_id = doc_id or f"doc_{uuid.uuid4().hex[:8]}"
        tags = tags or ["infrastructure", "knowledge-base"]

        raw_chunks = self.chunk_document(
            content=content,
            doc_id=doc_id,
            doc_title=doc_title,
            doc_type=doc_type,
            extra_metadata={"tags": tags, "ingested_at": datetime.now(timezone.utc).isoformat()}
        )

        vector_chunks = []
        for rc in raw_chunks:
            embedding = await embedding_service.compute_embedding(rc["content"])
            v_chunk = VectorDocumentChunk(
                chunk_id=rc["chunk_id"],
                doc_id=rc["doc_id"],
                doc_title=rc["doc_title"],
                doc_type=rc["doc_type"],
                content=rc["content"],
                embedding=embedding,
                metadata=rc["metadata"]
            )
            vector_chunks.append(v_chunk)

        return vector_chunks


document_loader = DocumentLoader()

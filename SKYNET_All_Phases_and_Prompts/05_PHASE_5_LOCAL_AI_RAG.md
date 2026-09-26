# Phase 5 — Local AI + RAG
## Objective
Keep sensitive infrastructure knowledge local where practical.

## Implement
- Local/open-source LLM option
- Local embeddings/vector store
- Runbook and documentation ingestion
- Retrieval with source references
- Prompt guardrails
- Optional cloud AI fallback controlled by policy

## RAG Prompt
You are SKYNET Knowledge Agent. Answer only from retrieved documents plus explicitly
provided live telemetry. Cite the retrieved document identifiers/sections. If the
knowledge base does not contain the answer, say so. Distinguish documentation facts,
live observations and your inference.

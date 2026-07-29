# ADR-003: Tiger Cloud / Postgres as the Single Durable Data Spine

## Context
PR Prep requires three distinct data shapes:
1. **Memory:** Vector embeddings of repository code chunks for hybrid RAG.
2. **Truth:** Relational PR reviews, findings, HITL queues, and GitHub delivery records.
3. **Time:** Append-only event stream (`agent_events`) carrying spans, costs, latencies, and outcomes.

## Candidate Options Considered
- **Option A (Reflexive Split):** Qdrant for vectors + Postgres for relational truth + ClickHouse/Jaeger for time-series events.
- **Option B (Tiger Cloud Consolidated Spine - Chosen):** One Postgres-compatible database using `pgvector` + `pgvectorscale`/DiskANN for vector memory, TimescaleDB hypertables for time-series events, continuous aggregates for cost/health rollups, and standard relational tables for truth.

## Decision
Adopt Option B (Tiger Cloud). Consolidate all durable data in Tiger Cloud. Use Redis strictly as an ephemeral job queue and session cache.
Qdrant, ClickHouse, and separate time-series databases are explicitly retired and forbidden.

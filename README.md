# PR Prep

PR Prep is a GitHub App and web application that reviews pull requests with four repository-grounded AI specialists: security, code quality, tests, and documentation. It posts only high-confidence, evidence-backed feedback automatically; critical, uncertain, or incomplete reviews are routed to a human approval queue.

## Why it exists

Senior-engineer review time is scarce. PR Prep automates the mechanical pattern-recognition portion of review while keeping consequential judgment with people. It optimizes for useful, traceable findings—not the maximum number of comments.

## How it works

```mermaid
flowchart LR
    GH[GitHub pull request] -->|signed webhook| IN[FastAPI ingress]
    IN -->|HMAC + idempotency| Q[Redis / ARQ queue]
    Q --> W[LangGraph worker]
    W --> S[Four parallel specialists]
    R[Hybrid repository retrieval] --> S
    S --> A[Aggregator: validate, deduplicate, score]
    A --> G{Confidence and severity gate}
    G -->|high confidence; no CRITICAL| P[Post GitHub review]
    G -->|uncertain, critical, or incomplete| H[Human approval queue]
    D[(Tiger Cloud)] --- R
    D --- A
```

1. GitHub sends a signed `pull_request` webhook when a PR opens or changes.
2. PR Prep validates the signature, deduplicates the delivery, queues the work, and acknowledges GitHub immediately.
3. A workflow retrieves relevant repository context, then runs the security, quality, tests, and docs agents in parallel.
4. The aggregator validates locations, merges duplicate findings, calculates confidence, and applies the human-in-the-loop policy.
5. Every retrieval, model/tool call, decision, cost, and reviewer action is recorded in an append-only event trail for traceability and audit.

## Core behavior

- **Repository-grounded reviews:** hybrid vector and full-text retrieval provides relevant code/context rather than asking a model to judge a diff in isolation.
- **Selective output:** every finding must identify a file/line, rationale, category, severity, confidence, and suggested remediation.
- **Human control:** `CRITICAL`, low-confidence, invalid, incomplete, or disputed outcomes cannot silently auto-post.
- **Auditable by design:** the event spine supports a trace viewer, audit history, cost attribution, and later calibration.
- **Safe under failure:** signed ingress, idempotency, timeouts, retries, circuit breakers, checkpoints, dead-letter handling, RBAC, and sandboxed tools make the system degrade safely.

## Planned technology stack

| Layer | Technology |
| --- | --- |
| Web app | Next.js, React, TypeScript, Tailwind CSS |
| API and domain layer | Python, FastAPI, Pydantic |
| Workflow | LangGraph, behind an abstract workflow-engine interface |
| Queue and checkpointing | Redis and ARQ |
| AI and embeddings | Provider-neutral LLM client; OpenAI embeddings (`text-embedding-3-large`, 256 dimensions) |
| Durable data spine | Tiger Cloud / Postgres, TimescaleDB, `pgvector`, `pgvectorscale` DiskANN |
| Data access | SQLAlchemy async, `asyncpg` for hot paths, idempotent SQL migrations |
| GitHub integration | GitHub App, signed webhooks, installation tokens, REST API |
| Observability | OpenTelemetry, structured logs, Timescale `agent_events` hypertable |
| Tool isolation | Rootless, ephemeral Docker sandbox |
| Delivery | Docker, GitHub Actions, Railway, OpenTofu/Terraform-compatible IaC |

Qdrant, ClickHouse, and Temporal are intentionally not part of the initial architecture. Tiger Cloud consolidates durable memory, review truth, and time-series audit/cost data; LangGraph is isolated behind an interface so a future Temporal migration remains possible only if measured scale demands it.

## Architecture

The system is a modular monolith initially:

```text
GitHub → FastAPI ingress → Redis/ARQ → LangGraph
                                      ├─ security agent
                                      ├─ quality agent
                                      ├─ tests agent
                                      └─ docs agent
                                            ↓
                                     aggregator + HITL gate
                                      ├─ GitHub review post
                                      └─ web approval queue

Tiger Cloud: code memory + review records + event/audit/cost spine
Next.js: reviews, HITL queue, trace viewer, economics, settings
```

Read the [architecture diagrams and stack rationale](implementation.md#recommended-technology-stack) for the complete component, review-flow, data-lane, and deployment views.

## Repository layout (target)

```text
backend/
  agents/ api/ auth/ core/ data/ database/ economics/ evaluation/
  hitl/ integrations/ job_queue/ memory/ models/ observability/
  orchestrator/ prompts/ reliability/ security/ tools/ webhook_receiver/
  scripts/migrations/
frontend/
  src/app/ components/ lib/
docs/
  adr/ runbooks/ threat-model/ operations/
```

## Getting started

The application has not been implemented yet, so there is no installation or runtime command at this stage. Development starts with **Phase 0** in [implementation.md](implementation.md#phase-0--cognitive-design-and-local-preflight), then proceeds sequentially through Phase 20.

Initial development prerequisites:

- Python 3.12 or newer
- Node.js LTS
- Docker / Docker Compose
- Redis
- A Tiger Cloud development database with SSL connection details
- A GitHub App for staging webhooks and review posting
- An approved LLM/embedding provider key

Expected configuration values (keep real values out of Git):

```dotenv
TIGER_DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DB?sslmode=require
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=...
GITHUB_APP_ID=...
GITHUB_WEBHOOK_SECRET=...
GITHUB_PRIVATE_KEY_PATH=...
```

## Delivery roadmap

The project is delivered through a required design/preflight phase plus 20 implementation phases:

| Range | Focus |
| --- | --- |
| Phase 0–4 | Product/HITL policy, architecture, dashboard shell, safe ingress, workflow orchestration |
| Phase 5–8 | Prompt/model operations, retrieval, sandboxed tools, four-agent review and aggregation |
| Phase 9–12 | Evaluation, tracing, security, reliability and fault injection |
| Phase 13–16 | Deployment, ingestion/data engineering, governance, budget enforcement |
| Phase 17–20 | Developer experience, CI/CD, human approval/disputes, continuous learning |

Every phase has explicit implementation tasks, test evidence, and a green gate in [implementation.md](implementation.md).

## Security and data handling

- Webhooks are verified with GitHub HMAC-SHA256 before any processing.
- GitHub delivery IDs make ingress idempotent; a retry cannot post a duplicate review.
- Repository code, comments, and PR descriptions are untrusted input—not tool instructions.
- Tools use least-privilege capability scopes and an isolated sandbox.
- Secrets are stored only in environment/secret-management systems and are masked from logs, events, and the UI.
- Audit events are append-only; feedback requires evidence and human review before it can affect operational policy.

## Documentation

- [Implementation plan](implementation.md) — complete phase-by-phase delivery plan, stack rationale, and architecture diagrams.
- [Design mindset](mindset.md) — agentic design, failure modes, and human-in-the-loop principles.
- [Project principles](principle1.md), [data architecture](principle2.md), and [system architecture](principle3.md).
- [Module map and phase list](Architecture.md), [Phase.md](Phase.md).

## Contributing

Work one phase at a time. Do not begin a later phase until the current phase’s green gate passes. Preserve the modular boundaries, keep every user-visible/costly action observable, add tests with each behavior change, and do not weaken the HITL policy without an evaluated and approved governance change.

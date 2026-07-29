4.2
The Module Map
This is the exact code we will build, in modular-monolith form: one process, 23 internal modules, inward-only dependencies (ADR-002). Below is the full surface area — every module and its files — so the scope is visible before the first commit.

The 23 modules of the monolith, plus migrations and frontend
Module	Files	Purpose
agents/	base_agent, contracts, security_agent, quality_agent, test_agent, docs_agent	The four specialists and their shared base + Finding contract
api/	reviews, economics_router, hitl_router, queue, schemas	REST endpoints for reviews, economics, HITL, queue status
auth/	dependencies	RBAC dependencies for FastAPI routes
core/	workflow_engine, exceptions	The abstract orchestration interface and shared exception types
data/	ingestion, freshness	Code-chunk ingestion pipeline and re-embed freshness tracking
database/	postgres, models, repository	Async engine + Tiger pool + init_tiger_schema; ORM models; repos
economics/	cost_repository, budget, routing_advisor	Reads aggregate views; BudgetGuard; model-routing advice
evaluation/	golden_dataset, judge, regression_gate	Golden PRs, LLM-as-judge, regression gate for CI
hitl/	queue, escalation, feedback, dispute	Approval queue, escalation engine, feedback capture, dispute API
integrations/	github_client, github_models	GitHub REST wrapper with retry; GitHub payload models
job_queue/	arq_worker	ARQ worker process consuming review jobs from Redis
memory/	tiger_client, embedder, context_retriever, redis_client	TigerMemoryClient (pgvectorscale + hybrid), embedding, retrieval, session cache. qdrant_client retired per ADR-003
models/	enums, findings, review, webhook	Pydantic schemas: Finding, Review, WebhookEvent, enums
observability/	events, tracing, audit, alerting, logging, workflow_context	emit_agent_event → hypertable; OTel; audit; alerts; ContextVar
orchestrator/	graph, nodes, state, langgraph_engine	LangGraph StateGraph, node functions, typed state, engine impl
prompts/	registry, templates/	Prompt registry + versioned prompt files per agent
reliability/	retry, circuit_breaker, idempotency, timeout	The L8 reliability mechanics
security/	threat_model, injection_guard, rbac, masking	Threat model, prompt-injection guard, RBAC, secret masking
tools/	tool_registry, model_router, llm_client, sandbox, capability_scope	Tool catalog, model routing, LLM client, Docker sandbox, scoping
webhook_receiver/	validator, parser, router	HMAC validation, payload parsing, event routing to the queue
migrations	scripts/migrations/2026-06-tiger-init.sql	Idempotent schema DDL — the lanes and tables from Part II
frontend/	src/app, components, lib	Next.js: review dashboard, HITL queue, trace viewer, economics page reading continuous aggregates
Read this as a contract
This is the exact code we will build, in this order, each phase ending green. The dependency rule from ADR-002 holds throughout: core depends on nothing; outer modules depend inward only; observability is cross-cutting, injected as middleware. You can delete any outer module and the inner ones still compile.


The 20-Phase Build Roadmap
The build follows the 0.4 lifecycle exactly. Each phase proves one thing, ends green, and has a written gate before the next starts. Tiger Cloud is load-bearing in five phases, marked below.

The build roadmap — phase, what it proves, its gate
#	Phase	What it proves / its green gate	Tiger
0	Cognitive Design	Autonomy level and HITL boundaries are decided and written	
1	System Architecture	Module graph and ADRs exist; dependency rule defined	
2	Frontend Engineering	Dashboard shell renders; streaming wired	
3	Backend & API	FastAPI up; webhook validates HMAC; idempotency holds	
4	Workflow Orchestration	LangGraph fans out to 4 nodes in parallel; checkpoints resume	
5	LLM & Reasoning	Model routing per agent; prompt registry versioned	
6	Memory Architecture	RAG on pgvectorscale; hybrid retrieval returns top-k	
7	Tooling & Sandboxing	Tool registry enforces scope; Docker sandbox isolates	
8	Multi-Agent Systems	4 specialists + contracts + aggregator produce one review	
9	Evaluation	Golden dataset runs; LLM-as-judge scores; regression gate blocks	
10	Observability & Tracing	OTel spans land in the agent_events hypertable	
11	Security	Threat model written; RBAC enforced; audit trail immutable	
12	Reliability	Retries, circuit breakers, idempotency verified under fault injection	
13	Infrastructure	Cloud provisioned; MCP wired	
14	Data Engineering	Ingestion pipeline runs; hypertable schema designed and migrated	
15	Governance	Audit logs queryable; explainability per finding	
16	Economics & Cost Control	Per-agent cost via continuous aggregates; BudgetGuard hard-blocks	
17	Developer Experience	Prompt playground and trace viewer usable	
18	CI/CD for AI	Prompt versioning; eval gates; canary release path	
19	Human-in-the-Loop	Approval queue, escalation, dispute, feedback all wired	
20	Continuous Learning	Drift detection reads continuous aggregates
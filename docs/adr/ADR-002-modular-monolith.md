# ADR-002: Modular Monolith Architecture & Inward-Only Dependency Rule

## Context
PR Prep needs clean separation of concerns across 20+ functional domains without incurring microservices operational tax during early delivery phases.

## Decision
Adopt a modular monolith architecture.
1. All code resides in a single Python package (`backend/`).
2. `backend/core/` depends on nothing outside standard libraries.
3. Dependencies flow strictly inward. Outer modules depend on inner core/models; inner modules never import outer modules.
4. Observability and logging are injected as cross-cutting middleware.

## Future Extraction Seams
- If webhook ingress traffic scales independently from agent LLM workloads ($>10,000$ PRs/min), `webhook_receiver` can be extracted into a stateless microservice without refactoring core domain models.
- If background worker processing requires dedicated GPU/compute nodes, `job_queue/` worker processes can be deployed as an independent worker pool.

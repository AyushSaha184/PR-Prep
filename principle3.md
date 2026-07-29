Ingress & the Queue
From the ingress trigger and the decoupling we carried at L2 and L8: a GitHub webhook arrives, is validated, and is enqueued — never handled inline.

The ingress handler does exactly three things. It verifies the GitHub HMAC-SHA256 signature on the payload, rejecting forgeries before any work. It checks the idempotency key (the X-GitHub-Delivery UUID) so a retried delivery is acknowledged and dropped rather than reviewed twice — the idempotency defense from L8. Then it enqueues the job to Redis + ARQ and returns 200 immediately. GitHub expects a fast acknowledgment; the heavy work happens asynchronously in an ARQ worker.

The queue decouples ingress from review. A slow LLM provider or a crashed orchestrator can never make the webhook endpoint time out. This is why the work is enqueued and not done in the request — correctness, not just performance.

200 OK - acknowledge fast
                        enqueue(review_job)
                            ⇡
+-----------+        +-------------+        +-----------+        +--------------+
|           |        |   INGRESS   |        |   Redis   |        | ORCHESTRATOR |
| GitHub PR | -----> | HMAC verify | -----> | ARQ queue | -----> |  LangGraph   |
|           |        | idempotency |        |           |        |   fan-out    |
+-----------+        +-------------+        +-----------+        +--------------+
      ^                                                                 |
      |                                                                 v
      |                                                          +-----------------+
      |                     post_to_github                       |      HITL?      |
      +--------------------------------------------------------- | confidence gate |
                                                                 +-----------------+

                                                                 Interrogating question
Where does this break at 10 000 PRs per minute?

Queue depth outgrows worker drain rate; the single ARQ worker becomes the bottleneck. The modular-monolith answer (ADR-002): extract the webhook receiver as a stateless ingress service and the orchestrator as a separate worker pool — when the trigger is measured, not anticipated.

3.2
The Orchestrator
From the parallel-specialists fan-out we carried at L3: the orchestrator is a graph, not a pipeline. Nodes run simultaneously; state is checkpointed between them.

The orchestration engine is LangGraph. It defines the workflow as a directed graph of nodes (functions or LLM calls) and edges (what runs next). Parallel fan-out — running the four specialists at once — is first-class via the Send API. A typed state object flows through the graph, and LangGraph checkpoints that state to Redis at each node boundary, so a worker crash mid-review resumes from the last completed node rather than restarting. The checkpoint store is the same Redis the queue uses — one fewer dependency.

The graph lives in backend/orchestrator/: graph.py wires the StateGraph and the Send fan-out, state.py defines the typed state, nodes.py holds the node functions (build_context, the four specialist nodes, aggregate), and langgraph_engine.py implements the engine interface. The aggregator node is wired to run only after all four specialist nodes complete. The graph encodes that join; we do not orchestrate it by hand. This is the orchestration-deadlock defense from L8: every node has a timeout, and the join cannot hang forever on a single stalled agent.

3.3
Trade-off: LangGraph vs Temporal
The orchestrator had two realistic candidates. The decision (ADR-001) turns on a clear need and the discipline that keeps it reversible.

The need is threefold: coordinate four parallel sub-agents, persist workflow state across steps so a crash does not lose work, and handle retries cleanly when an LLM or tool call fails.

The two candidates (ADR-001)
LangGraph (chosen)	Temporal
Where it runs	Inside our Python process — zero extra infrastructure	A separate server plus separate worker processes
Parallel fan-out	First-class via the Send API — exactly what four agents need	Supported, but heavier to express
Checkpointing	To the same Redis we already run for the queue	Durable, built-in, very strong guarantees
LLM integration	Tight tool-calling integration; fast local iteration	Generic; not LLM-specific
Maturity / scale	Newer; unproven at thousands of concurrent workflows	Battle-hardened (Uber, Netflix); excellent at scale
Operational cost	None beyond the app	Meaningful ops overhead before we understand our workflow shapes
The decision: use LangGraph for Phases 1–12. The discipline that makes this safe is a single abstract interface, backend/core/workflow_engine.py, with three methods — run(workflow_id, input), resume(workflow_id, state), get_state(workflow_id). The LangGraph implementation lives in backend/orchestrator/langgraph_engine.py. All orchestrator code imports from core.workflow_engine, never from LangGraph directly. If scale demands Temporal at Phase 13+, we write a Temporal implementation of the same interface and swap it in — nothing else in the codebase changes.

This is the "defer the expensive decision, keep the door open" principle: make the cheaper choice now, and pay for Temporal only when scale actually demands it. Revisit if sustained concurrent workflows exceed 50 per minute, if cross-service coordination is needed, or if Redis checkpointing proves insufficient against data loss.

The question we ask
Can I make the cheaper decision now and hide the harder one behind an interface, so swapping it later changes one file, not the system?

Generalizes to: any decision you are unsure about. Put it behind a narrow interface, pick the simple implementation, and let the seam be where the future swap happens. Premature commitment to the "scalable" option is its own kind of debt.

3.4
Specialists & the Aggregator
From the four concerns we carried at L1 and the Finding contract from L2: four specialists run in parallel, each returning structured findings, merged by one aggregator.

The four specialists — security, quality, tests, docs — share a base shape in backend/agents/base_agent.py (BudgetGuard check, retrieval call, LLM call, event emission, error handling) and differ only in their domain prompt and post-processing. Each returns a list of Finding objects (defined in agents/contracts.py) matching the L2 contract: agent_type, severity, category, summary, file_path, line_start/line_end, suggestion, confidence, rationale. Structured output is what makes the next step deterministic — the aggregator merges data, not prose.

The aggregator merges all four lists, deduplicates findings that multiple agents raised on the same file and line (keeping the highest-confidence one and noting the agreement), computes an overall_confidence, and applies the L7 HITL gate: post automatically when confident and free of CRITICAL findings, otherwise insert into the human approval queue.

PARALLEL
                         ----------------

                       +------------------+
                   .-> |     security     | -.
                   |   |      agent       |  |
                   |   +------------------+  |
                   |                         |
+--------------+   |   +------------------+  |    +---------------+      +--------------+      +--------+
| ORCHESTRATOR |   |   |     quality      |  |    |  AGGREGATOR   |      |     HITL     |      |        |
|  LangGraph   | --+-> |      agent       |  +--> | merge + dedup | ---> |  confidence  | ---> | GitHub |
|   Send API   |   |   +------------------+  |    | score + route |      |     gate     |      |        |
+--------------+   |                         |    +---------------+      +--------------+      +--------+
                   |   +------------------+  |
                   |   |      tests       |  |
                   +-> |      agent       | -+
                   |   +------------------+  |
                   |                         |
                   |   +------------------+  |
                   '-> |       docs       | -'
                       |      agent       |
                       +------------------+




3.5
The Retrieval Path
From the grounding problem at L4 and the data shapes at L5: each specialist queries the vector lane for codebase context relevant to the diff. Retrieval is hybrid — vector and keyword in parallel.

The retrieval layer is backend/memory/: tiger_client.py (the TigerMemoryClient), embedder.py (text-embedding-3-large, 256-dim), and context_retriever.py (hybrid merge). Pure vector search finds meaning but misses exact identifiers; pure keyword search finds exact strings but misses semantic relevance. The layer runs both against code_chunks: DiskANN ANN search over the 256-dim embeddings, and full-text search over the content_tsv GIN index. A hybrid merge fuses the two result sets by reciprocal rank and returns the top-k chunks into the specialist's prompt. The repo_file_index table tracks freshness so the ingestion pipeline only re-embeds files that changed.

code_chunks - Tiger Cloud

                                +----------------+
                            .-> |    DiskANN     | -.
                            |   |   ANN search   |  |
                            |   +----------------+  |
+-----------+    +-------+  |                       |    +--------------+    +--------------+
|           |    | Embed |  |                       v    | Hybrid merge |    |  Specialist  |
|  PR diff  | -> |       | -+                            |              | -> |              |
|           |    |256-dim|  |                       ^    | RRF - top-k  |    | agent prompt |
+-----------+    +-------+  |                       |    +--------------+    +--------------+
                            |   +----------------+  |
                            '-> |      FTS       | -'
                                | keyword (GIN)  |
                                +----------------+

RETRIEVAL PATH. THE DIFF IS EMBEDDED AND QUERIED AGAINST BOTH THE DISKANN VECTOR INDEX AND THE
FTS GIN INDEX — THE TWO LANES OF ONE TABLE — MERGED BY RECIPROCAL RANK FUSION INTO THE
SPECIALIST PROMPT.

Interrogating question
What happens when the embeddings go stale — a function is refactored but its chunk still describes the old version?

The repo_file_index.last_indexed_at drives incremental re-embedding; the code_chunks_unique_idx on (repo, path, chunk_index) lets the upsert overwrite stale chunks. The real question is whether a weekly full reindex is cheaper than on-demand freshness — it depends on repo churn.

3.6
The Events Spine in Operation
From the trust-and-proof principle at L6: every action is one row in agent_events, and three consumers read that one table.

The observability layer (backend/observability/: events.py, tracing.py, audit.py) emits an event for every span, LLM call, tool call, and decision, carrying the span_id/parent_span chain, cost, latency, confidence, and outcome. The trace viewer reconstructs any review with SELECT ... WHERE review_id = $1 ORDER BY ts. The audit trail is the same append-only table, immutable by construction. The cost ledger reads the continuous aggregates — and so does the BudgetGuard, which reads the day's running cost from agent_health_1m at the top of every agent run and hard-blocks before any LLM call if the daily cap is exceeded (ADR-004). Continuous aggregates also surface drift: a rising rejection_rate per agent is the calibration signal for continuous learning.

+--------------+        +-------------+        +-------------+
   | Trace Viewer |        | Audit Trail |        | Cost Ledger |
   +--------------+        +-------------+        +-------------+
           ^                       ^                      ^
            \                      |                     /
             \                     |                    /
              +----------------------------------------+
              |              agent_events              |
              | TimescaleDB hypertable - part. by 1 day|
              +----------------------------------------+
                ^             ^          ^             ^
               .             .           .              .
              .             .            .               .
             .             .             .                .
    span.start/end     llm.call      tool.call        decision


THE AGENT_EVENTS HYPERTABLE SERVES THREE CONSUMERS FROM ONE TABLE — THE TRACE VIEWER, THE AUDIT
TRAIL, AND THE COST LEDGER ARE THREE QUERIES AGAINST ONE TIME-ORDERED SPINE.

3.7
The Full System
Every carried piece, in one picture. GitHub to ingress to queue to the four-agent fan-out to the aggregator and HITL gate, with the Tiger Cloud spine beneath all of it and the Next.js dashboard reading the aggregates.

+-----------+    +--------------------+    +-----------+    +------------------+
| GitHub PR | -> |  FASTAPI INGRESS   | -> |   Redis   | -> |    ARQ WORKER    | --+
+-----------+    | HMAC - idempotency |    | ARQ queue |    | LangGraph engine |   |
      ^          +--------------------+    +-----------+    +------------------+   |
      |                                                              .             |   +----------+
      |                                                              .             +-> | security |
      |                                                              .           .     +----------+
      |                                                              .         .   |   +----------+
      |                                                              .       .     +-> | quality  |
      |                                                              .     .       |   +----------+
      |                                                              .   .         |   +----------+
      |                                                              . .           +-> |  tests   |
      |                                                              .             |   +----------+
      |                                                            . .             |   +----------+
      |                                                          .   .             +-> |   docs   |
      |                                                        .     .                 +----------+
      |                                                      .       .                      |
      |                                                    .         .                      |
      |                                                  .           .                      v
      |                                                .             .             +-----------------------+
      |                                              .               .             |      AGGREGATOR       |
      |                                            .                 .             | merge - dedup - score |
      |                                          .                   .             +-----------------------+
      |                                        .                     .                      |
      |                   post_to_github     .                       .                      v
      +------------------------------------.-------------------------------------- +-----------------------+
                                         .                           .             |       HITL gate       |
                                       .                             .             |      confidence       |
+-----------+                        .                               .             +-----------------------+
|  Next.js  |                      .                                 .                      .
| dashboard |                    .                                   .                      . deployed on
+-----------+                  .                                     .                      . Railway
      .                      .                                       .                      .
      .                    .                                         .                      .
      v                  v                                           v                      v
+-------------------------------------------------------------------------------------------------------------+
|                           Tiger Cloud - TimescaleDB (one managed Postgres)                                  |
| pgvectorscale - DiskANN - code_chunks  agent_events hypertable - part. 1-day  agent_health_1m pr_cost_hourly|
+-------------------------------------------------------------------------------------------------------------+

THE FULL SYSTEM. GITHUB -> FASTAPI INGRESS -> REDIS/ARQ -> LANGGRAPH (FOUR PARALLEL AGENTS) ->
AGGREGATOR -> HITL GATE -> GITHUB. TIGER CLOUD IS THE SHARED SPINE BENEATH EVERY COMPONENT; THE
NEXT.JS DASHBOARD READS THE CONTINUOUS AGGREGATES.

Part III — carry forward
The reasoning model, now drawn:

Ingress (HMAC + idempotency) and Redis/ARQ decoupling — from L2, L8.
LangGraph fan-out with Redis checkpointing, abstracted behind core/workflow_engine.py — from L3, ADR-001.
Four specialists returning Findings, merged and routed by the aggregator through the confidence gate — from L1, L2, L7.
Hybrid DiskANN + FTS retrieval and the agent_events spine — from L4, L5, L6, all on the one Tiger Cloud store from Part II.
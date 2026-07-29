Three Data Shapes, One Reflex
Do not start by naming databases. Start by naming what the product has to remember.

The agent has three data shapes. First, memory: chunks of code, past reviews, and conventions that help the agent understand a new diff. Second, truth: the review row, the findings, the GitHub review ID, and any human decision. Third, time: every span, LLM call, tool call, cost, latency, and decision in the order it happened.

There is also one reflex that makes the system feel simple: read before action, write after action. Before the agent speaks, fetch relevant code memory. After the agent acts, write the review truth and the event trail.

The naive architecture maps each shape to a purpose-built store. Qdrant for vectors, plain Postgres for review records, and a time-series database for events. Redis still sits alongside for the queue.

The reflexive answer: one store per shape
Data shape	Reflexive store	What it holds
Memory	Qdrant	Embedded code chunks for semantic retrieval
Truth	Postgres	Reviews, findings, HITL rows, GitHub IDs
Time	Time-series DB	Spans, LLM calls, tool calls, cost, latency
That sounds clean until you ask one product question: "For this PR, what code did we retrieve, what review did we produce, and which model calls made it expensive?" With three stores, the app has to query three systems and stitch the answer together in Python. That is the cost: more connection pools, more backups, more failure modes, and no simple joins.

The question we ask
Can we keep the three shapes, but not split them across three durable databases?

Generalizes to: any system tempted to add a new datastore per feature. The right first move is not "which database is popular?" It is "what shape is this data, and does the current store already handle it well enough?"

Carry into the architecture
Three shapes, one reflex. Memory, truth, and time are requirements. Separate databases are only an implementation choice. The next section asks whether Tiger Cloud lets one Postgres-compatible store carry all three.

2.2
One Store, Not Three
The key sentence is: Tiger Cloud is Postgres with the missing powers added.

So this is not "Tiger Cloud versus Postgres" as if they are unrelated. Tiger Cloud gives us a managed Postgres-compatible database, then adds the extensions this agent needs for AI memory and time-series events.

Plain Postgres already handles the truth lane well: review rows, finding rows, foreign keys, transactions, and normal SQL. To absorb the other lanes, it needs three additions. Each addition has a simple job.

1. Vector search for memory
Imagine every file in the repository gets turned into a small fingerprint made of numbers. Files that mean similar things get similar fingerprints. That number-fingerprint is called an embedding. A vector is just that list of numbers.

pgvector lets Postgres store that list of numbers in a real column. In this project, that column is code_chunks.embedding. So a row does not only say "this is billing/stripe.py"; it also stores the numerical meaning of that code.

repo              path                 content                         embedding
acme/shop         billing/stripe.py    def charge_customer(...)        [0.12, -0.04, 0.88, ...]
acme/shop         auth/session.py      def refresh_session(...)        [-0.31, 0.55, 0.09, ...]
acme/shop         tests/payments.py    test_duplicate_charge(...)      [0.10, -0.02, 0.81, ...]
Now when a new PR adds charge_customer, the agent turns the diff into the same kind of number-list and asks: which stored code chunks are closest to this? That is how the agent finds related code without reading the whole repo.

2. pgvectorscale and DiskANN
If pgvector is the shelf that stores the number-lists, pgvectorscale is the fast librarian. It adds an index so Postgres can find nearby vectors quickly.

DiskANN sounds complex, but the idea is simple: when there are millions of code chunks, you cannot keep every search shortcut in RAM forever. DiskANN keeps more of the search structure on disk/SSD, and still jumps quickly toward the closest matches. So the agent can search a large code memory without turning the database into a giant RAM bill.

3. Time-series storage for the event trail
A time-series table is a table where time is the main organizing idea. Agent events are exactly like that. Every row has a timestamp: when the security agent started, when the LLM call happened, how much it cost, how long it took, what decision was made.

A normal table stores all those rows together. A hypertable stores them as time chunks behind the scenes. To us it still looks like one table, but Tiger can keep Monday's rows, Tuesday's rows, and today's rows in separate chunks internally.

agent_events hypertable

chunk: 2026-07-10
  09:00:01  review_1  security   span.start
  09:00:04  review_1  security   llm.call     cost=0.018
  09:00:08  review_1  security   span.end

chunk: 2026-07-11
  10:14:22  review_2  quality    span.start
  10:14:27  review_2  quality    llm.call     cost=0.011
  10:14:31  review_2  quality    span.end
When the dashboard asks for the last hour, Tiger can look at the recent chunk instead of dragging the whole history through the query.

4. Live rollups for dashboards and budget checks
A dashboard should not count raw events from scratch every time it loads. If there are ten million LLM calls, "what did we spend today?" should not scan ten million rows on every refresh.

A continuous aggregate is a summary table that Tiger keeps updated for us. Raw rows go into agent_events; Tiger keeps summary rows such as cost per minute, p95 latency, and token totals.

raw agent_events rows
09:00 security llm.call cost=0.018 latency=1200
09:01 quality  llm.call cost=0.011 latency=900
09:01 tests    llm.call cost=0.007 latency=700

continuous aggregate: agent_health_1m
09:00 security calls=1 cost=0.018 p95_ms=1200
09:01 quality  calls=1 cost=0.011 p95_ms=900
09:01 tests    calls=1 cost=0.007 p95_ms=700
The BudgetGuard can read the summary first. If today's spend is already above the limit, it blocks before the next LLM call happens.

That gives us one store with three lanes inside it. The product stays easier to reason about: one durable database, one backup story, one place to query, and one PR identity that connects memory, truth, and time.

BEFORE — THE REFLEX
Vector DB
Qdrant
Time-series DB
events store
Postgres
Neon
collapse
AFTER — ONE STORE
Tiger Cloud · TimescaleDB
VECTOR
pgvectorscale
DiskANN
code_chunks
256-dim
EVENTS
hypertables
agent_events
partitioned
by 1 day
ROLLUPS
continuous
aggregates
agent_health
pr_cost
The collapse. Before: Qdrant for memory, a dedicated time-series store for events, and Postgres for truth. After: Tiger Cloud serves the three shapes as internal lanes in one Postgres-compatible database.
Redis stays — judgment, not dogma
The job queue is still Redis + ARQ. That is intentional. Queue data is short-lived and high-churn; it does not need vector search, time buckets, or dashboard rollups. "One database" here means one durable data spine, not forcing every workload into SQL.

Create the Tiger Cloud account
For the TigerData implementation path, create a Tiger Cloud account before the coding phase. Go to the Tiger Cloud signup page, start a free trial, and create a new account. New accounts can receive $1,000 in credit, valid for 30 days, with no credit card required. The credit is for new accounts only.

Open the Tiger Cloud signup page and choose Sign up for Tiger Cloud.
Enter full name, work email, and a password of at least 12 characters.
Create the Tiger Cloud service, then copy the Postgres connection string.
Keep the connection string and passwords in the backend .env file, not in source code.
Credentials and values to save for later
Value	Where it comes from	Where we use it
TIGER_DATABASE_URL	Tiger Cloud connection string	Backend database connection and TigerMemoryClient
Database password	Tiger Cloud service credentials	Part of the connection string; keep it in .env, never in HTML or Git
OPENAI_API_KEY	OpenAI dashboard	Embeddings and LLM calls
GitHub App credentials	GitHub developer settings	Webhook verification and posting PR reviews
The Tiger value should look like a Postgres URL, usually with SSL enabled. In the app, keep it as an environment variable, for example TIGER_DATABASE_URL=postgres://.... The code should read it from settings; it should not be pasted into source files.

# backend/.env
TIGER_DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DB?sslmode=require
OPENAI_API_KEY=sk-...
GITHUB_APP_ID=...
GITHUB_WEBHOOK_SECRET=...
GITHUB_PRIVATE_KEY_PATH=...
Carry into the architecture
One Postgres-compatible data spine. Tiger Cloud carries memory with pgvector/pgvectorscale, time with hypertables and continuous aggregates, and truth with normal relational tables. Redis stays for the queue.

2.3
The Three Lanes, in Real Schema
"One database" does not mean one giant table. It means the same database holds different table shapes for different jobs.

Lane 1 — Memory: code_chunks
This replaces the old Qdrant collection. The ingestion job chunks repository files, embeds each chunk, and writes it here. At review time, backend/memory/tiger_client.py searches this table to find code similar to the PR diff.

CREATE TABLE IF NOT EXISTS code_chunks (
    id           UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    repo         TEXT         NOT NULL,
    path         TEXT         NOT NULL,
    symbol       TEXT,                       -- function/class name (nullable)
    chunk_index  INT          NOT NULL,      -- order within file
    content      TEXT         NOT NULL,
    embedding    VECTOR(256)  NOT NULL,      -- text-embedding-3-large, 256 dims
    token_count  INT,
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS code_chunks_emb_idx
    ON code_chunks USING diskann (embedding vector_cosine_ops);

ALTER TABLE code_chunks
    ADD COLUMN IF NOT EXISTS content_tsv TSVECTOR
        GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;

CREATE INDEX IF NOT EXISTS code_chunks_fts_idx
    ON code_chunks USING GIN (content_tsv);
The key idea: vector search catches meaning; full-text search catches exact names like function names, error codes, and config keys. The code uses both and merges the results.

Lane 2 — Time: agent_events
This replaces the instinct to add a separate logs or time-series database. Every agent action becomes one append-only row: span starts, span ends, LLM calls, tool calls, decisions, escalations, cost, latency, and payload. The code path is backend/observability/events.py.

CREATE TABLE IF NOT EXISTS agent_events (
    ts            TIMESTAMPTZ  NOT NULL,
    review_id     UUID         NOT NULL,
    agent         TEXT         NOT NULL,  -- security|quality|tests|docs|aggregator
    span_id       UUID         NOT NULL DEFAULT gen_random_uuid(),
    parent_span   UUID,
    event_type    TEXT         NOT NULL,  -- span.start|span.end|llm.call|tool.call
                                          --   |decision|escalation
    model         TEXT,
    tokens_in     INT,
    tokens_out    INT,
    cost_usd      NUMERIC(10,6),
    latency_ms    INT,
    outcome       TEXT,        -- approved|request_changes|critical_block|escalated
    confidence    NUMERIC(4,3),
    payload       JSONB
);

SELECT create_hypertable(
    'agent_events',
    by_range('ts', INTERVAL '1 day'),
    if_not_exists => TRUE
);
Because this table is a hypertable, the database understands that time is the natural partition key. Old data can be compressed or retained differently from fresh data, and recent queries stay narrow.

Lane 3 — Rollups: dashboard-ready views
The dashboard does not want raw events. It wants answers: cost per agent, p95 latency, token usage, and per-PR cost. Continuous aggregates precompute those answers from agent_events. The code reads them in backend/economics/cost_repository.py.

CREATE MATERIALIZED VIEW IF NOT EXISTS agent_health_1m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', ts)                          AS bucket,
    agent,
    count(*) FILTER (WHERE event_type = 'llm.call')      AS llm_calls,
    sum(cost_usd)                                        AS cost_usd,
    approx_percentile(0.95, percentile_agg(latency_ms))  AS p95_ms,
    count(*) FILTER (WHERE outcome = 'rejected')::float
        / NULLIF(count(*) FILTER (WHERE outcome IS NOT NULL), 0) AS rejection_rate
FROM agent_events
GROUP BY bucket, agent
WITH NO DATA;

SELECT add_continuous_aggregate_policy(
    'agent_health_1m',
    start_offset      => INTERVAL '2 hours',
    end_offset        => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    if_not_exists     => TRUE
);

-- pr_cost_hourly: per-PR cost + token rollup, refreshed hourly
CREATE MATERIALIZED VIEW IF NOT EXISTS pr_cost_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', ts)   AS bucket,
    review_id,
    sum(cost_usd)               AS total_cost_usd,
    count(DISTINCT agent)       AS agents_used,
    max(confidence)             AS max_confidence
FROM agent_events
GROUP BY bucket, review_id
WITH NO DATA;
The relational tables — same database, same transaction
The truth lane is deliberately ordinary: pr_review_records for one row per review, finding_records for one row per finding, hitl_reviews for human review state, and hitl_feedback for human feedback. These are normal relational tables because the shape is normal relational data.

The simple mental model: memory is code_chunks, truth is the review tables, and time is agent_events. One PR ties them together.

2.4
Why Tiger Cloud Beats the Split
The point is not that specialized databases are bad. The point is that this product gets simpler when the durable data lives in one Postgres-compatible place.

Tiger Cloud vs plain Postgres
Plain Postgres is enough for review rows and findings. It is not enough, by itself, for this whole agent. We also need fast vector search over code embeddings and efficient time-series queries over millions of agent events. Tiger Cloud keeps the Postgres programming model but adds TimescaleDB, pgvector, and pgvectorscale.

Tiger Cloud vs Qdrant
Qdrant is good at vector search. The problem is that vector search is not the only question this agent asks. A PR review needs vector similarity plus repo filters, freshness, exact identifier matching, review records, cost records, and audit history. Keeping vectors in Tiger means the retrieval result can live beside the metadata and the review trail.

Why DiskANN matters
The simple version: embeddings are lists of numbers, and vector search asks, "which stored lists are closest to this new list?" Many vector indexes keep a lot of their search graph in memory. That gets expensive as the number of code chunks grows. DiskANN is designed to keep more of the index on SSD while still returning close neighbors quickly. That is why pgvectorscale can make Postgres realistic for large vector memory, not just toy demos.

Why hypertables matter
Agent events are naturally time-ordered. The dashboard usually asks recent-time questions: last hour, last day, last week. A hypertable partitions the event stream by time, so recent queries touch recent chunks instead of treating the table like one endless pile.

Why continuous aggregates matter
The app should not calculate "daily spend" by scanning raw LLM calls every time someone opens the dashboard. Continuous aggregates keep summary tables warm: cost per agent, latency percentiles, token usage, and per-PR cost. The dashboard reads the summary; Tiger keeps it updated.

Alternatives considered and rejected (ADR-003)
Option	Rejected because
Keep Qdrant + Postgres	Works, but splits memory from review truth and audit history.
Plain Postgres only	Good for truth, weak for large vector memory and time-series rollups.
Add ClickHouse for events	Powerful, but another durable store, connection, schema, and failure mode.
Add Jaeger or Tempo for traces	Useful for infra tracing, but now the product audit trail is outside the product database.
Trade-offs accepted
Trade-off	Rationale
Tiger Cloud is a managed service	Accepted because it replaces multiple durable stores and keeps the system easier to operate.
There are two access styles	SQLAlchemy stays for normal relational work; asyncpg is used for hot paths like event inserts and chunk upserts.
Redis still exists	Accepted because Redis is a queue/cache, not the durable data spine.
The question we ask
When I choose one database, am I simplifying the product, or am I hiding a workload that the database cannot actually handle?

Generalizes to: consolidation is good only when the single store handles each data shape honestly. Name the shapes, name the missing capabilities, and check that the chosen store really has them.

Carry into the architecture
A simpler single spine. Tiger Cloud wins here because it keeps memory, truth, and time in one Postgres-compatible store while still giving each lane the index or table shape it needs.
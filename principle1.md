Why This System Exists
Imagine a team without automated review. Every pull request waits on a senior engineer's attention. That attention is the scarce resource: it is slow (PRs queue for hours or days), inconsistent (the same issue is caught on Monday and missed on Friday), and fatigued (the tenth review of the day is not the first). The cost is not "no review happens" — it is that the most expensive, most valuable human time on the team is spent on work that is, in large part, mechanical pattern recognition.

So an automated reviewer exists to solve exactly one problem: reclaiming senior-reviewer attention by automating the mechanical part of review, so the human is spent only where judgment is genuinely required.

A review agent is not a replacement for human judgment. It is a way to spend human judgment only where it is actually scarce — and to do the rest consistently, tirelessly, and at any hour.

Hold onto the word selective. The system should not flood the PR with every conceivable comment. It should surface high-value findings and route uncertain ones to a human. That selectivity is the seed of the whole architecture.

The question we ask
Why does this system exist at all, and what single cost or loss does it remove?

Generalizes to: before any component, name the one scarcity the system relieves. A search system relieves the cost of not finding; a payments ledger relieves the cost of disputed truth. If you cannot name it, you are designing a feature nobody needs.

Carry into the architecture
A selective, high-value posture. The system optimizes for surfacing findings worth a senior's attention and deferring the rest — not for maximal output. Selectivity, not coverage, is the first principle.

L1
Start From How a Senior Reviews
Before touching LLMs, prompts, or vector databases, ask how a senior engineer actually reviews a pull request. When you are designing something genuinely hard, look for a system that already solved it. Human review has been refined over decades, and the structure we need is sitting inside how a good reviewer thinks.

Watch one closely. They do four things that a naive single-prompt reviewer does not. They bring codebase context — they know this function overrides a base class, that this pattern contradicts a past decision. They reason across separate concerns — a security pass, a correctness pass, a test-coverage pass, a documentation pass, each with a different mindset. They stay skeptical — they do not assume the diff is correct. And they cite evidence — "this is wrong because line 40 can be null here," not "looks off."

Read those four again as an engineer. "Brings codebase context" means the agent needs retrieval. "Reasons across separate concerns" means the agent is not one reasoner but several. "Stays skeptical" and "cites evidence" mean every finding needs a rationale and a confidence. The way a senior reviews is not trivia — it is a decomposition waiting to be built.

Security concern / "could this be exploited?"
Injection risks, secrets in code, auth bypasses, unsafe deserialization. A distinct mindset from correctness.
Quality concern / "is the logic right?"
Correctness bugs, logic errors, code smells, unnecessary complexity. The classic review pass.
Tests concern / "what's untested?"
Missing cases, untested edge conditions, brittle assertions, coverage gaps.
Docs concern / "will the next reader understand?"
Missing docstrings, outdated comments, undocumented public APIs, decisions left unexplained.
The question we ask
Is there a mature system — human or engineered — that already solved a version of this, and what structure can I borrow from it?

Generalizes to: analogies hand you a ready-made decomposition. A recommendation system borrows from word of mouth; a cache borrows from working memory; a review agent borrows from how an expert reads.

Carry into the architecture
Four specialist concerns, born from how a human reviews. The system is not one reasoner but four — security, quality, tests, docs — each a distinct pass with its own mindset. This is the seed of the multi-agent design.

L2
Map the Mess
Now apply the Part 0 template. Map the mess of what happens on a PR today: a developer pushes a commit, opens a PR, and then waits. Eventually a reviewer notices, context-switches into the change, reads the diff, sometimes pulls the branch to run it, leaves comments, and the developer iterates. The waiting and the context-switching are pure cost.

Name the trigger and the output. The trigger is precise: GitHub emits a pull_request webhook when a PR is opened or updated. The output is precise too: a single structured review, posted back to that PR, with findings attached to specific files and lines.

That word structured is doing strategic work. A review is not a blob of prose. It is a list of findings, each with a shape: which concern raised it, how severe, where in the code, why, and how sure the agent is. Deciding that shape now is what lets every later component — the aggregator, the human-review gate, the audit trail — do its job. A first cut of that shape:

agent_type / which concern raised this
security, quality, tests, or docs — so findings can be grouped and attributed.
severity + category / how bad, what kind
CRITICAL down to INFO; a category like "injection" or "missing-test."
file / line / the exact location
So the finding posts inline on the PR, not as a vague summary.
confidence + rationale / how sure, and why
Confidence drives the human-review gate. Rationale is what makes the finding auditable and disputable.
The question we ask
What is the precise trigger, the precise output, and the shape of the object that travels between every component?

Generalizes to: a system is components plus the contract between them. Name the trigger and the output first, then name the object on the arrows. The object usually matters more than the boxes.

Carry into the architecture
An ingress trigger and a structured findings contract. The trigger is a GitHub webhook; the output is a structured review. The unit that flows through the system is a Finding with agent_type, severity, category, file/line, confidence, and rationale.

L3
Industry-Standard Thinking
Most people picture one arrow: diff in, LLM, comments out. That is not how a capable review system works, and the gap between those pictures is the gap between a demo and a product. Walk the rungs of how the industry has climbed toward review automation, and watch why each prior rung falls short.

Four rungs of review automation
Rung	What it does	Why it falls short
Linters	Pattern-match syntax and style rules	No semantics. Cannot reason about intent, logic, or whether a test is meaningful.
Static analysis	Data-flow and type analysis; finds some real bugs	High false-positive rate; no codebase-wide judgment; cannot read documentation intent.
Single-LLM review	One prompt judges the whole diff	One mindset for four concerns; no grounding in the repo; hallucinates with confidence; no audit.
Agentic fan-out	Specialist agents, each grounded, each skeptical, merged by an aggregator	The rung this design stands on — but it demands orchestration, retrieval, and a proof layer.
The single-LLM rung is the seductive one, because it works in a demo. It collapses four concerns into one prompt, which means it does each of them shallowly, and it has no way to be grounded, audited, or trusted. The fan-out rung — running the four concerns from L1 as parallel specialists — is where production lives.

The question we ask
What does the mature version of this decompose into, beyond the happy path the demo shows?

Generalizes to: every interesting system has a hidden back half. List the rungs the industry has already climbed, and stand on the highest one whose cost you can actually pay.

Carry into the architecture
Parallel specialists, not a single prompt. The four concerns from L1 run as four agents in parallel, each doing one job deeply. This is the agentic fan-out, and it implies an orchestrator and an aggregator we will name later.

L4
The Grounding Problem
Here is where most single-LLM reviewers fail. An LLM handed a diff in isolation knows what changed but not what it changed within. It cannot know that this function overrides a base method, that this pattern was deliberately rejected in a past decision, or that the test convention in this repo is table-driven. So it does what models do under uncertainty: it guesses, confidently. That is hallucination in a critical path — the first failure mode from the 0.2 catalog.

A senior reviewer does not have this problem because they know the repo. The design question is: what gives the agent that knowledge? It cannot be the full repository in the prompt — that exhausts the context window on any non-trivial codebase, and most of it is irrelevant to a given diff. The answer is retrieval: for each diff, fetch only the most relevant slices of the codebase and put those in the prompt.

An ungrounded reviewer is a confident stranger. A grounded one is a colleague who has read the code. Retrieval is what turns the stranger into the colleague.

The question we ask
What does this reasoner need to know that is not in front of it, and how do we put exactly that — and only that — in front of it?

Generalizes to: any LLM judging an artifact in isolation hallucinates. Retrieval-augmented generation is the general fix — fetch the relevant context, do not dump everything, do not assume the model already knows.

Carry into the architecture
A retrieval layer (RAG). Each specialist queries for the codebase context relevant to the diff and reasons over diff-plus-context, never the diff alone. Grounding is not optional; it is what separates this from a single-LLM reviewer.

L5
What Kinds of Memory Does Review Need?
L4 said "retrieve context." But context is not one kind of thing. A senior reviewer draws on several kinds of memory, and — exactly as in cognitive science — each kind has a different shape and a different access pattern. Naming them now is what determines the data design later.

Kind of memory	What it holds for review	The data shape it wants
Semantic	The codebase itself — functions, classes, modules, ADRs, conventions, as meaning	Vector embeddings + similarity search
Episodic	Past reviews — what was flagged before, what was disputed, what was merged	Time-stamped relational rows
Procedural	How this team likes things done — conventions, ADRs, severity policy	Small, high-priority, almost always loaded
Read those three again as an engineer. Semantic memory wants similarity search over embeddings — a vector store. Episodic memory wants time-ordered, queryable rows — relational history. Procedural memory is small and structured — facts and rules. The taxonomy is not philosophy; it is a schema waiting to be written, and it tells us we do not have one data need but three distinct shapes.

The question we ask
What distinct kinds of state does this system hold, and does each kind want a different shape rather than one undifferentiated bucket?

Generalizes to: before choosing storage, enumerate the kinds of state by access pattern. Hot vs cold, similarity vs exact, append-only vs mutable. The kinds drive the shapes; the shapes drive the stores.

Carry into the architecture
Three data shapes. Semantic memory of the repo wants a vector / ANN shape. Past reviews and findings want a relational shape. Conventions and decisions want a small structured shape. Hold these three — Part II decides how many actual databases they require.

L6
Trust and Proof
Suppose the agent posts a finding: "this endpoint is vulnerable to SQL injection, confidence 0.6." A developer disputes it. Now what? If there is no record of why the finding was raised — which context was retrieved, which prompt version ran, what the model returned, what it cost — the system cannot defend itself, cannot be debugged, and cannot improve. A review you cannot audit is worthless, and a system whose cost can run away unobserved is dangerous.

So trust requires a third thing beyond reasoning and grounding: proof. Every action the agent takes — every span of work, every LLM call, every tool call, every decision — must be recorded as an event, in time order, durably. That single stream of events is what powers three things at once: a trace viewer (reconstruct any review end-to-end), an audit trail (defend or dispute any finding), and a cost ledger (attribute every token to an agent and a model).

If the system cannot show its work, it has not done the work. The proof layer is not instrumentation bolted on at the end — it is born here, as a first principle, the moment we ask the system to be trusted.

The question we ask
When this system produces an output, can it prove how it got there — and can it tell us what that cost?

Generalizes to: any system making consequential automated decisions needs an immutable, time-ordered record of its actions. Payments, fraud scoring, medical triage. Design the audit stream with the decision, not after the incident.

Carry into the architecture
An events spine. Every action becomes a time-ordered event row — span, LLM call, tool call, decision — carrying cost, latency, confidence, and outcome. One stream feeds the trace viewer, the audit trail, and the cost ledger. This is a fourth data need, time-series in shape.

L7
When Not to Trust It
L0 said the system should be selective. L6 gave it the confidence field. Now apply the 0.3 HITL spectrum to this system. The agent is not always right, and it knows roughly when it is unsure — that is what the confidence on each finding measures. The design decision is what to do with that knowledge.

The answer is a confidence-weighted gate. High-confidence reviews, with no critical findings, post automatically — the agent has earned that autonomy. Low-confidence reviews route to a human approval queue. Any finding marked CRITICAL escalates regardless of confidence, because the consequence of a missed critical issue is too high to automate (consequence of error, from 0.3). This places the system at the "human handles exceptions" level of the spectrum, with an escalation path to "human decides."

The confidence-weighted gate
Condition	Action	Which 0.3 factor
High confidence, no CRITICAL	Post automatically	Maturity earns autonomy
Confidence below threshold	Route to human approval queue	Uncertainty, defer judgment
Any CRITICAL finding	Escalate, page a human	Consequence of error too high
Developer disputes a posted finding	Route to dispute, record feedback	Reversibility, learning loop
The question we ask
Where on the human-involvement spectrum does this system belong, and what signal moves a given case up or down it?

Generalizes to: autonomy is not binary. Let the system earn it case by case, gated on a confidence signal and the stakes. Content moderation, lending, triage — all use the same confidence-weighted routing.

Carry into the architecture
A confidence-weighted HITL gate. The aggregator computes an overall confidence; below threshold or on any CRITICAL finding, the review enters a human approval queue instead of posting. This implies queue and feedback tables in the relational shape from L5.

L8
Failure Modes, Applied
Run the 0.2 catalog directly against code review. Each general failure mode lands on a specific defense, and — notice — each defense is a component we have already carried or are about to add.

General failure (0.2)	In code review it looks like	Defense
Hallucination in critical path	A finding about code the agent never actually saw	Grounding (L4) + rationale + confidence (L2)
Tool / API timeout	The LLM provider or GitHub API stalls	Retries with backoff, circuit breakers
Orchestration deadlock	The aggregator waits forever on a hung agent	Timeouts on every node, dead-letter handling
The "almost-right" problem	A finding 90% right but subtly misattributed	Dedup across agents, confidence threshold, HITL (L7)
Human bottleneck	The approval queue grows faster than reviewers clear it	Escalation-rate monitoring on the events spine (L6)
Feedback-loop poisoning	The agent "learns" a wrong preference from a few disputes	Minimum evidence threshold before acting on feedback
Idempotency gap	A retried webhook posts the same review twice	Idempotency key at ingress, dedup before posting
Failure analysis did not invent new parts. It justified the parts we chose and added a thin layer of reliability mechanics on top.

The question we ask
For each component, what happens when it fails, and does the system degrade to slower-but-correct rather than fast-but-wrong?

Generalizes to: run a pre-mortem before code. Walk each box and break it on purpose. The fallbacks you design now are the incidents you avoid later.

Carry into the architecture
A reliability layer. Retries, circuit breakers, timeouts, idempotency at ingress, and dedup at the aggregator — each mapped to a specific failure mode, not added speculatively.

L9
The Mental Model
Before we draw a single box, the assembled reasoning in prose. The pieces we carried, in the order they were earned, already describe the whole system.

A pull request triggers the work (L2). It is enqueued, not handled inline, because the trigger must be acknowledged fast and the work decoupled from the ingress (L2, L8). An orchestrator fans the work out to four specialists — security, quality, tests, docs (L1, L3) — running in parallel. Each specialist is grounded by retrieval over the codebase (L4), because an ungrounded reviewer hallucinates. The codebase, the past reviews, and the conventions are three kinds of memory, three data shapes (L5). Each specialist returns structured findings with confidence and rationale (L2). An aggregator merges and deduplicates them, computes an overall confidence, and applies the HITL gate (L7): post automatically when confident, route to humans when not. Every action along the way is written to an events spine (L6) so the whole thing can be traced, audited, and priced. And a reliability layer (L8) keeps each step degrading to slower-but-correct.

Now ask: how many databases does this need? We have memory, truth, and time. The naive answer is three durable stores. Part II interrogates that answer — and arrives at one.

Running ledger / what Part I has built

The reasoning model, assembled from first principles
L0	A selective, high-value posture: reclaim scarce senior-reviewer attention.
L1	The four specialist concerns: security, quality, tests, docs — born from how a human reviews.
L2	An ingress trigger and the Finding contract with confidence and rationale.
L3	Parallel specialists, not a single prompt — the agentic fan-out.
L4	A retrieval layer: ground every specialist in the codebase.
L5	Three data shapes: vector (semantic), relational (episodic), structured (procedural).
L6	An events spine: every action a time-ordered row, feeding trace + audit + cost.
L7	A confidence-weighted HITL gate routing low-confidence reviews to humans.
L8	A reliability layer: retries, circuit breakers, idempotency, dedup.
L9	The assembled mental model — and the open question: how many databases?
Part II answers the database question. Part III draws the boxes. Part IV lists everything we will build.
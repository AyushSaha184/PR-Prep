0.1
The Universal Design Template
After enough systems, intuition becomes a repeatable process. Five moves turn any workflow, in any domain, into an agentic design. We will apply all five to PR review in Part I.

Move 1. Map the mess
Document what actually happens today, not the process document nobody follows. Watch the person doing the work. Record the trigger that starts it, every step in the middle, the deliverable at the end, where the human is actually thinking versus mechanically shuffling information, and where it breaks.

Move 2. Name the trigger and the output
Every automatable workflow has a precise trigger and a precise output. "A claim email arrives at claims@company.com," not "claims come in." "A structured review is posted to the PR," not "code gets reviewed." If you cannot state both in one sentence each, you have not looked closely enough.

Move 3. Assign components
Take each step and assign it to a component type. Detecting that work is needed is a trigger. Fetching data is a tool/API. Reading unstructured input or writing language is an LLM. A score or classification that must be identical every time is deterministic ML. A judgment with legal, financial, or safety stakes is a human checkpoint.

Most common mistake
Assigning an LLM to a step that should be deterministic. If the output must be the same every time given the same input — a severity score, a routing class — it must be deterministic. If the output is language and some variation is acceptable, it can be an LLM.

Move 4. Choose autonomy
Decide how much the system does on its own versus how much it defers to a human. This is not a default — it is a design choice driven by the consequence of error. Section 0.3 gives the full spectrum.

Move 5. Design for failure
Walk each component and break it on purpose. What happens when the LLM hallucinates, the API times out, two parallel agents conflict? Every component should fail gracefully.

The system should degrade to slower but correct, never fast but wrong. The worst failure mode is a wrong answer delivered with confidence.

0.2
The Failure Modes Catalog
Every agentic system fails. The only question is whether it fails safely. Seven recurring modes, and how to design against each. We will run this catalog against code review in L8.

Seven general agentic failure modes
Mode	What happens	Design against it with
Hallucination in a critical path	The model states something plausible but false in a place that matters	Citation requirement, a fact-check layer, human review for high stakes, prompts that permit "I don't know"
Model drift	Accurate at deployment, degrades as the world changes	Monitoring dashboard, alert thresholds, periodic retraining, rules fallback
Tool / API timeout	An external system stalls and the pipeline hangs	Timeout-and-retry, graceful degradation on partial data, circuit breaker on a dead service
Feedback-loop poisoning	Bad feedback is stored and degrades future behavior	Minimum evidence threshold, audit for protected proxies, decay on old feedback, human reset
Orchestration deadlock	Two parallel steps wait on each other; a merge never receives an input	Timeouts on every step, health checks, idempotent operations, dead-letter queue
Human bottleneck	Auto-handling works, but the escalation queue grows faster than humans clear it	Escalation-rate monitoring, queue prioritization, threshold tuning under load, honest capacity planning
The "almost-right" problem	Output 90% correct, 10% subtly wrong, while reviewers drift into complacency	Rotate reviewers, flag low-confidence outputs, random audits, inject known-wrong inputs to test vigilance
0.3
The Human-in-the-Loop Spectrum
Not every system needs the same level of human involvement. The right level is a design choice, not a default. Five levels, and the three factors that pick one.

Level	Description	Where it fits
Full automation	System handles everything; human samples periodically	Routine, low-stakes, reversible work
Human reviews output	System produces, human verifies before it goes out	Drafts with reputational stakes
Human handles exceptions	System auto-handles easy cases, human sees the hard ones	Anomalies, low-confidence cases, escalations
Human decides, system prepares	System gathers all context, human makes the call	High-consequence, irreversible decisions
Full human with AI assist	Human does the work, system helps at specific steps	Early-stage, low-trust, or creative work
Three factors choose the level. Consequence of error: a wrong style comment is annoying; a missed SQL injection is dangerous. Reversibility: an auto-posted review can be disputed and removed; a merged migration cannot be un-run easily. System maturity: new systems need more oversight; proven ones earn less.

Start with more human involvement than you think you need. Reduce it as the system proves itself. It is far easier to remove a checkpoint than to recover from removing it too early.
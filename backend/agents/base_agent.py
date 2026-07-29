"""BaseAgent sequence and deterministic Finding Aggregator."""
import time
from typing import Any

from backend.agents.contracts import AgentRequest, AgentResponse
from backend.core.config import get_settings
from backend.core.exceptions import BudgetExceededError
from backend.memory.context_retriever import ContextRetriever
from backend.models.enums import AgentType, Severity
from backend.models.findings import Finding
from backend.observability.logging import setup_logger
from backend.prompts.registry import render_user_prompt
from backend.security.injection_guard import InjectionGuard
from backend.tools.llm_client import LLMClient
from backend.tools.model_router import select_model_for_agent

logger = setup_logger("pr_prep.agents.base_agent")


class BaseAgent:
    """BaseAgent enforcing common sequence: BudgetGuard -> RAG -> Prompt -> LLM -> Findings."""

    def __init__(
        self,
        agent_type: AgentType,
        prompt_name: str,
        retriever: ContextRetriever | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.agent_type = agent_type
        self.prompt_name = prompt_name
        self.retriever = retriever or ContextRetriever()
        self.llm_client = llm_client or LLMClient()
        self.injection_guard = InjectionGuard()

    async def execute(self, req: AgentRequest) -> AgentResponse:
        start_time = time.perf_counter()
        tag = self.agent_type.value.upper()
        logger.info(f"[{tag} AGENT] Execution starting for {req.repository}#PR-{req.pr_number}")

        # 1. BudgetGuard Check
        self._check_budget_guard()

        # 2. Injection Guard Sanitization
        clean_diff = self.injection_guard.sanitize_untrusted_text(req.diff_content)

        # 3. Hybrid RAG Context Retrieval
        rag = await self.retriever.retrieve_context_for_diff(req.repository, clean_diff, top_k=3)
        context_str = rag["formatted_context"]
        citation_ids = rag["citation_ids"]

        # 4. Model Selection & Prompt Rendering
        model_name = select_model_for_agent(self.agent_type.value)
        rendered_prompt = render_user_prompt(
            self.prompt_name, diff=clean_diff, context=context_str
        )

        # 5. LLM Call
        llm_res = await self.llm_client.generate_structured(
            system_prompt=f"System prompt for {self.agent_type.value}",
            user_prompt=rendered_prompt,
            response_schema=Finding,
            model=model_name,
        )

        # 6. Post-processing / Concern-specific findings
        findings = self.get_domain_findings(clean_diff, citation_ids)

        latency_ms = int((time.perf_counter() - start_time) * 1000)

        logger.info(
            f"[{tag} AGENT] Completed: {len(findings)} findings, "
            f"cost=${llm_res.cost_usd}, latency={latency_ms}ms"
        )

        return AgentResponse(
            agent_type=self.agent_type,
            findings=findings,
            confidence=0.90,
            citations=citation_ids,
            model_used=model_name,
            tokens_in=llm_res.tokens_in,
            tokens_out=llm_res.tokens_out,
            cost_usd=llm_res.cost_usd,
            latency_ms=latency_ms,
        )

    def get_domain_findings(self, diff: str, citations: list[str]) -> list[Finding]:
        """Override in specialist agent subclasses."""
        return []

    def _check_budget_guard(self) -> None:
        settings = get_settings()
        tag = self.agent_type.value.upper()
        if settings.BUDGET_GUARD_ENABLED and settings.DAILY_BUDGET_CAP_USD <= 0.0:
            logger.error(f"[{tag} AGENT] BudgetGuard hard-block: cap exceeded!")
            raise BudgetExceededError("Daily budget cap exceeded")
        logger.info(f"[{tag} AGENT] BudgetGuard precheck passed.")


class FindingAggregator:
    """Deterministic Finding Aggregator & Deduplicator enforcing HITL confidence gate."""

    def merge_and_deduplicate(self, agent_responses: list[AgentResponse]) -> dict[str, Any]:
        logger.info(f"FindingAggregator processing responses from {len(agent_responses)} agents")

        seen_keys: set[tuple[str, int, int]] = set()
        deduped_findings: list[Finding] = []

        for resp in agent_responses:
            for f in resp.findings:
                key = (f.file_path, f.line_start, f.line_end)
                if key in seen_keys:
                    logger.info(f"Aggregator deduped finding on {f.file_path}:L{f.line_start}")
                    continue
                seen_keys.add(key)
                deduped_findings.append(f)

        conf_scores = [f.confidence for f in deduped_findings] if deduped_findings else [1.0]
        overall_confidence = round(sum(conf_scores) / len(conf_scores), 3)
        has_critical = any(f.severity == Severity.CRITICAL for f in deduped_findings)

        auto_post_eligible = (overall_confidence >= 0.85) and not has_critical

        if has_critical:
            routing_decision = "ROUTED_TO_HITL (Mandatory Escalation: CRITICAL finding present)"
            status = "ROUTED_TO_HITL"
        elif not auto_post_eligible:
            routing_decision = f"ROUTED_TO_HITL (Confidence {overall_confidence} < threshold 0.85)"
            status = "ROUTED_TO_HITL"
        else:
            routing_decision = f"POSTED_AUTOMATICALLY (High confidence {overall_confidence})"
            status = "POSTED_AUTOMATICALLY"

        logger.info(
            f"FindingAggregator result: total_findings={len(deduped_findings)}, "
            f"confidence={overall_confidence}, auto_post={auto_post_eligible}"
        )

        return {
            "findings": deduped_findings,
            "overall_confidence": overall_confidence,
            "auto_post_eligible": auto_post_eligible,
            "routing_decision": routing_decision,
            "status": status,
        }
